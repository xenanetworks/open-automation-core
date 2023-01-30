from typing import (
    Tuple,
    Optional,
)
from pydantic import BaseModel
from xoa_driver import enums


class PortExternalModel(BaseModel):
    id: int
    model: str
    reserved_by: str
    sync_status: Optional[bool] = None
    traffic_state: Optional[enums.TrafficOnOff] = None
    max_speed: Optional[int] = None
    """max L1 Mbps, used by UI validation (Rate Cap column) & config validation"""

    max_speed_reduction: Optional[int] = None
    """max ppm value of speed reduction, used by UI validation (Speed Reduct column) & config validation"""

    min_interframe_gap: Optional[int] = None
    """used by UI validation (IFG column) & config validation"""

    max_interframe_gap: Optional[int] = None
    """used by UI validation (IFG column) & config validation"""

    max_streams_per_port: Optional[int] = None
    """used for config validation"""

    packet_limit: Optional[int] = None
    """used by UI validation (Time duration of a test iteration) & config validation"""

    min_packet_length: Optional[int] = None
    """used by UI validation & config validation"""

    max_packet_length: Optional[int] = None
    """used by UI validation & config validation"""

    max_header_length: Optional[int] = None
    """used by UI validation & config validation"""

    max_protocol_segments: Optional[int] = None
    """used by UI validation & config validation"""

    max_repeat: Optional[int] = None
    """max packet repeats for modifier, used by UI validation & config validation"""

    can_set_autoneg: bool = False
    """used by UI validation (AN column) & config validation"""

    can_tcp_checksum: bool = False
    """whether supports TCP segment with valid checksum & config validation"""

    can_udp_checksum: bool = False
    """whether supports UDP segment with valid checksum & config validation"""

    can_micro_tpld: bool = False
    """whether supports micro TPLD, used for config validation"""

    can_mdi_mdix: bool = False
    """whether supports MDI/MDIX (MDI/MDIX column), used by UI validation & config validation"""

    can_sync_traffic_start: bool = False
    """whether supports synchronized traffic start, used for config validation"""

    can_fec: bool = False
    """used by UI validation (FEC column), used by UI validation & config validation"""

    can_anlt: bool = False
    """used by UI validation (AN column), & config validation"""

    is_chimera: bool = False
    can_brr: bool = False
    """used by UI validation (BRR Column) & config validation"""

    speed_modes_supported: Tuple["enums.PortSpeedMode", ...]
    """
    corresponds to P_SPEEDS_SUPPORTED, and should be a list of enums.PortSpeedMode.
    This will be used by UI to render the items in the dropdown list for Speed selection.
    """

    speed_mode_current: Optional[enums.PortSpeedMode] = None
    """corresponds to P_SPEEDSELECTION, a single value of enums.PortSpeedMode type, showing the current speed mode."""

    speed_current: Optional[int] = None
    """corresponds to P_SPEED, a value showing the expected port speed in Mbps."""

    speed_reduction: Optional[int] = None
    """corresponds to P_SPEEDREDUCTION, a value showing the speed reduction in ppm."""
