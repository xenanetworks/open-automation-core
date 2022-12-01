import asyncio
import collections
from contextlib import suppress
from typing import (
    Dict,
    Generic,
    List,
    Callable,
    Any,
    Coroutine,
    TypeVar,
)
import warnings
CB = Callable[..., Coroutine[Any, None, None]]
T = TypeVar("T")


class SimpleObserver(Generic[T]):
    __slots__ = ("__events", "__loop")

    def __init__(self) -> None:
        self.__events: Dict[T, List[CB]] = collections.defaultdict(list)
        self.__loop = asyncio.get_event_loop()

    def __handle_exceptions(self, task: "asyncio.Task") -> None:
        with suppress(asyncio.CancelledError):
            if e := task.exception():
                warnings.warn(str(e))

    def subscribe(self, evt: T, func: CB) -> None:
        self.__events[evt].append(func)

    def emit(self, evt: T, *args, **kwargs) -> None:
        for action in self.__events[evt]:
            task = self.__loop.create_task(action(*args, **kwargs))
            task.add_done_callback(self.__handle_exceptions)
