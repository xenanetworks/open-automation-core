import functools
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from xoa_driver import utils
if TYPE_CHECKING:
    from xoa_driver import ports

from ..dataset import StatisticsData

__all__ = ("PortStatistics",)


@dataclass(init=False, repr=False)
class PortMax:
    tx_bps: int = 0
    rx_bps: int = 0
    tx_pps: int = 0
    rx_pps: int = 0
    
    def reset(self) -> None:
        for field in fields(self):
            setattr(self, field.name, 0)
    
    def __update_value(self, name: str, value: int) -> None:
        current = getattr(self, name)
        setattr(self, name, max(current, value))
    
    update_tx_bps = functools.partialmethod(__update_value, "tx_bps")
    update_rx_bps = functools.partialmethod(__update_value, "rx_bps")
    update_tx_pps = functools.partialmethod(__update_value, "tx_pps")
    update_rx_pps = functools.partialmethod(__update_value, "rx_pps")


def _bps_to_mbps(bps: int, packet_size: int) -> int:
    return int(bps * pow(10, -6) * (packet_size + 20) / packet_size)

class PortStatistics:
    __slots__ = ("__peer_tpld", "__port", "__peer_port", "max")
    
    def __init__(self, tid: int, port: "ports.GenericL23Port", peer_port: "ports.GenericL23Port") -> None:
        self.__port = port
        self.__peer_port = peer_port
        self.__peer_tpld = peer_port.statistics.rx.access_tpld(tid)
        self.max = PortMax()
    
    async def clear(self) -> None:
        await utils.apply( 
            self.__port.statistics.tx.clear.set(),  
            self.__port.statistics.rx.clear.set()
        )
        
    async def check_rx_data(self) -> bool:
        rx_data = await self.__peer_tpld.traffic.get()
        return rx_data.packet_count_since_cleared > 0
    
    async def collect_data(self, packet_size: int, is_final: bool=False) -> StatisticsData:
        # TODO: statistics need to be processed in executor
        stream_tx = self.__port.statistics.tx.obtain_from_stream(self.__port.streams.obtain(0))
        tx, rx, error, fcs = await utils.apply(
            stream_tx.get(),
            self.__peer_tpld.traffic.get(),
            self.__peer_tpld.errors.get(),
            self.__peer_port.statistics.rx.extra.get(),
        )

        tx_packet = int(tx.packet_count_since_cleared)
        rx_packet = int(rx.packet_count_since_cleared)
        
        self.max.update_tx_bps(tx.bit_count_last_sec)
        self.max.update_rx_bps(rx.bit_count_last_sec)
        self.max.update_tx_pps(tx.packet_count_last_sec)
        self.max.update_rx_pps(rx.packet_count_last_sec)

        tx_mbps = _bps_to_mbps(self.max.tx_bps, packet_size)
        rx_mbps = _bps_to_mbps(self.max.rx_bps, packet_size)
        
        loss = (
            (tx_packet - rx_packet)
            if is_final
            else int(error.swapped_seq_misorder_event_count)
        )
        fcs = fcs.fcs_error_count
        loss_percent = loss * 100 // tx_packet if tx_packet else 0
        return StatisticsData(
            tx_packet=tx_packet,
            tx_mbps=tx_mbps,
            tx_pps=self.max.tx_pps,
            rx_packet=rx_packet,
            rx_mbps=rx_mbps,
            rx_pps=self.max.rx_pps,
            loss=loss,
            loss_percent=loss_percent,
            fcs=fcs,
        )