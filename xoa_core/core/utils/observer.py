import asyncio
import collections
from contextlib import suppress
from enum import Enum
from typing import (
    Dict,
    List,
    Callable,
    Any,
    Coroutine,
)
import warnings
CB = Callable[..., Coroutine[Any, None, None]]


class SimpleObserver:
    __slots__ = ("__events", "__loop")

    def __init__(self) -> None:
        self.__events: Dict[Enum, List[CB]] = collections.defaultdict(list)
        self.__loop = asyncio.get_event_loop()

    def __handle_exceptions(self, task: "asyncio.Task") -> None:
        with suppress(asyncio.CancelledError):
            if e := task.exception():
                warnings.warn(str(e))

    def subscribe(self, evt: Enum, func: CB) -> None:
        self.__events[evt].append(func)

    def emit(self, evt: Enum, *args, **kwargs) -> None:
        for action in self.__events[evt]:
            task = self.__loop.create_task(action(*args, **kwargs))
            task.add_done_callback(self.__handle_exceptions)
