from __future__ import annotations

import asyncio
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Callable,
    NewType,
)

from pydantic import SecretStr

if TYPE_CHECKING:
    from xoa_driver import testers

from xoa_driver import utils

from xoa_core.core.resources.datasets import enums
from xoa_core.core.resources.resource.models import __decorator as decorator

from .module import ModuleModel


TesterID = NewType("TesterID", str)


@dataclass
class TesterModel:
    id: TesterID
    product: enums.EProductType
    host: str
    port: int
    password: SecretStr
    name: str = " - "
    reserved_by: str = ""
    is_connected: bool = False
    modules: tuple[ModuleModel, ...] = field(default_factory=tuple)
    keep_disconnected: bool = False
    max_name_len: int = 0  # used by UI validation (Tester Name) & config validation
    max_comment_len: int = 0  # used by UI validation (Tester Description) & config validation
    max_password_len: int = 0  # used by UI validation (Tester Password) & config validation

    async def on_evt_reserved_by(self, _, value) -> None:
        self.reserved_by = value.username

    async def on_evt_disconnected(self, *_) -> None:
        self.is_connected = False
        self.modules = tuple()

    async def sync(self, tester: "testers.GenericAnyTester", notifier: Callable) -> None:
        tn, cpb = await utils.apply(
            tester.name.get(),
            tester.capabilities.get()
        )

        self.name = str(tn.chassis_name)
        self.reserved_by = tester.info.reserved_by
        self.is_connected = tester.session.is_online
        self.keep_disconnected = False
        self.max_name_len = cpb.max_name_len
        self.max_comment_len = cpb.max_name_len
        self.max_password_len = cpb.max_name_len
        self.modules = tuple(
            await asyncio.gather(*[
                ModuleModel.from_module(module, notifier)
                for module in tester.modules
            ])
        )

        tester.on_reserved_by_change(decorator.post_notify(notifier)(self.on_evt_reserved_by))
        tester.on_disconnected(self.on_evt_disconnected)
