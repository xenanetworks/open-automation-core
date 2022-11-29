from __future__ import annotations
from functools import partial
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    Set,
)
if TYPE_CHECKING:
    from xoa_core.core.utils import observer
    from .datasets.external.tester import TesterExternalModel
from .datasets import enums
from . import misc
from . import exceptions
from .resource import Resource
from .types import TesterID


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

    @property
    def avaliable_resources(self) -> dict[str, "TesterExternalModel"]:
        return {r.id: r.as_pydantic for r in self.__resources.values()}

    async def add(self, resource: Resource) -> None:
        await resource.init_dataset(props.id, props.product)
        self.__resources[resource.id] = resource
        self.__optimize()

    def get(self, id: TesterID) -> Resource | None:
        return self.__resources.get(id, None)

    def remove(self, id: TesterID) -> bool:
        if self.__resources.pop(id, None):
            self.__optimize()
            return True
        return False
