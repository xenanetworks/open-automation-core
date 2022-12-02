from __future__ import annotations

import asyncio
from typing import Any, Dict, Protocol, ValuesView, Generator

from pydantic import BaseModel

from . import const
from ..datasets.external.tester import TesterExternalModel
from . import Resource
from .models.tester import TesterID
from .exceptions import UnknownResourceError


class MultiResActions:
    """
    Interface of actions applied to
    multiple Resources at the same time
    """

    __slots__ = ("resources",)

    def __init__(self, resources: ValuesView[Resource]) -> None:
        self.resources = resources

    async def connect(self) -> None:
        tasks = [r.connect() for r in self.resources if not r.keep_disconnected]
        await asyncio.gather(*tasks, return_exceptions=True)
        # for err in filter(lambda v: isinstance(v, Exception), result):
        #     ...

    def get_dict(self) -> dict[TesterID, "TesterExternalModel"]:
        return {
            r.id: TesterExternalModel.parse_obj(r.as_dict)
            for r in self.resources
        }

    def select(self, tester_ids: tuple[TesterID, ...]) -> Generator[Resource, None, None]:
        for res in self.resources:
            if res.id not in tester_ids:
                raise UnknownResourceError(res.id)
            yield res


""""
Messages Order
CONNECTED - Ignored message

1. ADDED - add tester to the pool send message to the user
    - CONNECTED - Try to initiate connection with the tester if OK send message to user
    - CHANGED - on tester data cahnged send message to the user
    - DISCONNECTED - send message to the user
2. REMOVED - Extract tester and send message to the user

DISCONNECTED - Ignored message
"""


class Msg(BaseModel):
    action: str
    data: Dict[str, Any]


class PublisherMethod(Protocol):
    def __call__(self, msg: Any) -> Any:
        ...


class ResourcesPool:
    __slots__ = ("__resources", "__publisher")

    def __init__(self, publisher: PublisherMethod) -> None:
        self.__publisher = publisher
        self.__resources: dict[TesterID, Resource] = dict()

    def __contains__(self, key: TesterID) -> bool:
        return key in self.__resources

    def __len__(self) -> int:
        return len(self.__resources)

    def __optimize(self) -> None:
        """Realocate pool for keep low memory usage."""
        self.__resources = {**self.__resources}

    async def __publish_message(self, dataset: dict[str, Any], event: str) -> None:
        message = Msg(action=event, data=dataset)
        self.__publisher(message)

    async def add(self, resource: Resource) -> None:
        """Add Resource to the pool and subscribe on changes"""
        self.__resources[resource.id] = resource
        self.__optimize()
        await self.__publish_message(resource.as_dict, const.ADDED)
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
            await self.__publish_message(resource.as_dict, const.REMOVED)
            return resource
        raise UnknownResourceError(id)

    @property
    def all(self) -> MultiResActions:
        return MultiResActions(self.__resources.values())
