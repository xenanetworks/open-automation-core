import asyncio
import shelve
from functools import (
    partial,
    wraps,
    partialmethod,
)
from typing import (
    Dict,
    Optional,
    TYPE_CHECKING,
)

from .datasets.internal.credentials import CredentialsModel
if TYPE_CHECKING:
    from .misc import IProps


class PrecisionStorage:
    __slots__ = ("_lock", "_loop", "__open",)

    def __init__(self, storage_path: str) -> None:
        self._lock = asyncio.Lock()
        self._loop = asyncio.get_event_loop()
        self.__open = partial(shelve.open, storage_path)

    def _run_in_executor(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self._lock:
                return await self._loop.run_in_executor(None, func, *args, **kwargs)
        return wrapper

    def _insert(self, params: "IProps") -> None:
        with self.__open() as db:
            db[params.id] = CredentialsModel.parse_obj(params)

    def _get_all(self) -> Dict[str, "CredentialsModel"]:
        with self.__open() as db:
            return dict(db)  # type: ignore

    def _get(self, id: str) -> Optional["CredentialsModel"]:
        with self.__open() as db:
            return db.get(id, None)  # type: ignore

    def _delete(self, id: str) -> None:
        with self.__open() as db:
            if id not in db:
                return None
            del db[id]

    def _contains(self, id: str) -> bool:
        with self.__open() as db:
            return id in db

    async def get_all(self) -> Dict[str, "CredentialsModel"]:
        return await self._run_in_executor(self._get_all)()

    async def get(self, id: str) -> Optional["CredentialsModel"]:
        return await self._run_in_executor(self._get)(id)

    async def is_registered(self, id: str) -> bool:
        return await self._run_in_executor(self._contains)(id)

    async def keep_disconnected(self, id: str, value: bool = True) -> None:
        if obj := await self.get(id):
            obj.keep_disconnected = value
            self.remember(obj)

    keep_connected = partialmethod(keep_disconnected, value=False)

    def remember(self, params: "IProps") -> None:
        asyncio.create_task(
            self._run_in_executor(self._insert)(params)
        )

    def forget(self, id: str) -> None:
        asyncio.create_task(
            self._run_in_executor(self._delete)(id)
        )
