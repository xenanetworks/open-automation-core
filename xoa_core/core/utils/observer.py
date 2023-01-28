import asyncio
import collections
from typing import (
    Dict,
    List,
    Callable,
    Any,
    Coroutine,
)
CB = Callable[..., Coroutine[Any, None, None]]


class SimpleObserver:
    __slots__ = ("__events", "__loop",)

    def __init__(self) -> None:
        self.__events: Dict[int, List[CB]] = collections.defaultdict(list)
        self.__loop = asyncio.get_event_loop()

    def __handle_exceptions(self, task: "asyncio.Task") -> None:
        if e := task.exception():
            print(e)

    def subscribe(self, evt: int, func: CB) -> None:
        self.__events[evt].append(func)

    def emit(self, evt: int, *args, **kwargs) -> None:
        for action in self.__events[evt]:
            task = self.__loop.create_task(action(*args, **kwargs))
            task.add_done_callback(self.__handle_exceptions)
