from __future__ import annotations
import functools
import hashlib
from typing import Any, Callable
from dataclasses import asdict
from .datasets.internal.tester import TesterModel
# from .datasets.internal.credentials import CredentialsModel
from xoa_driver.testers import GenericAnyTester
from .types import TesterID, IProps
from .exceptions import (
    InvalidTesterTypeError,
    TesterCommunicationError,
)
from .misc import get_tester_inst

# TODO: need to handle disconnection if server drop the connection


def _make_tester_id(host: str, port: int) -> TesterID:
    val_bytes = f"{host}:{port}".encode("utf-8")
    return TesterID(hashlib.md5(val_bytes).hexdigest())


class Resource:
    __slots__ = ("tester", "dataset", "credentials", "notify_updates")

    def __init__(self, credentials: IProps, on_update: Callable) -> None:
        self.credentials = credentials
        self.notify_updates = on_update
        self.dataset = TesterModel(
            id=_make_tester_id(credentials.host, credentials.port),
            product=credentials.product,
            host=credentials.host,
            port=credentials.port,
            password=credentials.password,
        )
        self.tester = self.__get_tester_inst()

    def __get_tester_inst(self) -> GenericAnyTester:
        if tester_ := get_tester_inst(self.dataset):
            return tester_
        raise InvalidTesterTypeError(self.dataset)

    def on_disconnect_action(self, action: Callable) -> None:
        self.tester.on_disconnected(
            functools.partial(action, self.id)
        )

    def __updated(self) -> None:
        self.notify_updates(asdict(self.dataset))

    async def connect(self) -> bool:
        if self.tester.session.is_online:
            return False
        try:
            await self.tester
        except Exception as e:
            raise TesterCommunicationError(self.dataset, e) from None
        else:
            await self.dataset.sync(self.tester, self.__updated)
            return True

    async def disconnect(self) -> bool:
        if self.tester.session.is_online:
            await self.tester.session.logoff()
            self.tester = self.__get_tester_inst()
            return True
        self.dataset.keep_disconnected = True
        return False

    async def configure(self) -> None:
        raise NotImplementedError()

    @property
    def id(self) -> TesterID:
        return self.dataset.id

    @property
    def keep_disconnected(self) -> bool:
        return self.dataset.keep_disconnected

    @property
    def as_dict(self) -> dict[str, Any]:
        return asdict(self.dataset)
