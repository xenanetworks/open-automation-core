from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Callable,
    Optional,
    Tuple,
    Type,
)
from pydantic import BaseModel
from typing_extensions import Self
from xoa_driver import (
    enums,
    ports,
    utils,
)
from .types import ModuleID, PortID
from .__decorator import post_notify


@dataclass
class PortModel:
    id: PortID
    index: int
    model: str
    reserved_by: str
    sync_status: bool | None = None
    traffic_state: enums.TrafficOnOff | None = None
    max_speed: int | None = None
    max_speed_reduction: int | None = None
    min_interframe_gap: int | None = None
    max_interframe_gap: int | None = None
    max_streams_per_port: int | None = None
    packet_limit: int | None = None
    min_packet_length: int | None = None
    max_packet_length: int | None = None
    max_header_length: int | None = None
    max_protocol_segments: int | None = None
    max_repeat: int | None = None
    can_set_autoneg: bool = False
    can_tcp_checksum: bool = False
    can_udp_checksum: bool = False
    can_micro_tpld: bool = False
    can_mdi_mdix: bool = False
    can_sync_traffic_start: bool = False
    can_fec: bool = False
    can_anlt: bool = False
    is_chimera: bool = False
    can_brr: bool = False
    speed_modes_supported: tuple["enums.PortSpeedMode", ...] = field(default_factory=tuple)
    speed_mode_current: enums.PortSpeedMode | None = None
    speed_current: int | None = None
    speed_reduction: int | None = None

    async def on_evt_traffic_state(self, _, value) -> None:
        self.traffic_state = enums.TrafficOnOff(value.on_off)

    async def on_evt_sync_status(self, _, value) -> None:
        self.sync_status = enums.SyncStatus(value.sync_status) is enums.SyncStatus.IN_SYNC

    async def on_evt_reserved_by(self, _, value) -> None:
        self.reserved_by = value.username

    @classmethod
    async def from_port(cls: Type[Self], module_id: ModuleID, port: "ports.GenericAnyPort", notifier: Callable) -> Self:
        inst = cls(
            id=PortID(f"{module_id}-{port.kind.port_id}"),
            index=port.kind.port_id,
            model=port.info.interface,
            reserved_by=port.info.reserved_by,
            sync_status=getattr(port.info, "sync_status", None),
            traffic_state=getattr(port.info, "traffic_state", None),
            **await _prepare_values(port),
        )
        port.on_reserved_by_change(post_notify(notifier)(inst.on_evt_reserved_by))
        if on_traffic_change := getattr(port, 'on_traffic_change', None):
            on_traffic_change(post_notify(notifier)(inst.on_evt_traffic_state))
        port.on_receive_sync_change(post_notify(notifier)(inst.on_evt_sync_status))
        return inst


async def _prepare_values(port: "ports.GenericAnyPort") -> dict[str, Any]:
    p_vals = dict()
    if not isinstance(port, (ports.PortL47, ports.PortL23VE)):
        if not isinstance(port, ports.PortChimera):
            ms, cur, red, tx_pl = await utils.apply(
                port.speed.mode.selection.get(),
                port.speed.current.get(),
                port.speed.reduction.get(),
                port.tx_config.packet_limit.get()
            )
            p_vals["speed_modes_supported"] = tuple(port.info.port_possible_speed_modes)
            p_vals["speed_mode_current"] = enums.PortSpeedMode(ms.mode)
            p_vals["speed_current"] = cur.port_speed
            p_vals["speed_reduction"] = None if red.ppm == -1 else red.ppm
            p_vals["packet_limit"] = tx_pl.packet_count_limit

        cpb = port.info.capabilities
        p_vals["max_speed"] = cpb.max_speed
        p_vals["max_speed_reduction"] = cpb.max_speed_reduction
        p_vals["min_interframe_gap"] = cpb.min_interframe_gap
        p_vals["max_interframe_gap"] = cpb.max_interframe_gap
        p_vals["max_streams_per_port"] = cpb.max_streams_per_port
        p_vals["min_packet_length"] = cpb.min_packet_length
        p_vals["max_packet_length"] = cpb.max_packet_length
        p_vals["max_header_length"] = cpb.max_header_length
        p_vals["max_protocol_segments"] = cpb.max_protocol_segments
        p_vals["max_repeat"] = cpb.max_repeat
        p_vals["can_set_autoneg"] = bool(cpb.can_set_autoneg)
        p_vals["can_tcp_checksum"] = bool(cpb.can_tcp_checksum)
        p_vals["can_udp_checksum"] = bool(cpb.can_udp_checksum)
        p_vals["can_micro_tpld"] = bool(cpb.can_micro_tpld)
        p_vals["can_mdi_mdix"] = bool(cpb.can_mdi_mdix)
        p_vals["can_sync_traffic_start"] = bool(cpb.can_sync_traffic_start)
        p_vals["can_fec"] = bool(cpb.can_fec)
        p_vals["can_anlt"] = bool(cpb.can_set_link_train and cpb.can_auto_neg_base_r)
        p_vals["is_chimera"] = bool(cpb.is_chimera)
        p_vals["can_brr"] = getattr(port, "is_brr_mode_supported", False)
    return p_vals


class PortInfoModel(BaseModel):
    id: PortID
    index: int
    model: str
    reserved_by: str
    sync_status: Optional[bool]
    traffic_state: Optional[enums.TrafficOnOff]
    max_speed: Optional[int]
    max_speed_reduction: Optional[int]
    min_interframe_gap: Optional[int]
    max_interframe_gap: Optional[int]
    max_streams_per_port: Optional[int]
    packet_limit: Optional[int]
    min_packet_length: Optional[int]
    max_packet_length: Optional[int]
    max_header_length: Optional[int]
    max_protocol_segments: Optional[int]
    max_repeat: Optional[int]
    can_set_autoneg: bool
    can_tcp_checksum: bool
    can_udp_checksum: bool
    can_micro_tpld: bool
    can_mdi_mdix: bool
    can_sync_traffic_start: bool
    can_fec: bool
    can_anlt: bool
    is_chimera: bool
    can_brr: bool
    speed_modes_supported: Tuple["enums.PortSpeedMode", ...]
    speed_mode_current: Optional[enums.PortSpeedMode]
    speed_current: Optional[int]
    speed_reduction: Optional[int]
