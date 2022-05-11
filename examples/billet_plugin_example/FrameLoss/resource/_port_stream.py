import asyncio
from xoa_driver import utils
from xoa_driver import enums

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .test_resource import TestResource
    from ..dataset import MacAddress

PPM_RATE_MULTIPLIER = 10_000

class Stream:
    __slots__ = ("__resource", "__peer_mac")
    def __init__(self, resource: "TestResource", peer_mac: "MacAddress") -> None:
        self.__resource = resource
        self.__peer_mac = peer_mac
    
    @property
    def header(self) -> str:
        """Prepare Packet Header data"""
        port_mac = self.__resource.mac_address
        return f"0x{port_mac.to_hexstring()}{self.__peer_mac.to_hexstring()}FFFF"
    
    async def setup_stream(self) -> None:
        port = self.__resource.port
        stream = await port.streams.create()
        await utils.apply(
            stream.tpld_id.set(self.__resource.tid),
            stream.packet.header.protocol.set([enums.ProtocolOption.ETHERNET]),
            stream.packet.header.data.set(self.header),
            stream.enable.set_on(),
        )
    
    async def configure_stream(self, size: int, rate: int) -> None:
        # Each port will contain only one stream but just in case we iterate through created streams
        configs = [
            utils.apply(
                stream.packet.length.set_fixed(size, size),
                stream.rate.fraction.set(rate * PPM_RATE_MULTIPLIER)
            ) for stream in self.__resource.port.streams
        ]
        await asyncio.gather(*configs)
