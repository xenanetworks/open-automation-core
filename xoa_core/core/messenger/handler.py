import asyncio
import uuid
import contextlib
from typing import (
    Optional,
    Tuple,
    Dict,
    Set,
    AsyncGenerator
)
from xoa_core.core.utils import observer
from .pipe import MesagesPipe
from . import misc


async def _get_from_queue(queue: "asyncio.Queue[Optional[misc.Message]]") -> AsyncGenerator[Optional[misc.Message], None]:
    while True:
        msg = await queue.get()
        try:
            yield msg
        finally:
            queue.task_done()


class OutMessagesHandler:
    __slots__ = ("__pipes", "__senders", "__observer", )

    def __init__(self) -> None:
        self.__pipes: Dict[str, MesagesPipe] = dict()
        self.__observer = observer.SimpleObserver()
        self.__observer.subscribe(misc.DISABLED, self.__on_pipe_disabled)

    def get_pipe(self, name: str) -> "MesagesPipe":
        if name in self.__pipes:
            return self.__pipes[name]
        self.__pipes[name] = pipe = MesagesPipe(
            name,
            self.__observer,
        )
        return pipe

    async def disable_pipe(self, name: str) -> None:
        if name not in self.__pipes:
            return None
        await self.__pipes[name].disable()

    def avaliable_pipes(self) -> Tuple[str, ...]:
        return tuple(self.__pipes.keys())

    async def __on_pipe_disabled(self, name: str) -> None:
        del self.__pipes[name]

    @contextlib.asynccontextmanager
    async def __user_stream(self, queue: "asyncio.Queue[Optional[misc.Message]]", *names: str) -> AsyncGenerator[None, None]:
        key = str(uuid.uuid4())
        pipes = (self.__pipes[name] for name in names)
        await asyncio.gather(*[pipe._add_stream(key, queue) for pipe in pipes])
        try:
            yield
        finally:
            await asyncio.gather(*[pipe._free_stream(key) for pipe in pipes])

    async def changes(self, *names: str, _filter: Optional[Set["misc.EMsgType"]] = None) -> AsyncGenerator[misc.Message, None]:
        if not all((self.__pipes.get(name) for name in names)):
            return
        msg_queue: asyncio.Queue[Optional["misc.Message"]] = asyncio.Queue()
        async with self.__user_stream(msg_queue, *names):
            async for msg in _get_from_queue(msg_queue):
                if msg is None:
                    break
                if _filter and msg.type not in _filter:
                    continue
                yield msg
