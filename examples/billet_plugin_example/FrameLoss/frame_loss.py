import typing
from xoa_core.types import PluginAbstract
if typing.TYPE_CHECKING:
    from .dataset import FrameLossModel  # noqa: F401

from . import const
from .resource.manager import ResourcesManager
from .test_manager import L23TestManager
from .statistics import StatisticsProcessor


class FrameLossTest(PluginAbstract["FrameLossModel"]):
    __slots__ = ("resources", "statistics")

    def prepare(self) -> None:
        self.resources = ResourcesManager(
            self.testers,
            self.port_identities,
            self.cfg.port_mapping
        )
        self.statistics = StatisticsProcessor(
            self.resources,
            self.cfg.frame_loss.is_used_criteria,
            self.cfg.frame_loss.acceptable_loss_unit,
            self.cfg.frame_loss.acceptable_loss
        )

    def calc_progress(self, current_packet_size: int, current_itteration: int) -> int:
        iterations = self.cfg.frame_loss.iterations
        packet_sizes = self.cfg.packet_size_cfg.packet_size
        current = (packet_sizes.index(current_packet_size) + 1) + len(packet_sizes) * (current_itteration - 1)
        total = len(packet_sizes) * iterations
        return current * 100 // total

    async def mac_lerning_frame(self, test: "L23TestManager") -> None:
        await self.resources.update_streams(
            self.cfg.packet_size_cfg.packet_size[0],
            self.cfg.frame_loss.start_rate
        )
        async for _ in test.generate_traffic(const.SLEEP_SECONDS):
            ...
        await self.statistics.check_rx_data()

    async def start(self) -> None:
        async with L23TestManager(self.resources) as test:
            await self.mac_lerning_frame(test)

            for current_props in self.cfg.get_test_loop():
                await self.state_conditions.wait_if_paused()
                await self.state_conditions.stop_if_stopped()

                await self.resources.update_streams(
                    current_props.packet_size,
                    current_props.rate
                )
                self.statistics.reset_max()
                async for duration_progress in test.generate_traffic(self.cfg.frame_loss.duration):
                    temporal_result = await self.statistics.collect_data(*current_props)
                    temporal_result["progress"] = duration_progress
                    self.xoa_out.send_statistics(temporal_result)
                final_result = await self.statistics.collect_data(*current_props, is_final=True)
                final_result["progress"] = 100

                self.xoa_out.send_statistics(final_result)
                self.xoa_out.send_progress(  # not verry accurate, but for demo will work
                    self.calc_progress(
                        current_props.packet_size,
                        current_props.iteration_number
                    )
                )
