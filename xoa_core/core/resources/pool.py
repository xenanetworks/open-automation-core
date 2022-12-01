from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, ValuesView
from pydantic import BaseModel
from xoa_core.core.utils.observer import SimpleObserver
from .datasets.external.tester import TesterExternalModel
from .resource import Resource
from .types import TesterID


@dataclass
class Actions:
    resources: ValuesView[Resource]

    async def connect(self) -> None:
        tasks = [r.connect() for r in self.resources if not r.keep_disconnected]
        result = await asyncio.gather(*tasks, return_exceptions=True)
        # for err in filter(lambda v: isinstance(v, Exception), result):
        #     ...

    def get_dict(self) -> dict[TesterID, "TesterExternalModel"]:
        return {
            r.id: TesterExternalModel.parse_obj(r.as_dict)
            for r in self.resources
        }


ADDED = "ADDED"
CONNECTED = "CONNECTED"
DISCONNECTED = "DISCONNECTED"
CHANGED = "CHANGED"
REMOVED = "REMOVED"

""""
Messages Order
1. CONNECTED - Try to initiate connection with the tester if OK send message to user
2.    ADDED - add tester to the pool send message to the user
3. CHANGED - on tester data cahnged send message to the user
4. DISCONNECTED - send message to the user
5. REMOVED - Extract tester and send message to the user
"""


class Msg(BaseModel):
    action: str
    data: dict[str, Any]


class PoolObserver:
    def __init__(self) -> None:
        self.publish = lambda msg: print(msg)
        self.observer: SimpleObserver[str] = SimpleObserver()
        self.observer.subscribe(ADDED, self.added)
        self.observer.subscribe(CONNECTED, self.connected)
        self.observer.subscribe(DISCONNECTED, self.disconnected)
        self.observer.subscribe(CHANGED, self.changed)
        self.observer.subscribe(REMOVED, self.removed)

    async def added(self, tester_data: dict[str, Any]) -> None:
        """Tester Added"""
        self.publish(
            Msg(action=ADDED, data=tester_data)
        )

    async def removed(self, tester_data: dict[str, Any]) -> None:
        """Tester Removed"""
        self.publish(
            Msg(action=REMOVED, data=tester_data)
        )

    async def connected(self, tester_data: dict[str, Any]) -> None:
        """Tester Connected"""
        self.publish(
            Msg(action=REMOVED, data=tester_data)
        )

    async def disconnected(self, tester_data: dict[str, Any]) -> None:
        """Tester Disconnected"""
        self.publish(
            Msg(action=REMOVED, data=tester_data)
        )

    async def changed(self, tester_data: dict[str, Any]) -> None:
        """Tester Data Changet"""
        self.publish(
            Msg(action=REMOVED, data=tester_data)
        )


class ResourcesPool:
    __slots__ = ("__resources", "__observer")

    def __init__(self) -> None:
        self.__observer = PoolObserver()
        self.__resources: dict[TesterID, Resource] = dict()

    def __contains__(self, key: TesterID) -> bool:
        return key in self.__resources

    def __len__(self) -> int:
        return len(self.__resources)

    def __optimize(self) -> None:
        """Realocate pool for keep low memory usage."""
        self.__resources = {**self.__resources}

    def add(self, resource: Resource) -> None:
        resource.call_on.change()
        resource.call_on.connected()
        resource.call_on.disconnected()
        self.__resources[resource.id] = resource
        self.__optimize()

    def get(self, id: TesterID) -> Resource | None:
        return self.__resources.get(id, None)

    def extract(self, id: TesterID) -> Resource | None:
        if resource := self.__resources.pop(id, None):
            self.__optimize()
            return resource
        return None

    @property
    def all(self) -> Actions:
        return Actions(self.__resources.values())
