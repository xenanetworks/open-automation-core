import asyncio
from typing import (
    TYPE_CHECKING, 
    Dict, 
    Any
)
if TYPE_CHECKING:
    from .resource.manager import ResourcesManager
from . import const
from . import exceptions
from .dataset import StatisticsData

class StatisticsProcessor:
    __slots__ = ("is_used_criteria", "acceptable_loss_unit", "acceptable_loss", "__resources", )
    
    def __init__(self, resources: "ResourcesManager", is_used_criteria: bool, acceptable_loss_unit: "const.AcceptableType", acceptable_loss: float) -> None:
        self.is_used_criteria = is_used_criteria
        self.acceptable_loss_unit = acceptable_loss_unit
        self.acceptable_loss = acceptable_loss
        
        self.__resources = resources

    async def check_rx_data(self) -> None:
        if not all(await asyncio.gather(*[r.statistics.check_rx_data() for r in self.__resources])):
            raise exceptions.NoRxDataError()

    def check_statistic_status(self, statistics:  "StatisticsData", is_final: bool = False) -> const.StatisticsStatus:
        statistic_status = const.StatisticsStatus.SUCCESS if is_final else const.StatisticsStatus.PENDING
        frame_bool = self.acceptable_loss_unit == const.AcceptableType.FRAME and statistics.loss > self.acceptable_loss
        percentage_bool = statistics.loss_percent > self.acceptable_loss
        if (self.is_used_criteria and (frame_bool or percentage_bool)) or statistics.loss > 0:
            return const.StatisticsStatus.FAIL
        return statistic_status
    
    async def collect_data(self, iteration: int, packet_size: int, rate: int, is_final=False) -> Dict[str, Any]:
        total = StatisticsData()
        row_data = {
            "iteration": iteration,
            "packet_size": packet_size,
            "rate": rate,
            "total": total,
            "status": const.StatisticsStatus.PENDING,
        }
        for resource in self.__resources:
            statistics = await resource.statistics.collect_data(packet_size, is_final)
            total += statistics
            row_data[resource.port_name] = statistics
        
        total.loss_percent = int(total.loss * 100 / total.tx_packet) if total.tx_packet else 0
        row_data["total"] = total
        row_data["status"] = self.check_statistic_status(total, is_final)
        return row_data
    
    def reset_max(self) -> None:
        for r in self.__resources:
            r.statistics.max.reset()
