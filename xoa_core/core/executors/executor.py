import asyncio
import contextlib
import uuid
import typing
from xoa_core.core.generic_types import (
    TObserver,
    TMesagesPipe,
    PipeFacade
)
if typing.TYPE_CHECKING:
    from xoa_core.types import PluginAbstract

from . import exceptions
from ._events import Event
from .executor_state import ExecutorState
from .executor_state_conditions import StateConditions, StateConditionsFacade


class PPlugin(typing.Protocol):
    def create_test_suite(self, state_conditions: "StateConditionsFacade", xoa_out: "PipeFacade") -> "PluginAbstract": ...  # noqa: E704


# TODO: Need to improve attributes creation in this class
class SuiteExecutor:
    __slots__ = ("suite_name", "state", "__id", "__observer", "__msg_pipe", "__test_suite", "__task", "state_conditions")

    def __init__(self, suite_name: str) -> None:
        self.__id = str(uuid.uuid4())
        self.suite_name = suite_name
        self.state = ExecutorState()
        self.state_conditions = StateConditions()

    @property
    def id(self) -> str:
        return self.__id

    def __on_execution_terminated(self, task: "asyncio.Task") -> None:
        if not self.state.is_stoped:
            self.state.set_stop()
        self.__observer.emit(Event.STOPPED, self.id)
        asyncio.create_task(self.__msg_pipe.disable())  # In rare case raise error but it's not break anything.
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            e = task.exception()
            if e is None:
                return None
            self.__observer.emit(Event.ERROR, task.get_name(), e)
            raise e

    def assign_pipe(self, pipe: "TMesagesPipe") -> None:
        self.__msg_pipe = pipe
        self.state.assign_senders(pipe.get_state_facade())

    def assign_plugin(self, plugin: PPlugin) -> None:
        self.__test_suite = plugin.create_test_suite(
            state_conditions=self.state_conditions.get_facade(),
            xoa_out=self.__msg_pipe.get_facade()
        )

    def run(self, observer: TObserver) -> None:
        self.__observer = observer
        self.state.set_run()
        self.__task = asyncio.create_task(
            self.__test_suite.start(),
            name=f"{self.suite_name}[{self.id}]"
        )
        self.__task.add_done_callback(self.__on_execution_terminated)

    async def toggle_pause(self) -> None:
        """User interface toggle pause."""
        if self.state.is_running:
            self.state.set_pause()
            self.state_conditions.pause()
            await self.__test_suite.on_pause()
        elif self.state.is_paused:
            self.state.set_run()
            self.state_conditions.resume()
            await self.__test_suite.on_continue()

    async def stop(self) -> None:
        """User interface stop the test suite."""
        self.state.set_stop()
        self.state_conditions.stop()
        await self.__test_suite.on_stop()
        self.__task.cancel()
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            await self.__task
