from enum import (
    IntEnum,
    auto,
)


class EProductType(IntEnum):
    VALKYRIE = 1
    VULKAN = 2
    SAFIRE = 3
    VANTAGE = 4
    CHIMERA = 5


class EResourcesEvents(IntEnum):
    ADDED = auto()
    EXCLUDED = auto()
    INFO_CHANGE_TESTER = auto()
    INFO_CHANGE_MODULE = auto()
    INFO_CHANGE_PORT = auto()
    ERROR = auto()
