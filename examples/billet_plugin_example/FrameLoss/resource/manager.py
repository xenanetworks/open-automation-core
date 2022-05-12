import asyncio
from typing import Dict, TypeVar
from xoa_driver import testers as driver_testers
from xoa_driver import modules
from .test_resource import TestResource
from .. import exceptions


T = TypeVar("T", bound="ResourcesManager")

class ResourcesManager:
    __slots__ = ("__testers", "__resources", "__port_identities", "__port_mapping")
    
    def __init__(self, testers: Dict[str, driver_testers.GenericAnyTester],  port_identities, port_mapping) -> None:
        self._validate_tester_type(testers.values(), driver_testers.L23Tester)
        self.__testers: Dict[str, driver_testers.L23Tester] = testers # type: ignore
        self.__resources: Dict[str, "TestResource"] = {}
        self.__port_identities = port_identities
        self.__port_mapping = port_mapping
    
    @staticmethod
    def _validate_tester_type(testers, valid_type) -> None:
        if not all(isinstance(t, valid_type) for t in testers):
            raise ValueError("")
    
    async def setup(self):
        await asyncio.gather(*self.__testers.values())
        for tid, (pid, port_identity) in enumerate(self.__port_identities.items()):
            module = self.__testers[port_identity.tester_id].modules.obtain(port_identity.module_index)
            if isinstance(module, modules.ModuleChimera):
                raise exceptions.WrongModuleTypeError(module)
            
            port = module.ports.obtain(port_identity.port_index)
            self.__resources[pid] = await TestResource(
                port=port,
                port_name=port_identity.name,
                tid=tid,
            )
        await self.__map_pairs()
    
    async def __map_pairs(self) -> None :
        coroutines = {
            self[port_map.transmitter].set_peer(self[port_map.receaver]) 
            for port_map in self.__port_mapping
        }
        await asyncio.gather(*coroutines)
    
    def __iter__(self):
        return iter(self.__resources.values())
    
    def __getitem__(self, key: str) -> "TestResource":
        return self.__resources[key]
    
    async def cleanup(self) -> None:
        if not self.__testers:
            return None
        await asyncio.gather(*[ resource.release() for resource in self ])
        seessions_to_close = [ 
            tester.session.logoff() for tester in self.__testers.values()
        ]
        await asyncio.gather(*seessions_to_close)
        self.__resources.clear()
        self.__testers.clear()
    
    @property
    def all_traffic_is_stop(self) -> bool:
        return all(r.traffic.is_off for r in self)
    
    @property
    def all_ports_is_sync(self) -> bool:
        return all(r.is_sync for r in self)
    
    async def set_time_limit(self, duration_sec: int) -> None:
        await asyncio.gather(*[r.traffic.set_time_duration(duration_sec) for r in self if r.is_tx])
    
    async def get_time_elipsed(self) -> int:
        return max(await asyncio.gather(*[r.traffic.get_time_elipsed() for r in self if r.is_tx]))
    
    async def set_frame_limit(self, max_frames: int) -> None:
        await asyncio.gather(*[r.traffic.set_frame_duration(max_frames) for r in self if r.is_tx])
    
    async def start_traffic(self) -> None:
        await asyncio.gather(*[r.traffic.start() for r in self if r.is_tx])
    
    async def stop_traffic(self) -> None:
        await asyncio.gather(*[r.traffic.stop() for r in self if r.is_tx])
    
    async def clear_statistic_counters(self) -> None:
        await asyncio.gather(*[r.clear() for r in self])
        while not self.all_ports_is_sync:
            await asyncio.sleep(0.01)
    
    async def prepare_streams(self) -> None:
        await asyncio.gather(*[r.stream.setup_stream() for r in self if r.is_tx])
    
    async def update_streams(self, packet_size: int, rate: int) -> None:
        await asyncio.gather(*[r.stream.configure_stream(packet_size, rate) for r in self if r.is_tx])