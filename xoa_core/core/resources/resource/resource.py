from __future__ import annotations
import asyncio
from functools import partial, partialmethod
import hashlib
from typing import Any, Callable, Coroutine
from dataclasses import asdict

from xoa_driver.testers import GenericAnyTester

from xoa_core.core.resources.datasets.external.credentials import Credentials
from .dataset.tester import TesterModel
from ..types import (
    TesterID,
    StorageResource,
)

from ..exceptions import (
    InvalidTesterTypeError,
    TesterCommunicationError,
)
from ..misc import get_tester_inst
from xoa_core.core.utils.observer import SimpleObserver
# TODO: need to handle disconnection if server drop the connection


def _make_tester_id(host: str, port: int) -> TesterID:
    val_bytes = f"{host}:{port}".encode("utf-8")
    return TesterID(hashlib.md5(val_bytes).hexdigest())


CB = Callable[..., Coroutine[Any, None, None]]

CONNECTED = 1
DISCONNECTED = 2
CHANGED = 3


class Events:
    def __init__(self, observer: SimpleObserver) -> None:
        self.__observer = observer

    def __register(self, event: int, func: CB) -> None:
        self.__observer.subscribe(event, func)

    connected = partialmethod(__register, event=CONNECTED)
    disconnected = partialmethod(__register, event=DISCONNECTED)
    change = partialmethod(__register, event=CHANGED)


class Resource:
    __slots__ = ("tester", "dataset", "observer")

    def __init__(self, credentials: Credentials, *, name: str | None = None) -> None:
        self.observer = SimpleObserver()
        self.dataset = TesterModel(
            id=_make_tester_id(credentials.host, credentials.port),
            product=credentials.product,
            host=credentials.host,
            port=credentials.port,
            password=credentials.password,
            name=name or " - "
        )
        self.tester = self.__get_tester_inst()
        # self.observer.subscribe(CONNECTED, )
        # self.observer.subscribe(DISCONNECTED, )
        self.observer.subscribe(DISCONNECTED, self.__on_loose_connection)
        # self.observer.subscribe(CHANGED, )

    def __get_tester_inst(self) -> GenericAnyTester:
        if tester_ := get_tester_inst(self.dataset):
            return tester_
        raise InvalidTesterTypeError(self.dataset)

    async def __on_loose_connection(self) -> None:
        if self.keep_disconnected:
            return None
        for retry in range(5):
            await asyncio.sleep(delay=retry * 2)
            try:
                await self.connect()
            except Exception:
                continue
            else:
                return None
        self.keep_disconnected = True

    async def connect(self) -> bool:
        if self.tester.session.is_online:
            return False
        try:
            await self.tester
        except Exception as e:
            raise TesterCommunicationError(self.dataset, e) from None
        else:
            self.observer.emit(CONNECTED)
            await self.dataset.sync(self.tester, partial(self.observer.emit, CHANGED))
            return True

    async def disconnect(self) -> bool:
        if self.tester.session.is_online:
            await self.tester.session.logoff()
            self.tester = self.__get_tester_inst()
            return True
        return False

    async def configure(self) -> None:
        raise NotImplementedError()

    @property
    def id(self) -> TesterID:
        return self.dataset.id

    @property
    def keep_disconnected(self) -> bool:
        return self.dataset.keep_disconnected

    @keep_disconnected.setter
    def keep_disconnected(self, val: bool) -> None:
        self.dataset.keep_disconnected = val

    @property
    def store_data(self) -> StorageResource:
        return {
            "id": self.dataset.id,
            "product": self.dataset.product,
            "host": self.dataset.host,
            "port": self.dataset.port,
            "password": self.dataset.password,
            "name": self.dataset.name,
            "keep_disconnected": self.dataset.keep_disconnected
        }

    @property
    def credentials(self) -> Credentials:
        return Credentials.parse_obj(self.store_data)

    @property
    def as_dict(self) -> dict[str, Any]:
        return asdict(self.dataset)

    @property
    def call_on(self) -> Events:
        return Events(self.observer)
