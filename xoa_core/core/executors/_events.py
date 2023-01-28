from enum import (
    IntEnum,
    auto,
)


class Event(IntEnum):
    STOPPED = auto()
    ERROR = auto()
