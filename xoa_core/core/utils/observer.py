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
    __slots__ = ("__events", "__pass_event")

    def __init__(self, *, pass_event: bool = False) -> None:
        self.__pass_event = pass_event
        self.reset()

    def __handle_exceptions(self, task: "asyncio.Task") -> None:
        with suppress(asyncio.CancelledError):
            if e := task.exception():
                warnings.warn(str(e))

    def reset(self) -> None:
        self.__events: Dict[T, List[CB]] = collections.defaultdict(list)

    def subscribe(self, evt: T, func: CB) -> None:
        self.__events[evt].append(func)

    def emit(self, evt: T, *args, **kwargs) -> None:
        kwargs_ = {**kwargs, "event": evt} if self.__pass_event else kwargs
        for action in self.__events[evt]:
            task = asyncio.create_task(action(*args, **kwargs_))
            task.add_done_callback(self.__handle_exceptions)
