from enum import Enum


SLEEP_SECONDS = 5


class DurationTimeUnit(Enum):
    SECOND = "seconds"
    MINUTE = "minutes"
    HOUR = "hours"
    DAY = "days"


class AcceptableType(Enum):
    PERCENT = "PERCENT"
    FRAME = "FRAME"


class StatisticsStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"


class OuterLoopMode(Enum):
    PKT_SIZE = "PACKET_SIZE"
    ITERATIONS = "ITERATIONS"
