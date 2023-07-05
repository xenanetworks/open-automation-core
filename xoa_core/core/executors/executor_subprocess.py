import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Union

from loguru import logger

if TYPE_CHECKING:
    from xoa_core.types import PluginAbstract, EMsgType, Progress
    from pydantic import BaseModel
    from .executor import PPlugin
    from xoa_core.core.plugin_abstract import (
        TransmitFunc,
    )
    from .dataset import EventFromParent

from xoa_core.core.executors.dataset import PIPE_CLOSE, POLL_MESSAGE_INTERNAL, MessageFromSubProcess
from xoa_core.types import Progress, EMsgType
from .executor_state_conditions import StateConditions


class RelayXOAOut:
    def __init__(self, transmit: "TransmitFunc", suite_name: str) -> None: # noqa: E704
        self.transmit = transmit

    def send_statistics(self, data: Union[Dict, "BaseModel"]) -> None:
        """Method used for push statistics data into the messages pipe for future distribution"""
        self.transmit(data, msg_type=EMsgType.STATISTICS)

    def send_progress(self, current: int, total: int = 100) -> None:
        self.transmit(Progress(current=current, total=total), msg_type=EMsgType.PROGRESS)

    def send_warning(self, warning: Exception) -> None:
        logger.debug(warning)

    def send_error(self, error: Exception) -> None:
        logger.debug(error)


class SubProcessTestSuite:
    __test_suite: "PluginAbstract"
    __task: "asyncio.Task"

    def __init__(self, suite_name: str, xoa_out_pipe, event_state_pipe) -> None:
        self.suite_name = suite_name
        self.xoa_out_pipe = xoa_out_pipe
        self.event_state_pipe = event_state_pipe
        self.state_conditions = StateConditions()

    def setup(self, plugin: "PPlugin") -> None:
        self.__test_suite = plugin.create_test_suite(
            self.state_conditions.get_facade(),
            xoa_out=RelayXOAOut(self.__send_xoa_out_message, self.suite_name),
        )

    def __send_xoa_out_message(self, msg: Any, *, msg_type: "Enum", **meta) -> None:
        self.xoa_out_pipe.send(MessageFromSubProcess(msg=msg, msg_type=msg_type))

    def __test_suite_ends(self, task: Any):
        self.xoa_out_pipe.send(PIPE_CLOSE)

    async def __sync_event_state(self) -> None:
        while True:
            if self.event_state_pipe.poll():
                msg: EventFromParent = self.event_state_pipe.recv()
                if msg.event_type.is_pause:
                    self.state_conditions.toggle_pause(msg.is_event_set)
                elif msg.event_type.is_stop:
                    self.state_conditions.stop()
                elif msg.event_type.is_cancel:
                    self.__task.cancel()
            await asyncio.sleep(POLL_MESSAGE_INTERNAL)

    def start(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sync_state = loop.create_task(self.__sync_event_state())
        self.__task = loop.create_task(self.__test_suite.start())
        self.__task.add_done_callback(self.__test_suite_ends)
        loop.run_until_complete(self.__task)

    def on_pause(self) -> None:
        ...

    def on_continue(self) -> None:
        ...

    def on_stop(self) -> None:
        ...