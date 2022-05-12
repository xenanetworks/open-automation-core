from typing import (
    Tuple,
    Optional,
    Callable,
    TypeVar,
    Type,
    Dict,
    Any,
)
from dataclasses import dataclass, field
from xoa_driver import ports
from xoa_driver import enums
from xoa_driver import utils

from xoa_core.core.utils import decorators

P = TypeVar("P", bound="PortModel")

@dataclass
class PortModel:
    id: int
    model: str
    reserved_by: str
    sync_status: Optional[bool] = None
    traffic_state: Optional[enums.TrafficOnOff] = None
    max_speed: Optional[int] = None # max L1 Mbps, used by UI validation (Rate Cap column) & config validation
    max_speed_reduction: Optional[int] = None # max ppm value of speed reduction, used by UI validation (Speed Reduct column) & config validation
    min_interframe_gap: Optional[int] = None # used by UI validation (IFG column) & config validation
    max_interframe_gap: Optional[int] = None # used by UI validation (IFG column) & config validation
    max_streams_per_port: Optional[int] = None # used for config validation
    packet_limit: Optional[int] = None # used by UI validation (Time duration of a test iteration) & config validation
    min_packet_length: Optional[int] = None # used by UI validation & config validation
    max_packet_length: Optional[int] = None # used by UI validation & config validation
    max_header_length: Optional[int] = None # used by UI validation & config validation
    max_protocol_segments: Optional[int] = None # used by UI validation & config validation
    max_repeat: Optional[int] = None # max packet repeats for modifier, used by UI validation & config validation
    can_set_autoneg: bool = False # used by UI validation (AN column) & config validation
    can_tcp_checksum: bool = False # whether supports TCP segment with valid checksum & config validation
    can_udp_checksum: bool = False # whether supports UDP segment with valid checksum & config validation
    can_micro_tpld: bool = False # whether supports micro TPLD, used for config validation
    can_mdi_mdix: bool = False # whether supports MDI/MDIX (MDI/MDIX column), used by UI validation & config validation
    can_sync_traffic_start: bool = False # whether supports synchronized traffic start, used for config validation
    can_fec: bool = False # used by UI validation (FEC column), used by UI validation & config validation
    can_anlt: bool = False # used by UI validation (AN column), & config validation
    is_chimera: bool = False 
    can_brr: bool = False # used by UI validation (BRR Column) & config validation
    speed_modes_supported: Tuple["enums.PortSpeedMode", ...] = field(default_factory=tuple) # corresponds to P_SPEEDS_SUPPORTED, and should be a list of enums.PortSpeedMode. This will be used by UI to render the items in the dropdown list for Speed selection.
    speed_mode_current: Optional[enums.PortSpeedMode] = None # corresponds to P_SPEEDSELECTION, a single value of enums.PortSpeedMode type, showing the current speed mode.
    speed_current: Optional[int] = None # corresponds to P_SPEED, a value showing the expected port speed in Mbps.
    speed_reduction: Optional[int] = None # corresponds to P_SPEEDREDUCTION, a value showing the speed reduction in ppm.
    
    
    async def on_evt_traffic_state(self, _, value) -> None:
        self.traffic_state = enums.TrafficOnOff(value.on_off)
    
    async def on_evt_sync_status(self, _, value) -> None:
        self.sync_status = enums.SyncStatus(value.sync_status) is enums.SyncStatus.IN_SYNC
    
    async def on_evt_reserved_by(self, _, value) -> None:
        self.reserved_by = value.username
    
    @classmethod
    async def from_port(cls: Type[P], port: "ports.GenericAnyPort", notifier: Callable) -> P:
        inst = cls(
            id = port.kind.port_id,
            model = port.info.interface,
            reserved_by = port.info.reserved_by,
            sync_status = getattr(port.info, "sync_status", None),
            traffic_state = getattr(port.info, "traffic_state", None),
            **await _prepare_values(port),
        )
        port.on_reserved_by_change(decorators.post_notify(notifier)(inst.on_evt_reserved_by))
        if on_traffic_change := getattr(port, 'on_traffic_change', None):
            on_traffic_change(decorators.post_notify(notifier)(inst.on_evt_traffic_state))
        port.on_receive_sync_change(decorators.post_notify(notifier)(inst.on_evt_sync_status))
        return inst



async def _prepare_values(port: "ports.GenericAnyPort") -> Dict[str, Any]:
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
        p_vals["can_anlt"] = cpb.can_set_link_train and cpb.can_auto_neg_base_r
        p_vals["is_chimera"] = bool(cpb.is_chimera)
        p_vals["can_brr"] = getattr(port, "is_brr_mode_supported", False)
    return p_vals