import typing
from xoa_core.core.utils import observer
from xoa_core.core import exceptions

from .executor import SuiteExecutor
from ._events import Event

from xoa_core.core.generic_types import TMesagesPipe


class ExecutorsManager:

    __slots__ = ("__msg_pipe", "__executors", "__observer", "__mono")

    def __init__(self, pipe: "TMesagesPipe", mono: bool = False) -> None:
        self.__mono = mono
        self.__executors: typing.Dict[str, "SuiteExecutor"] = dict()
        self.__msg_pipe = pipe

        self.__observer = observer.SimpleObserver()
        self.__observer.subscribe(Event.STOPPED, self.__on_execution_stopped)
        self.__observer.subscribe(Event.ERROR, self.__on_execution_error)

    async def __on_execution_stopped(self, exec_id: str) -> None:
        del self.__executors[exec_id]
        self.__msg_pipe.transmit(f"Test Suite stopped: {exec_id}")

    async def __on_execution_error(self, suite_name: str, error: Exception) -> None:
        self.__msg_pipe.transmit(f"Test Suite Error: {suite_name}, {error}")

    def run(self, executor: "SuiteExecutor") -> str:
        if self.__mono and len(self.__executors) > 1:
            raise exceptions.MultiModeError()
        self.__executors[executor.id] = executor
        executor.run(self.__observer)
        self.__msg_pipe.transmit(f"Test Suite Started: {executor.id}")
        return executor.id

    async def stop(self, exec_id: str) -> None:
        if ex := self.__executors.get(exec_id):
            await ex.stop()

    async def toggle_pause(self, exec_id: str) -> None:
        if ex := self.__executors.get(exec_id):
            await ex.toggle_pause()
