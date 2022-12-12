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

from xoa_core.core.messenger.misc import EMsgType, Message, PipeFacade, PipeStateFacade


# region Execution Manager

# TTesterReceaver = Callable[[str, str], Optional["testers.GenericAnyTester"]]

# endregion

# region Utils SimpleObserver

TCallback = Callable[..., Coroutine[Any, None, None]]


class TObserver(Protocol):
    def subscribe(self, evt: int, func: TCallback) -> None: ...  # noqa: E704
    def emit(self, evt: int, *args, **kwargs) -> None: ...  # noqa: E704

# endregion


# region Messanger


class TMesagesPipe(Protocol):
    async def _add_stream(self, key: str, queue: "asyncio.Queue") -> None: ...  # noqa: E704
    async def _free_stream(self, key: str) -> None: ...  # noqa: E704
    async def disable(self) -> None: ...  # noqa: E704
    def transmit(self, msg: Any, *, msg_type: EMsgType = EMsgType.DATA) -> None: ...  # noqa: E704
    def get_facade(self) -> PipeFacade: ...  # noqa: E704
    def get_state_facade(self) -> PipeStateFacade: ...  # noqa: E704
    transmit_warn: "partialmethod"
    transmit_err: "partialmethod"


class TMessagesHandler(Protocol):
    def get_pipe(self, name: str) -> "TMesagesPipe": ...  # noqa: E704
    async def disable_pipe(self, name: str) -> None: ...  # noqa: E704
    def avaliable_pipes(self) -> Tuple[str, ...]: ...  # noqa: E704
    async def changes(self, *names: str) -> AsyncGenerator["Message", None]: ...  # noqa: E704


# endregion
