from typing import (
    Tuple, 
    Union, 
    Iterable,
    Generator
)
from operator import attrgetter

from pydantic import (
    BaseModel, 
    validator,
    conint,
)
from . import const
from . import loop_modes

class MacAddress(str):
    def to_hexstring(self):
        return self.replace(":", "").replace("-", "").upper()

    def first_three_bytes(self):
        return self.replace(":", "").replace("-", "").upper()[:6]



class PacketSizeConfig(BaseModel):
    packet_size_type: int = 1
    packet_size: Tuple[int, ...] = tuple([64, 128, 256, 512, 1024, 1280, 1518])

    @validator("packet_size", pre=True, always=True, allow_reuse=True)
    def split_packet_size(cls, v: Union[Iterable[int], str]) -> Tuple[int, ...]:
        if isinstance(v, str):
            _v = v.replace(" ", "").split(",")
            return tuple(map(int, _v))
        return tuple(v)


class FrameLossConfig(BaseModel):
    start_rate: int = 50
    end_rate: int = 100
    step_rate: int = 50
    iterations: conint(gt=0) = 1 # type: ignore
    is_used_criteria: bool = False
    acceptable_loss: float = 0
    acceptable_loss_unit: const.AcceptableType = const.AcceptableType.PERCENT
    duration_unit: const.DurationTimeUnit = const.DurationTimeUnit.SECOND
    duration: int = 10 # seconds

    @validator("duration", pre=True, always=True, allow_reuse=True)
    def set_duration(cls, v: int, values) -> int:
        return int(
            {
                const.DurationTimeUnit.SECOND: 1,
                const.DurationTimeUnit.MINUTE: 60,
                const.DurationTimeUnit.HOUR: 3600,
                const.DurationTimeUnit.DAY: 86400,
            }[values["duration_unit"]] * v
        )
    
    @property
    def rate(self) -> range:
        return range(
            self.start_rate,
            self.end_rate + 1,
            self.step_rate,
        )

class PortConfig(BaseModel):
    transmitter: str
    receaver: str


class FrameLossModel(BaseModel):
    outer_loop_mode: const.OuterLoopMode = const.OuterLoopMode.ITERATIONS
    packet_size_cfg: PacketSizeConfig
    frame_loss: FrameLossConfig
    port_mapping: Tuple[PortConfig, ...] = tuple()
    
    def get_test_loop(self) -> Generator[loop_modes.CurrentIterProps, None, None]:
        iterations = range(self.frame_loss.iterations)
        frame_loss_rate = self.frame_loss.rate
        packet_sizes = self.packet_size_cfg.packet_size
        loop = {
            const.OuterLoopMode.PKT_SIZE: loop_modes.pkt_size,
            const.OuterLoopMode.ITERATIONS: loop_modes.iterations,
            
        }.get(self.outer_loop_mode, None)
        if loop is None:
            return
        yield from loop(iterations, packet_sizes, frame_loss_rate)


class StatisticsData(BaseModel):
    tx_packet: int = 0
    tx_mbps: int = 0
    tx_pps: int = 0
    rx_packet: int = 0
    rx_mbps: int = 0
    rx_pps: int = 0
    loss: int = 0
    loss_percent: int = 0
    fcs: int = 0

    def __add__(self, other: "StatisticsData") -> "StatisticsData":
        for name, value in self:
            setattr(self, name, value + attrgetter(name)(other))
        return self