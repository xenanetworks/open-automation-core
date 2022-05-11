from typing import (
    TYPE_CHECKING,
    Protocol,
    Any,
    Callable,
    # Optional,
    Coroutine,
    Tuple,
    AsyncGenerator,
    # TypeVar,
)

if TYPE_CHECKING:
    import asyncio
    # from xoa_driver import testers
    from functools import partialmethod
    # from valhalla_core.core.test_suites.datasets import PluginData

from xoa_core.core.messanger.misc import EMsgType, Message, PipeFacade, PipeStateFacade


# region Execution Manager

# TTesterReceaver = Callable[[str, str], Optional["testers.GenericAnyTester"]]

# endregion

# region Utils SimpleObserver

TCallback = Callable[..., Coroutine[Any, None, None]]

class TObserver(Protocol):
    def subscribe(self, evt: int, func: TCallback) -> None: ...
    def emit(self, evt: int, *args, **kwargs) -> None: ...

# endregion


# region Messanger


class TMesagesPipe(Protocol):
    async def _add_stream(self, key: str, queue: "asyncio.Queue") -> None: ...
    async def _free_stream(self, key: str) -> None: ...
    async def disable(self) -> None: ...
    def transmit(self, msg: Any, *, msg_type: EMsgType = EMsgType.DATA) -> None: ...
    def get_facade(self) -> PipeFacade: ...
    def get_state_facade(self) -> PipeStateFacade: ...
    transmit_warn: "partialmethod"
    transmit_err: "partialmethod"

class TMessagesHandler(Protocol):
    def get_pipe(self, name: str) -> "TMesagesPipe": ...
    async def disable_pipe(self, name: str) -> None: ...
    def avaliable_pipes(self) -> Tuple[str, ...]: ...
    async def changes(self, *names: str) -> AsyncGenerator["Message", None]: ...


# endregion