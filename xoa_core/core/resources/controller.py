from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
)
if TYPE_CHECKING:
    from xoa_driver import testers
    from xoa_core.core.generic_types import TMesagesPipe

from .pool import ResourcesPool
from .resource.facade import Resource
from .resource.misc import Credentials
from .storage import PrecisionStorage
from .types import TesterID, TesterInfoModel


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
        failed = await self._pool.all.connect()
        for resource in failed:
            resource.dataset.keep_disconnected = True
            await self.__store.save(resource.store_data)

    async def add_tester(self, credentials: Credentials) -> TesterID:
        new_resource = Resource(credentials)  # InvalidTesterTypeError
        if await self.__store.is_registered(new_resource.id):
            return new_resource.id
        await new_resource.connect()  # TesterCommunicationError
        await self.__store.save(new_resource.store_data)
        await self._pool.add(new_resource)
        return new_resource.id

    async def remove_tester(self, id: TesterID) -> None:
        resource = await self._pool.extract(id)
        await self.__store.delete(resource.id)
        await resource.disconnect()

    async def configure_tester(self, id: TesterID, config: dict[str, Any]) -> None:
        """ User Apply Changes """
        resource = self._pool.get(id)
        await resource.configure(config)

    async def list_testers_info(self) -> list[TesterInfoModel]:
        return list(self._pool.all.get_items())

    async def get_tester_info(self, tester_id: TesterID) -> TesterInfoModel:
        resource = self._pool.get(tester_id)
        return resource.info()

    async def connect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        await resource.connect()  # TesterCommunicationError, IsConnectedError
        await self.__store.save(resource.store_data)

    async def disconnect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        await resource.disconnect()  # IsDisconnectedError
        await self.__store.save(resource.store_data)

    def get_testers_by_id(self, testers_ids: Iterable[TesterID], username: str, debug: bool = False) -> dict[str, "testers.GenericAnyTester"]:
        return {
            res.id: res.prepare_session(username, debug)
            for res in self._pool.all.select(tuple(testers_ids))
        }
