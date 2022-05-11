import asyncio

from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from xoa_driver import ports

from xoa_driver import utils
from xoa_driver import enums
from ._port_stream import Stream
from ._port_statistics import PortStatistics
from ._traffic import Traffic
from ..dataset import MacAddress



class TestResource:
    __slots__ = ("port", "mode", "port_name", "tid",  "stream", "statistics", "mac_address", "traffic", "__reservation_status", "__traffic_status", "__sync_status")
    
    def __init__(self, port: "ports.GenericL23Port", port_name: str,  tid: int = 0) -> None:
        self.mode = 0x01
        self.port = port
        self.port_name = port_name
        self.tid = tid
        
        self.traffic = Traffic(port)
        self.__sync_status = enums.SyncStatus(self.port.info.sync_status)
        self.__reservation_status = enums.ReservedStatus(self.port.info.reservation)

        self.port.on_reservation_change(self.__on_reservation_status)
        self.port.on_receive_sync_change(self.__on_sync_change)
    
    async def __on_sync_change(self, port, v) -> None:
        self.__sync_status = enums.SyncStatus(v.sync_status)
    
    async def __on_reservation_status(self, port: "ports.GenericL23Port", v) -> None:
        self.__reservation_status = enums.ReservedStatus(v.status)
    
    def __await__(self):
        return self.__prepare().__await__()
    
    async def __prepare(self):
        await self.reserve()
        mac = await self.port.net_config.mac_address.get()
        self.mac_address = MacAddress(mac.mac_address)
        return self
    
    @property
    def is_sync(self) -> bool:
        return self.__sync_status is enums.SyncStatus.IN_SYNC
    
    @property
    def is_tx(self) -> bool:
        return bool(self.mode & 0x10)
    
    async def clear(self) -> None:
        await utils.apply( 
            self.port.statistics.tx.clear.set(),  
            self.port.statistics.rx.clear.set()
        )
    
    async def set_peer(self, peer: "TestResource") -> None:
        self.mode |= 0x10
        self.stream = Stream(self, peer.mac_address)
        self.statistics = PortStatistics(self.tid, self.port, peer.port)
        await self.stream.setup_stream()
    
    async def reserve(self) -> None:
        if self.__reservation_status is enums.ReservedStatus.RESERVED_BY_OTHER:
            await self.port.reservation.set_relinquish()
            while self.__reservation_status is not enums.ReservedStatus.RELEASED:
                await asyncio.sleep(0.01)
        await utils.apply(
            self.port.reservation.set_reserve(),
            self.port.reset.set()
        )
    
    async def release(self) -> None:
        await utils.apply(
            self.port.reset.set(),
            self.port.reservation.set_release(),
        )