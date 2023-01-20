from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Type,
    Tuple,
    Optional,
)
from pydantic import BaseModel
from typing_extensions import Self
from xoa_driver import (
    enums,
    modules,
)

from .__decorator import post_notify
from .types import (
    ModuleID,
    TesterID,
)
from .port import (
    PortModel,
    PortInfoModel,
)


@dataclass
class ModuleModel:
    id: ModuleID
    index: int
    model: str
    reserved_by: str
    ports: tuple[PortModel, ...]
    name: str = " - "
    can_media_config: bool = False
    is_chimera: bool = False
    can_local_time_adjust: bool = False
    max_clock_ppm: int | None = None

    async def on_evt_reserved_by(self, _, value) -> None:
        self.reserved_by = value.username

    @classmethod
    async def from_module(cls: Type[Self], tester_id: TesterID, module: "modules.GenericAnyModule", notifier: Callable) -> Self:
        module_id = ModuleID(f"{tester_id}-{module.module_id}")
        inst = cls(
            id=module_id,
            index=module.module_id,
            model=module.info.model,
            reserved_by=module.info.reserved_by,
            **await _prepare_values(module),
            ports=tuple(
                await asyncio.gather(*[
                    PortModel.from_port(module_id, port, notifier)
                    for port in module.ports
                ])
            )
        )
        module.on_reserved_by_change(post_notify(notifier)(inst.on_evt_reserved_by))
        return inst


async def _prepare_values(module: "modules.GenericAnyModule") -> dict[str, Any]:
    m_cpb = dict()
    if not isinstance(module, (modules.ModuleL47, modules.ModuleL47VE)):
        cpb = await module.capabilities.get()
        m_cpb["can_media_config"] = cpb.can_media_config is enums.YesNo.YES
        m_cpb["is_chimera"] = cpb.is_chimera is enums.YesNo.YES
        m_cpb["can_local_time_adjust"] = cpb.can_local_time_adjust is enums.YesNo.YES
        m_cpb["max_clock_ppm"] = cpb.max_clock_ppm

    if m_name := getattr(module, "name", None):
        mn = await m_name.get()
        m_cpb["name"] = mn.name
    return m_cpb


class ModuleInfoModel(BaseModel):
    id: ModuleID
    index: int
    model: str
    reserved_by: str
    ports: Tuple[PortInfoModel, ...]
    name: str
    can_media_config: bool
    is_chimera: bool
    can_local_time_adjust: bool
    max_clock_ppm: Optional[int]
