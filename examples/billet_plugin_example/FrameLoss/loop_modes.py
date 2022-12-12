from typing import (
    Generator,
    NamedTuple,
)


class CurrentIterProps(NamedTuple):
    iteration_number: int
    packet_size: int
    rate: int


def iterations(iterations, packet_sizes, frame_loss_rate) -> Generator[CurrentIterProps, None, None]:
    for i in iterations:
        current_iteration_number = i + 1
        for packet_size in packet_sizes:
            for rate in frame_loss_rate:
                yield CurrentIterProps(
                    current_iteration_number,
                    packet_size,
                    rate
                )


def pkt_size(iterations, packet_sizes, frame_loss_rate) -> Generator[CurrentIterProps, None, None]:
    for packet_size in packet_sizes:
        for i in iterations:
            current_iteration_number = i + 1
            for rate in frame_loss_rate:
                yield CurrentIterProps(
                    current_iteration_number,
                    packet_size,
                    rate
                )
