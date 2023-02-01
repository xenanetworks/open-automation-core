

import asyncio
import contextlib
import time
from typing import Awaitable, TypeVar, AsyncGenerator, Protocol


class TResourcesManager(Protocol):
    async def clear_statistic_counters(self) -> None: ...  # noqa: E704
    async def start_traffic(self) -> None: ...  # noqa: E704
    async def stop_traffic(self) -> None: ...  # noqa: E704
    async def cleanup(self) -> None: ...  # noqa: E704
    async def setup(self) -> None: ...  # noqa: E704
    async def set_time_limit(self, duration_sec: int) -> None: ...  # noqa: E704
    async def get_time_elipsed(self) -> int: ...  # noqa: E704
    async def set_frame_limit(self, max_frames: int) -> None: ...  # noqa: E704
    @property
    def all_traffic_is_stop(self) -> bool: ...  # noqa: E704
    @property
    def all_ports_is_sync(self) -> bool: ...  # noqa: E704


T = TypeVar("T", bound="L23TestManager")


class L23TestManager:
    __slots__ = ("__testers", "__resources", "__lock")

    def __init__(self, resources: TResourcesManager) -> None:
        self.__resources = resources
        self.__lock = asyncio.Lock()

    async def setup(self):
        await self.__resources.setup()
        return self

    async def __aenter__(self: Awaitable[T]) -> T:
        return await self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        async with self.__lock:
            await self.__resources.cleanup()

    def __await__(self: T):  # type: ignore
        return self.setup().__await__()

    @contextlib.asynccontextmanager
    async def __traffic_runner(self) -> AsyncGenerator[None, None]:
        await self.__resources.clear_statistic_counters()
        await self.__resources.start_traffic()
        try:
            yield
        finally:
            async with self.__lock:
                await self.__resources.stop_traffic()

    async def generate_traffic(self, duration: int, *, sampling_rate: float = 1.0) -> AsyncGenerator[int, None]:
        await self.__resources.set_time_limit(duration)
        # await self.__resources.set_frame_limit(duration)
        time_clock = 0
        time_step = 1.0 / sampling_rate
        duration_accived = False
        async with self.__traffic_runner():
            while not self.__resources.all_traffic_is_stop:
                begin = time.time()
                time_clock = await self.__resources.get_time_elipsed()
                if time_clock == 0 or duration_accived:
                    await asyncio.sleep(0.01)
                    continue
                duration_accived = time_clock == duration
                yield time_clock * 100 // duration
                await asyncio.sleep(time_step - (time.time() - begin))
