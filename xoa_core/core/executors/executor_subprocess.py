import asyncio
import contextlib
from enum import Enum
from functools import partialmethod
from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from pydantic import BaseModel
    from xoa_core.types import PluginAbstract, EMsgType, Progress
    from .executor import PPlugin, PRPCPipe
    from xoa_core.core.plugin_abstract import (
        TransmitFunc,
    )

from xoa_core.types import Progress, EMsgType
from .dataset import PIPE_CLOSE, POLL_MESSAGE_INTERVAL, MessageFromSubProcess, ExecuteEvent
from .executor_state_conditions import StateConditions
from .exceptions import StopPlugin
from loguru import logger


class RelayXOAOut:
    def __init__(self, transmit: "TransmitFunc", suite_name: str) -> None: # noqa: E704
        self.transmit = transmit

    def send_statistics(self, data: Union[Dict, "BaseModel"]) -> None:
        """Method used for push statistics data into the messages pipe for future distribution"""
        self.transmit(data, msg_type=EMsgType.STATISTICS)

    def send_progress(self, current: int, total: int = 100, loop: int = 0) -> None:
        self.transmit(Progress(current=current, total=total, loop=loop), msg_type=EMsgType.PROGRESS)

    def send_warning(self, warning: Exception) -> None:
        self.transmit(warning, msg_type=EMsgType.WARNING)

    def send_error(self, error: Exception) -> None:
        self.transmit(error, msg_type=EMsgType.ERROR)


class SubProcessTestSuite:
    __test_suite: "PluginAbstract"
    __task: "asyncio.Task"
    __loop: "asyncio.AbstractEventLoop"
    xoa_out_pipe: "PRPCPipe"
    rpc_pipe: "PRPCPipe"

    def __init__(self, suite_name: str, xoa_out_pipe, rpc_pipe) -> None:
        self.suite_name = suite_name
        self.state_conditions = StateConditions()
        self.xoa_out_pipe = xoa_out_pipe
        self.rpc_pipe = rpc_pipe
        self.rpc_function_table = {
            ExecuteEvent.PAUSE: self.state_conditions.pause,
            ExecuteEvent.STOP: self.state_conditions.stop,
            ExecuteEvent.CONTINUE: self.state_conditions.resume,
            ExecuteEvent.CANCEL: self.__cancel_test_suite,
            ExecuteEvent.ON_PAUSE: self.__on_pause,
            ExecuteEvent.ON_CONTINUE: self.__on_continue,
            ExecuteEvent.ON_STOP: self.__on_stop,
        }

    def __cancel_test_suite(self) -> None:
        self.__task.cancel()

    def assign_plugin(self, plugin: "PPlugin") -> None:
        self.__test_suite = plugin.create_test_suite(
            self.state_conditions.get_facade(),
            xoa_out=RelayXOAOut(self.__send_xoa_out_message, self.suite_name),
        )

    def __send_xoa_out_message(self, msg: Any, *, msg_type: "Enum", **meta) -> None:
        self.xoa_out_pipe.send(MessageFromSubProcess(msg=msg, msg_type=msg_type))

    def __test_suite_ends(self, task: "asyncio.Task"):
        # if err := task.exception():
        #     self.__send_xoa_out_message(err, msg_type=EMsgType.ERROR)
        self.xoa_out_pipe.send(PIPE_CLOSE)

    async def __rpc_listener(self) -> None:
        while True:
            if self.rpc_pipe.poll():
                event_name: str = self.rpc_pipe.recv()
                func = self.rpc_function_table[ExecuteEvent[event_name]]
                func()
            await asyncio.sleep(POLL_MESSAGE_INTERVAL)

    def start(self) -> None:
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        self.__loop.create_task(self.__rpc_listener())
        self.__task = self.__loop.create_task(self.__test_suite.start())
        self.__task.add_done_callback(self.__test_suite_ends)
        with contextlib.suppress(asyncio.CancelledError, StopPlugin):
            self.__loop.run_until_complete(self.__task)

    def invoke_test_suite_callback(self, event: str) -> None:
        return
        event_func = getattr(self.__test_suite, event)
        self.__loop.create_task(event_func())

    __on_pause = partialmethod(invoke_test_suite_callback, 'on_pause')
    __on_continue = partialmethod(invoke_test_suite_callback, 'on_continue')
    __on_stop = partialmethod(invoke_test_suite_callback, 'on_stop')