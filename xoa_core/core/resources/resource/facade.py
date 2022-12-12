from __future__ import annotations

import asyncio
from dataclasses import asdict

from functools import lru_cache
from typing import (
    Any,
    Callable,
    Coroutine,
)
from xoa_driver.testers import GenericAnyTester
from xoa_core.core.utils.observer import SimpleObserver

from . import const
from . import (
    exceptions,
    misc,
)
from .models.tester import TesterModel, TesterInfoModel
from .models.types import (
    TesterID,
    StorageResource,
)


EventCallback = Callable[[TesterInfoModel, str], Coroutine[None, None, None]]


class Events:
    __slots__ = ("__observer",)

    def __init__(self, observer: SimpleObserver) -> None:
        self.__observer = observer

    def reset(self) -> None:
        self.__observer.reset()

    def on_connected(self, func: EventCallback) -> None:
        self.__observer.subscribe(const.CONNECTED, func)

    def on_disconnected(self, func: EventCallback) -> None:
        self.__observer.subscribe(const.DISCONNECTED, func)

    def on_changed(self, func: EventCallback) -> None:
        self.__observer.subscribe(const.CHANGED, func)


class Resource:
    __slots__ = ("tester", "dataset", "__observer")

    def __init__(self, credentials: misc.Credentials, *, name: str | None = None, keep_disconnected: bool | None = None) -> None:
        self.__observer: SimpleObserver[str] = SimpleObserver(pass_event=True)
        self.dataset = TesterModel(
            id=misc.make_resource_id(credentials.host, credentials.port),
            product=credentials.product,
            host=credentials.host,
            port=credentials.port,
            password=credentials.password,
            name=name or " - "
        )
        if keep_disconnected is not None:
            self.dataset.keep_disconnected = keep_disconnected
        self.tester = self.__get_tester_inst()

    def __get_tester_inst(self) -> GenericAnyTester:
        if tester_ := misc.get_tester_inst(self.credentials):
            return tester_
        raise exceptions.InvalidTesterTypeError(self.credentials)

    async def __on_tester_loose_connection(self, _) -> None:
        self.__observer.emit(const.DISCONNECTED, self.info())
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
        self.dataset.keep_disconnected = True

    def __on_data_changed(self) -> None:
        self.__observer.emit(const.CHANGED, self.info())

    def set_index(self, tester_index: int) -> None:
        self.dataset.index = tester_index

    async def connect(self) -> None:
        if self.tester.session.is_online:
            raise exceptions.IsConnectedError(self.id)
        self.dataset.keep_disconnected = False
        try:
            await self.tester
        except Exception as e:
            raise exceptions.TesterCommunicationError(self.credentials, e) from None
        else:
            # IMPORTANT: To keep order of next functions call
            # 1 - sync which can emit CHANGED event
            # 2 - Emit CONNECTED
            # 3 - Subscribe on tester disconnected
            await self.dataset.sync(self.tester, self.__on_data_changed)
            self.__observer.emit(const.CONNECTED, self.info())
            self.tester.on_disconnected(self.__on_tester_loose_connection)

    async def disconnect(self) -> None:
        if not self.tester.session.is_online:
            raise exceptions.IsDisconnectedError(self.id)
        self.dataset.keep_disconnected = True
        await self.tester.session.logoff()
        self.tester = self.__get_tester_inst()

    async def configure(self, config: dict[str, Any]) -> None:
        raise NotImplementedError()

    def prepare_session(self, username: str, debug: bool = False) -> GenericAnyTester:
        if tester_ := misc.get_tester_inst(self.credentials, username=username, debug=debug):
            return tester_
        raise exceptions.InvalidTesterTypeError(self.credentials)

    @property
    def id(self) -> TesterID:
        return self.dataset.id

    @property
    def keep_disconnected(self) -> bool:
        return self.dataset.keep_disconnected

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
    @lru_cache
    def credentials(self) -> misc.Credentials:
        return misc.Credentials.parse_obj(self.store_data)

    def info(self) -> TesterInfoModel:
        return TesterInfoModel.parse_obj(asdict(self.dataset))

    @property
    def events(self) -> Events:
        return Events(self.__observer)
