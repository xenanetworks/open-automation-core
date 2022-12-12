from __future__ import annotations

import asyncio
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Callable,
    Tuple,
)

from pydantic import (
    BaseModel,
    SecretStr,
)
if TYPE_CHECKING:
    from xoa_driver import testers

from xoa_driver import utils

from .__decorator import post_notify
from .module import (
    ModuleModel,
    ModuleInfoModel,
)
from .types import (
    EProductType,
    TesterID,
)


@dataclass
class TesterModel:
    id: TesterID
    product: EProductType
    host: str
    port: int
    password: SecretStr
    index: int | None = None  # Will be populated in pool
    name: str = " - "
    reserved_by: str = ""
    is_connected: bool = False
    modules: tuple[ModuleModel, ...] = field(default_factory=tuple)
    keep_disconnected: bool = False
    max_name_len: int = 0
    max_comment_len: int = 0
    max_password_len: int = 0

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
                ModuleModel.from_module(self.id, module, notifier)
                for module in tester.modules
            ])
        )

        tester.on_reserved_by_change(post_notify(notifier)(self.on_evt_reserved_by))
        tester.on_disconnected(self.on_evt_disconnected)


class TesterInfoModel(BaseModel):
    id: TesterID
    index: int
    product: EProductType
    host: str
    port: int
    password: SecretStr
    name: str
    reserved_by: str
    is_connected: bool
    modules: Tuple[ModuleInfoModel, ...] = tuple()
    keep_disconnected: bool
    max_name_len: int
    max_comment_len: int
    max_password_len: int
