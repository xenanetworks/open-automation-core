from __future__ import annotations

import asyncio
from typing import (
    Any,
    Callable,
    Generator,
)

from pydantic import BaseModel

from .resource import const
from .resource.facade import Resource
from .resource.models.types import TesterID
from .resource.models.tester import TesterInfoModel
from .resource.exceptions import UnknownResourceError


""""
Messages Order
CONNECTED - Ignored message

1. ADDED - add tester to the pool send message to the user
    - CONNECTED - If know tester get connected send msg to user
    - CHANGED - If cnown tester data was changet sending msg to user
    - DISCONNECTED - If know tester get disconnected send msg to user
2. REMOVED - Extract tester and send message to the user

DISCONNECTED - Ignored message
"""


class MultiResActions:
    """
    Interface of actions applied to
    multiple Resources at the same time
    """

    __slots__ = ("resources",)

    def __init__(self, resources: dict[TesterID, Resource]) -> None:
        self.resources = resources

    async def connect(self) -> Generator[Resource, None, None]:
        prefiltered = (r for r in self.resources.values() if not r.keep_disconnected)
        result = await asyncio.gather(
            *[r.connect() for r in prefiltered],
            return_exceptions=True
        )
        return (
            resource
            for result, resource in zip(result, prefiltered)
            if isinstance(result, Exception)
        )

    def get_items(self) -> Generator[TesterInfoModel, None, None]:
        return (r.info() for r in self.resources.values())

    def select(self, tester_ids: tuple[TesterID, ...]) -> Generator[Resource, None, None]:
        for tester_id in tester_ids:
            res = self.resources.get(tester_id, None)
            if not res:
                raise UnknownResourceError(tester_id)
            yield res


class Msg(BaseModel):
    action: str
    data: TesterInfoModel


class ResourcesPool:
    __slots__ = ("__resources", "__publisher")

    def __init__(self, publisher: Callable[[Any], None]) -> None:
        self.__publisher = publisher
        self.__resources: dict[TesterID, Resource] = dict()

    def __contains__(self, key: TesterID) -> bool:
        return key in self.__resources

    def __len__(self) -> int:
        return len(self.__resources)

    def __optimize(self) -> None:
        """Realocate pool for keep low memory usage."""
        self.__resources = {**self.__resources}
        for idx, item in enumerate(self.__resources.values()):
            item.set_index(idx)

    async def __publish_message(self, dataset: TesterInfoModel, event: str) -> None:
        message = Msg(action=event, data=dataset)
        self.__publisher(message)

    async def add(self, resource: Resource) -> None:
        """Add Resource to the pool and subscribe on changes"""
        self.__resources[resource.id] = resource
        self.__optimize()
        await self.__publish_message(resource.info(), const.ADDED)
        resource.events.on_changed(self.__publish_message)
        resource.events.on_connected(self.__publish_message)
        resource.events.on_disconnected(self.__publish_message)

    def get(self, id: TesterID) -> Resource:
        """Get a known Resource by it's ID"""
        if res := self.__resources.get(id, None):
            return res
        raise UnknownResourceError(id)

    async def extract(self, id: TesterID) -> Resource:
        """Exclude the Resource from the pool and stop propagate changes"""
        if resource := self.__resources.pop(id, None):
            self.__optimize()
            resource.events.reset()
            await self.__publish_message(resource.info(), const.REMOVED)
            return resource
        raise UnknownResourceError(id)

    @property
    def all(self) -> MultiResActions:
        return MultiResActions(self.__resources)
