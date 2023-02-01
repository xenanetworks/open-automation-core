import typing
if typing.TYPE_CHECKING:
    from xoa_driver import ports
from xoa_driver import enums

MICROSECONDS_RATIO = 1e+6


class Traffic:
    __slots__ = ("__port", "__status")

    def __init__(self, port: "ports.GenericL23Port") -> None:
        self.__port = port
        self.__status = enums.TrafficOnOff(port.info.traffic_state)

        port.on_traffic_change(self.__on_traffic_state)

    async def __on_traffic_state(self, port: "ports.GenericL23Port", v) -> None:
        self.__status = enums.TrafficOnOff(v.on_off)

    @property
    def is_off(self) -> bool:
        return self.__status is enums.TrafficOnOff.OFF

    async def set_time_duration(self, duration_sec: int) -> None:
        await self.__port.tx_config.time_limit.set(int(duration_sec * MICROSECONDS_RATIO))

    async def get_time_elipsed(self) -> int:
        return int((await self.__port.tx_config.time.get()).microseconds / MICROSECONDS_RATIO)

    async def set_frame_duration(self, packets_limit: int) -> None:
        await self.__port.tx_config.packet_limit.set(packets_limit)

    async def start(self) -> None:
        await self.__port.traffic.state.set_start()

    async def stop(self) -> None:
        await self.__port.traffic.state.set_stop()
