import asyncio
from . import exceptions


class StateConditionsFacade:
    __slots__ = ("__wait_if_paused", "__stop_if_stopped")

    def __init__(self, wait_if_paused, stop_if_stopped) -> None:  # TODO: Add type notations
        self.__wait_if_paused = wait_if_paused
        self.__stop_if_stopped = stop_if_stopped

    async def wait_if_paused(self) -> None:
        await self.__wait_if_paused()

    async def stop_if_stopped(self) -> None:
        await self.__stop_if_stopped()


class StateConditions:
    __slots__ = ("continue_event", "stop_event")

    def __init__(self) -> None:
        self.continue_event = asyncio.Event()
        self.continue_event.set()
        self.stop_event = asyncio.Event()

    async def wait_if_paused(self) -> None:
        """Wait till user toggle pause state."""
        await self.continue_event.wait()

    async def stop_if_stopped(self) -> None:
        if self.stop_event.is_set():
            raise exceptions.StopPlugin()

    def get_facade(self) -> StateConditionsFacade:
        return StateConditionsFacade(
            self.wait_if_paused,
            self.stop_if_stopped
        )

    def pause(self) -> None:
        self.continue_event.clear()

    def resume(self) -> None:
        self.continue_event.set()

    def stop(self) -> None:
        self.stop_event.set()
