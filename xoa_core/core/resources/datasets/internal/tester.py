import asyncio
from typing import (
    TYPE_CHECKING,
    Tuple,
    Callable,
    TypeVar,
    Type,
)
from pydantic import SecretStr
from dataclasses import dataclass, field
if TYPE_CHECKING:
    from xoa_driver import testers
from xoa_driver import utils
from xoa_core.core.utils import decorators
from xoa_core.core.resources.datasets import enums
from .module import ModuleModel

T = TypeVar("T", bound="TesterModel")


@dataclass
class TesterModel:
    product: enums.EProductType
    host: str
    port: int
    password: SecretStr
    name: str = " - "
    reserved_by: str = ""
    is_connected: bool = False
    modules: Tuple[ModuleModel, ...] = field(default_factory=tuple)
    id: str = None  # type: ignore
    keep_disconnected: bool = False
    max_name_len: int = 0
    max_comment_len: int = 0
    max_password_len: int = 0

    async def on_evt_reserved_by(self, _, value) -> None:
        self.reserved_by = value.username

    async def on_evt_disconnected(self, *_) -> None:
        self.is_connected = False
        self.modules = tuple()

    @classmethod
    async def from_tester(cls: Type[T], resource_id: str, product: "enums.EProductType", tester: "testers.GenericAnyTester", notifier: Callable) -> T:
        tn, cpb = await utils.apply(
            tester.name.get(),
            tester.capabilities.get()
        )
        inst = cls(
            id=resource_id,
            product=product,
            host=tester.info.host,
            port=tester.info.port,
            password=SecretStr(tester.session.pwd),
            name=str(tn.chassis_name),
            reserved_by=tester.info.reserved_by,
            is_connected=tester.session.is_online,
            keep_disconnected=False,
            max_name_len=cpb.max_name_len,
            max_comment_len=cpb.max_name_len,
            max_password_len=cpb.max_name_len,
            modules=tuple(
                await asyncio.gather(*[
                    ModuleModel.from_module(module, notifier)
                    for module in tester.modules
                ])
            )
        )
        tester.on_reserved_by_change(decorators.post_notify(notifier)(inst.on_evt_reserved_by))
        tester.on_disconnected(decorators.post_notify(notifier)(inst.on_evt_disconnected))
        return inst
