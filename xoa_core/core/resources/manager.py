import asyncio
from typing import (
    TYPE_CHECKING,
    Iterable,
    Generator,
    TypeVar,
    Union,
    Dict,
    Any,
)
if TYPE_CHECKING:
    from xoa_driver import testers
    from xoa_core.core.generic_types import TMesagesPipe
from .datasets.external.tester import TesterExternalModel


from xoa_core.core.utils import observer

from .resources_pool import ResourcesPool

from . import storage

from .datasets import enums
from .datasets.external import credentials
from .datasets.internal.credentials import CredentialsModel


from . import misc
from .exceptions import (
    InvalidTesterTypeError,
    TesterCommunicationError,
    ResourceNotAvaliableError
)

AllTesterTypes = Union["CredentialsModel", "TesterExternalModel"]

RM = TypeVar("RM", bound="ResourcesManager")


class ResourcesManager:
    __slots__ = ("_msg_pipe", "__precision_storage", "__observer", "_pool", )

    def __init__(self, msg_pipe: "TMesagesPipe", data_storage_path: str) -> None:
        self._msg_pipe = msg_pipe
        self.__precision_storage = storage.PrecisionStorage(data_storage_path)
        self.__observer = observer.SimpleObserver()
        self._pool = ResourcesPool(self.__observer)

        self.__observer.subscribe(enums.EResourcesEvents.ADDED, self.__tester_added)
        self.__observer.subscribe(enums.EResourcesEvents.EXCLUDED, self.__tester_excluded)
        self.__observer.subscribe(enums.EResourcesEvents.INFO_CHANGE_TESTER, self.__tester_info_change)

    def __await__(self: RM) -> Generator[Any, None, RM]:
        return self.__setup().__await__()

    async def __setup(self: RM) -> RM:
        known_testers = await self.__precision_storage.get_all()
        tasks = tuple(
            self._pool.add(tester)
            for tester in known_testers.values()
            if not tester.keep_disconnected
        )
        exceptions = filter(
            None,
            await asyncio.gather(*tasks, return_exceptions=True)
        )
        for err in exceptions:
            await self.__precision_storage.keep_disconnected(err.props.id)
            self._msg_pipe.transmit_err(err)
        return self

    async def add_tester(self, params: "credentials.Credentials") -> bool:
        if not await self.__precision_storage.is_registered(params.id):
            credentials = CredentialsModel.from_external(params)
            try:
                await self._pool.add(credentials)
            except (InvalidTesterTypeError, TesterCommunicationError) as err:
                self._msg_pipe.transmit_err(err)
            else:
                self.__precision_storage.remember(credentials)
                return True
        return False

    async def remove_tester(self, id: str):
        self.__precision_storage.forget(id)
        await self._pool.suspend(id)

    async def update_tester(self):
        """ User Apply Changes """
        pass

    async def get_all_testers(self) -> Dict[str, "AllTesterTypes"]:
        known_testers = await self.__precision_storage.get_all()
        all_credentials = {tid: TesterExternalModel.parse_obj(credentials) for tid, credentials in known_testers.items()}
        return {**all_credentials, **self._pool.avaliable_resources}

    async def connect(self, id: str) -> None:
        if id in self._pool.res_identifiers:
            return None
        if obj := await self.__precision_storage.get(id):
            try:
                await self._pool.add(obj)
            except (InvalidTesterTypeError, TesterCommunicationError) as err:
                self._msg_pipe.transmit_err(err)
            else:
                await self.__precision_storage.keep_connected(id)

    async def disconnect(self, id: str) -> None:
        await self.__precision_storage.keep_disconnected(id)
        await self._pool.suspend(id)

    def get_testers_by_id(self, testers_ids: Iterable[str], username: str, debug=False) -> Dict[str, "testers.GenericAnyTester"]:
        testers = {}
        for tester_id in testers_ids:
            resource = self._pool.use_resource(tester_id)
            if resource is None:
                raise ResourceNotAvaliableError(tester_id)
            tester = misc.get_tester_inst(resource.credentials, username, debug)
            if tester is None:
                raise InvalidTesterTypeError(resource.credentials)
            testers[tester_id] = tester
        return testers

    async def __tester_added(self, data: "TesterExternalModel") -> None:
        self._msg_pipe.transmit(data)

    async def __tester_excluded(self, id: str) -> None:
        if obj := await self.__precision_storage.get(id):
            self._msg_pipe.transmit(TesterExternalModel.parse_obj(obj))
            if obj.keep_disconnected:
                return None
            await self.connect(id)

    async def __tester_info_change(self, data: "TesterExternalModel") -> None:
        self._msg_pipe.transmit(data)
