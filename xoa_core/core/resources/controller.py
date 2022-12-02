from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from xoa_driver import testers
    from xoa_core.core.generic_types import TMesagesPipe

from .datasets.external.credentials import Credentials
from .datasets.external.tester import TesterExternalModel
from .resource.pool import ResourcesPool
from .resource import Resource
from .storage import PrecisionStorage
from .types import TesterID, StorageResource

# TODO:  organize propper imports
# TODO:  save keep_disconnected on failure to add tester at startup time
# TODO:  save keep_disconnected after connection failed and all atempts to reconnect also was unsuccesful


class ResourcesController:
    __slots__ = ("__store", "_pool",)

    def __init__(self, msg_pipe: "TMesagesPipe", data_storage: PrecisionStorage) -> None:
        self.__store = data_storage
        self._pool = ResourcesPool(msg_pipe.transmit)

    async def start(self) -> None:
        known_testers = await self.__store.get_all()
        for credential in known_testers:
            resource = Resource(
                Credentials.parse_obj(credential),
                name=credential.get("name"),
                keep_disconnected=credential.get("keep_disconnected", False)
            )
            await self._pool.add(resource)
        await self._pool.all.connect()

    async def add_tester(self, credentials: Credentials) -> bool:
        new_resource = Resource(credentials)  # InvalidTesterTypeError
        if await self.__store.is_registered(new_resource.id):
            return False
        await new_resource.connect()  # TesterCommunicationError
        await self.__store.save(StorageResource(**new_resource.as_dict))
        await self._pool.add(new_resource)
        return True

    async def remove_tester(self, id: TesterID) -> None:
        resource = await self._pool.extract(id)
        await resource.disconnect()
        await self.__store.delete(resource.id)

    async def configure_tester(self, id: TesterID, config: dict[str, Any]) -> None:
        """ User Apply Changes """
        resource = self._pool.get(id)
        await resource.configure(config)

    async def get_all_testers(self) -> dict[TesterID, TesterExternalModel]:
        return self._pool.all.get_dict()

    async def connect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        await resource.connect()
        await self.__store.save(StorageResource(**resource.as_dict))

    async def disconnect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        await resource.disconnect()
        await self.__store.save(StorageResource(**resource.as_dict))

    def get_testers_by_id(self, testers_ids: Iterable[TesterID], username: str, debug: bool = False) -> dict[str, "testers.GenericAnyTester"]:
        return {
            res.id: res.prepare_session(username, debug)
            for res in self._pool.all.select(tuple(testers_ids))
        }
