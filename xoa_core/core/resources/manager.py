from __future__ import annotations
# from functools import partial
from typing import (
    TYPE_CHECKING,
    Iterable,
)
if TYPE_CHECKING:
    from xoa_driver import testers
    from xoa_core.core.generic_types import TMesagesPipe
from .datasets.external.tester import TesterExternalModel


# from xoa_core.core.utils import observer

from .resource import Resource
from .pool import ResourcesPool
from .storage import PrecisionStorage
from .types import TesterID

# from .datasets.enums import EResourcesEvents
from .datasets.external.credentials import Credentials


from . import misc
from .exceptions import (
    InvalidTesterTypeError,
    UnknownResourceError,
    IsDisconnectedError,
    IsConnectedError
)


class ResourcesManager:
    __slots__ = ("_msg_pipe", "__store", "__observer", "_pool",)

    def __init__(self, msg_pipe: "TMesagesPipe", data_storage: PrecisionStorage) -> None:
        # self._msg_pipe = msg_pipe
        self.__store = data_storage

        self._pool = ResourcesPool()
        # self._pool.use_transmitter(msg_pipe.transmit)
        # self._pool.on.added(self._msg_pipe.transmit)
        # self._pool.on.removed(self._msg_pipe.transmit)
        # self._pool.on.connected(self._msg_pipe.transmit)
        # self._pool.on.disconnected(self._msg_pipe.transmit)
        # self._pool.on.data_changed(self._msg_pipe.transmit)

        # self.__observer.subscribe(EResourcesEvents.ADDED, self.__on_tester_added)
        # self.__observer.subscribe(EResourcesEvents.DISCONNECTED, self.__on_tester_disconnected)
        # self.__observer.subscribe(EResourcesEvents.INFO_CHANGE_TESTER, self.__on_tester_info_change)
        # self.__observer.subscribe(EResourcesEvents.REMOVED, self.__on_tester_removed)

    async def start(self) -> None:
        known_testers = await self.__store.get_all()
        for credential in known_testers:
            resource = Resource(
                Credentials.parse_obj(credential),
                name=credential.get("name")
            )
            resource.keep_disconnected = credential.get("keep_disconnected", False)
            self._pool.add(resource)
        await self._pool.all.connect()

    async def add_tester(self, credentials: Credentials) -> bool:
        new_resource = Resource(credentials)  # InvalidTesterTypeError
        if await self.__store.is_registered(new_resource.id):
            return False
        await new_resource.connect()  # TesterCommunicationError
        new_resource.keep_disconnected = False
        await self.__store.save(new_resource)
        self._pool.add(new_resource)
        return True

    async def remove_tester(self, id: TesterID) -> None:
        resource = self._pool.extract(id)
        if not resource:
            raise UnknownResourceError(id)
        await resource.disconnect()
        await self.__store.delete(resource.id)

    async def configure_tester(self) -> None:
        """ User Apply Changes """
        # await self.__store.save(new_resource.as_dict)
        pass

    async def get_all_testers(self) -> dict[TesterID, TesterExternalModel]:
        return self._pool.all.get_dict()

    async def connect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        if not resource:
            raise UnknownResourceError(id)
        resource.keep_disconnected = False
        if not await resource.connect():
            raise IsConnectedError(id)
        await self.__store.save(resource)

    async def disconnect(self, id: TesterID) -> None:
        resource = self._pool.get(id)
        if not resource:
            raise UnknownResourceError(id)
        resource.keep_disconnected = True
        if not await resource.disconnect():
            raise IsDisconnectedError(id)
        await self.__store.save(resource)

    def get_testers_by_id(self, testers_ids: Iterable[TesterID], username: str, debug=False) -> dict[str, "testers.GenericAnyTester"]:
        testers = {}
        for tester_id in testers_ids:
            resource = self._pool.get(tester_id)
            if resource is None:
                raise UnknownResourceError(tester_id)
            tester = misc.get_tester_inst(resource.credentials, username, debug)
            if tester is None:
                raise InvalidTesterTypeError(resource.credentials)
            testers[tester_id] = tester
        return testers
