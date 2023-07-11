import asyncio
import contextlib
import uuid
import typing
from multiprocessing import Process, Pipe

if typing.TYPE_CHECKING:
    from pydantic import BaseModel
    from xoa_core.types import PluginAbstract
    from xoa_core.core.plugin_abstract import (
        PStateConditionsFacade,
        PPipeFacade,
    )

from xoa_core.core.generic_types import (
    TObserver,
    TMesagesPipe,
)
from xoa_core.types import PluginAbstract, EMsgType
from .dataset import PIPE_CLOSE, ExecuteEvent, MessageFromSubProcess
from .executor_info import ExecutorInfo
from . import exceptions
from ._events import Event
from .executor_state import ExecutorState
from .executor_subprocess import SubProcessTestSuite

from loguru import logger


class PPlugin(typing.Protocol):
    def create_test_suite(self, state_conditions: "PStateConditionsFacade", xoa_out: "PPipeFacade") -> "PluginAbstract": ...  # noqa: E704


class PRPCPipe(typing.Protocol):
    def send(self, obj: typing.Any) -> None: ...
    def poll(self) -> bool: ...
    def recv(self) -> typing.Any: ...


def _get_transmit_func(msg_type: EMsgType, xoa_out: "PPipeFacade") -> typing.Callable[[typing.Any], typing.Any]:
    func = {
        EMsgType.STATISTICS: xoa_out.send_statistics,
        EMsgType.PROGRESS: xoa_out.send_progress,
        EMsgType.WARNING: xoa_out.send_warning,
        EMsgType.ERROR: xoa_out.send_error,
    }.get(msg_type)
    assert func
    return func


class SuiteExecutor:
    __slots__ = ("suite_name", "state", "__id", "__observer", "__msg_pipe", "__test_suite", "__rpc_pipe_write", "__xoa_out_pipe_read")
    __rpc_pipe_write: PRPCPipe
    __xoa_out_pipe_read: PRPCPipe

    def __init__(self, suite_name: str) -> None:
        self.__id = str(uuid.uuid4())
        self.suite_name = suite_name
        self.state = ExecutorState()
        __rpc_pipe_read, self.__rpc_pipe_write = Pipe(False)
        self.__xoa_out_pipe_read, __xoa_out_pipe_write = Pipe(duplex=False)
        self.__test_suite = SubProcessTestSuite(
            suite_name=self.suite_name,
            xoa_out_pipe=__xoa_out_pipe_write,
            rpc_pipe=__rpc_pipe_read
        )

    @property
    def id(self) -> str:
        return self.__id

    def __on_execution_terminated(self, task: "asyncio.Task") -> None:
        if not self.state.is_stoped:
            self.state.set_stop()
        err = None
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            err = task.exception()
            if err is not None:
                self.__msg_pipe.transmit_err(err)
                self.__observer.emit(Event.ERROR, task.get_name(), err)  # only notify of the Execution manager.
        self.__observer.emit(Event.STOPPED, self.id)
        asyncio.create_task(self.__msg_pipe.disable())  # In rare case raise error but it's not break anything.
        if err:
            raise exceptions.ExecutionError(task.get_name()) from err

    def get_info(self) -> ExecutorInfo:
        return ExecutorInfo(
            id=self.__id,
            suite_name=self.suite_name,
            state=self.state.current_state,
        )

    def assign_pipe(self, pipe: "TMesagesPipe") -> None:
        self.__msg_pipe = pipe
        self.state.assign_senders(pipe.get_state_facade())

    def assign_plugin(self, plugin: PPlugin) -> None:
        self.__test_suite.assign_plugin(plugin)

    async def __relay_child_xoa_message(self) -> None:
        xoa_out = self.__msg_pipe.get_facade(self.suite_name)
        child_message: typing.Union["MessageFromSubProcess", str]
        while True:
            child_message = await asyncio.to_thread(self.__xoa_out_pipe_read.recv)
            if child_message == PIPE_CLOSE:
                return

            assert isinstance(child_message, MessageFromSubProcess)
            transmit = _get_transmit_func(child_message.msg_type, xoa_out)
            if child_message.msg_type == EMsgType.PROGRESS:
                transmit(**child_message.msg.dict())# type: ignore
            elif child_message.msg_type == EMsgType.ERROR:
                raise child_message.msg
            else:
                transmit(child_message.msg)


    def run(self, observer: TObserver) -> None:
        self.__observer = observer
        self.state.set_run()
        msg = asyncio.create_task(self.__relay_child_xoa_message())
        msg.add_done_callback(self.__on_execution_terminated)
        p = Process(target=self.__test_suite.start, daemon=True)
        p.start()

    def __send_rpc(self, event_type: ExecuteEvent) -> None:
        self.__rpc_pipe_write.send(event_type.value)

    def toggle_pause(self) -> None:
        """User interface toggle pause."""
        if self.state.is_running:
            self.state.set_pause()
            self.__send_rpc(ExecuteEvent.PAUSE)
            self.__send_rpc(ExecuteEvent.ON_PAUSE)
        elif self.state.is_paused:
            self.state.set_run()
            self.__send_rpc(ExecuteEvent.CONTINUE)
            self.__send_rpc(ExecuteEvent.ON_CONTINUE)

    async def stop(self) -> None:
        """User interface stop the test suite."""
        self.state.set_stop()
        self.__send_rpc(ExecuteEvent.STOP)
        self.__send_rpc(ExecuteEvent.ON_STOP)
        self.__send_rpc(ExecuteEvent.CANCEL)
        # with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
        #     await self.__task
