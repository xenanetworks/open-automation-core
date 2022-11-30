from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, ValuesView
if TYPE_CHECKING:
    from .datasets.external.tester import TesterExternalModel
from .resource import Resource
from .types import TesterID


@dataclass
class Actions:
    resources: ValuesView[Resource]

    async def connect(self) -> None:
        tasks = [r.connect() for r in self.resources if not r.keep_disconnected]
        await asyncio.gather(*tasks, return_exceptions=True)

    def get_dict(self) -> dict[str, "TesterExternalModel"]:
        return {r.id: r.as_pydantic for r in self.resources}


class ResourcesPool:
    __slots__ = ("__resources",)

    def __init__(self) -> None:
        self.__resources: dict[TesterID, Resource] = dict()

    def __contains__(self, key: TesterID) -> bool:
        return key in self.__resources

    def __len__(self) -> int:
        return len(self.__resources)

    def __optimize(self) -> None:
        """Realocate pool for keep low memory usage."""
        self.__resources = {**self.__resources}

    def add(self, resource: Resource) -> None:
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
