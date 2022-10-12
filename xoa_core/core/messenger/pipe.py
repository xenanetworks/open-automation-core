import asyncio
import contextlib
from functools import partialmethod
from typing import (
    Any,
    Final,
    Dict,
    Optional,
)

from xoa_core.core.generic_types import TObserver
from . import misc


class MesagesPipe:
    __slots__ = ("name", "__evt", "__queue", "__observer", "__push_streams", "__lock", "__procesor")

    def __init__(self, name: str, observer: "TObserver") -> None:
        self.name: Final[str] = name
        self.__evt = asyncio.Event()
        self.__queue: "asyncio.Queue[misc.Message]" = asyncio.Queue()
        self.__observer = observer
        self.__lock = asyncio.Lock()
        self.__push_streams: Dict[str, asyncio.Queue[Optional["misc.Message"]]] = {}
        self.__procesor = asyncio.create_task(
            self.__worker(),
            name=f"MessagesPipe[{self.name}]"
        )

    async def _add_stream(self, key: str, queue: asyncio.Queue) -> None:
        async with self.__lock:
            self.__push_streams[key] = queue

    async def _free_stream(self, key: str) -> None:
        async with self.__lock:
            self.__push_streams.pop(key)
            self.__push_streams = dict(self.__push_streams)

    async def __worker(self) -> None:
        while True:
            val = await self.__queue.get()
            async with self.__lock:
                await asyncio.gather(
                    *[
                        stm.put(val)
                        for stm in self.__push_streams.values()
                    ]
                )
            self.__queue.task_done()

    async def disable(self) -> None:
        self.__evt.set()
        await self.__queue.join()
        self.__procesor.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self.__procesor
        for stm in self.__push_streams.values():
            stm.put_nowait(None)  # Inform to stop watching
        self.__observer.emit(misc.DISABLED, self.name)

    def transmit(self, msg: Any, *, msg_type: misc.EMsgType = misc.EMsgType.DATA) -> None:
        """Unblocable function"""
        assert not self.__evt.is_set(), "Message pipe is closed"
        message = misc.Message(
            pipe_name=self.name,
            destenation=None,
            type=msg_type,
            payload=msg
        )
        self.__queue.put_nowait(message)

    def get_facade(self) -> misc.PipeFacade:
        return misc.PipeFacade(self.transmit)

    def get_state_facade(self) -> misc.PipeStateFacade:
        return misc.PipeStateFacade(self.transmit)

    transmit_warn = partialmethod(transmit, msg_type=misc.EMsgType.WARNING)
    transmit_err = partialmethod(transmit, msg_type=misc.EMsgType.ERROR)
