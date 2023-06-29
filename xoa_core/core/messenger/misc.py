from __future__ import annotations
from typing import (
    Dict,
    Optional,
    Protocol,
    Any,
)
from enum import Enum
from pydantic import BaseModel

DISABLED = 1


class EMsgType(Enum):
    STATE = "STATE"
    DATA = "DATA"
    STATISTICS = "STATISTICS"
    PROGRESS = "PROGRESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Message(BaseModel):
    pipe_name: str
    meta: Dict[str, Any] = {}
    type: EMsgType = EMsgType.DATA
    payload: Any


class StatePayload(BaseModel):
    state: Optional[str]
    old_state: Optional[str]


class Progress(BaseModel):
    current: int
    total: int
    loop: int


class TransmitFunc(Protocol):
    def __call__(self, msg: Any, *, msg_type: EMsgType, **meta: Any) -> None:
        ...


class PipeStateFacade:
    __slots__ = ("__transmit",)

    def __init__(self, transmit: "TransmitFunc") -> None:
        self.__transmit = transmit

    def __call__(self, state: str | None, old_state: str | None) -> None:
        data = StatePayload(
            state=state,
            old_state=old_state
        )
        self.__transmit(data, msg_type=EMsgType.STATE)


class PipeFacade:
    __slots__ = ("__transmit", "__suite_name")

    def __init__(self, transmit: "TransmitFunc", suite_name: str) -> None:
        self.__transmit = transmit
        self.__suite_name = suite_name

    def send_statistics(self, data: dict[str, Any] | "BaseModel") -> None:
        self.__transmit(data, msg_type=EMsgType.STATISTICS, suite_name=self.__suite_name)

    def send_progress(self, current: int, total: int = 100, loop: int = 0) -> None:
        progress = Progress(
            current=current,
            total=total,
            loop=loop,
        )
        self.__transmit(progress, msg_type=EMsgType.PROGRESS, suite_name=self.__suite_name)

    def send_warning(self, warning: Exception) -> None:
        self.__transmit(str(warning), msg_type=EMsgType.WARNING, suite_name=self.__suite_name)

    def send_error(self, error: Exception) -> None:
        self.__transmit(str(error), msg_type=EMsgType.ERROR, suite_name=self.__suite_name)
