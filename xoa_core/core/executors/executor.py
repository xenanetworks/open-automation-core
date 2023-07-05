import asyncio
import contextlib
from enum import Enum
import queue
import time
import uuid
import typing
from multiprocessing import Process, Pipe

from xoa_core.core.generic_types import (
    TObserver,
    TMesagesPipe,
)
from xoa_core.types import PluginAbstract, EMsgType
from xoa_core.core.executors.dataset import PIPE_CLOSE, POLL_MESSAGE_INTERNAL, EventFromParent, ExecuteEvent, MessageFromSubProcess

if typing.TYPE_CHECKING:
    from pydantic import BaseModel
    from xoa_core.types import PluginAbstract
    from xoa_core.core.plugin_abstract import (
        PStateConditionsFacade,
        PPipeFacade,
        TransmitFunc,
    )


from .executor_info import ExecutorInfo
from . import exceptions
from ._events import Event
from .executor_state import ExecutorState
from .executor_subprocess import SubProcessTestSuite

from loguru import logger



class PPlugin(typing.Protocol):
    def create_test_suite(self, state_conditions: "PStateConditionsFacade", xoa_out: "PPipeFacade") -> "PluginAbstract": ...  # noqa: E704


class SuiteExecutor:
    # __slots__ = ("suite_name", "state", "__id", "__observer", "msg_pipe", "__test_suite", "__task", "state_conditions", "plugin", "event_pipe", "message_pipe")

    def __init__(self, suite_name: str) -> None:
        self.__id = str(uuid.uuid4())
        self.suite_name = suite_name
        self.state = ExecutorState()
        self.test_suite_state_pipe_read, self.test_suite_state_pipe_write = Pipe(False)
        self.xoa_out_pipe_read, self.xoa_out_pipe_write = Pipe(duplex=False)
        self.__test_suite = SubProcessTestSuite(
            suite_name=self.suite_name,
            xoa_out_pipe=self.xoa_out_pipe_write,
            event_state_pipe=self.test_suite_state_pipe_read
        )

    @property
    def id(self) -> str:
        return self.__id

    def __on_execution_terminated(self, task: "asyncio.Task") -> None:
        logger.debug('terminated')
        if not self.state.is_stoped:
            self.state.set_stop()
        self.__observer.emit(Event.STOPPED, self.id)
        asyncio.create_task(self.msg_pipe.disable())  # In rare case raise error but it's not break anything.
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            e = task.exception()
            if e is None:
                return None
            self.__observer.emit(Event.ERROR, task.get_name(), e)
            raise e

    def get_info(self) -> ExecutorInfo:
        return ExecutorInfo(
            id=self.__id,
            suite_name=self.suite_name,
            state=self.state.current_state,
        )

    def assign_pipe(self, pipe: "TMesagesPipe") -> None:
        self.msg_pipe = pipe
        self.state.assign_senders(pipe.get_state_facade())

    def assign_plugin(self, plugin: PPlugin) -> None:
        self.plugin = plugin
        self.__test_suite.setup(self.plugin)

    async def read_child_message(self):
        xoa_out = self.msg_pipe.get_facade(self.suite_name)
        child_message: typing.Union["MessageFromSubProcess", str]
        for child_message in iter(lambda: self.xoa_out_pipe_read.recv(), 'STOP'):
            if child_message == PIPE_CLOSE:
                return

            assert isinstance(child_message, MessageFromSubProcess)
            if child_message.msg_type == EMsgType.STATISTICS:
                xoa_out.send_statistics(child_message)
            elif child_message.msg_type == EMsgType.PROGRESS:
                xoa_out.send_progress(child_message.msg.current)
            elif child_message.msg_type == EMsgType.WARNING:
                xoa_out.send_warning(child_message.msg)
            elif child_message.msg_type == EMsgType.ERROR:
                xoa_out.send_error(child_message.msg)

            await asyncio.sleep(POLL_MESSAGE_INTERNAL)
        # while True:
        #     if self.xoa_out_pipe_read.poll():
        #         msg = self.xoa_out_pipe_read.recv()
        #     await asyncio.sleep(POLL_MESSAGE_INTERNAL)

    def run(self, observer: TObserver) -> None:
        self.__observer = observer
        self.state.set_run()
        msg = asyncio.create_task(self.read_child_message())
        msg.add_done_callback(self.__on_execution_terminated)
        p = Process(target=self.__test_suite.start, daemon=True)
        p.start()

    def __send_event_to_child(self, event_type: ExecuteEvent, is_event_set: bool) -> None:
        self.test_suite_state_pipe_write.send(EventFromParent(
            event_type=event_type,
            is_event_set=is_event_set,
        ))

    def toggle_pause(self) -> None:
        """User interface toggle pause."""
        if self.state.is_running:
            self.state.set_pause()
            self.__send_event_to_child(ExecuteEvent.PAUSE, True)
            # await self.__test_suite.on_pause()
        elif self.state.is_paused:
            self.state.set_run()
            self.__send_event_to_child(ExecuteEvent.PAUSE, False)
            # await self.__test_suite.on_continue()

    async def stop(self) -> None:
        """User interface stop the test suite."""
        self.state.set_stop()
        self.__test_suite.on_stop()
        self.__send_event_to_child(ExecuteEvent.STOP, True)
        self.__send_event_to_child(ExecuteEvent.CANCEL, True)
        # with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
        #     await self.__task
