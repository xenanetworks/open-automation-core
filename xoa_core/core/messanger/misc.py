from typing import (
    Optional,
    Protocol,
    Any,
    Dict,
    Union
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
    destenation: Optional[str] = None
    type: EMsgType = EMsgType.DATA
    payload: Any


class StatePayload(BaseModel):
    state: Optional[str]
    old_state: Optional[str]


class TransmitFunc(Protocol):
    def __call__(self, msg: Any, *, msg_type: EMsgType) -> None:
        ...


class PipeStateFacade:
    __slots__ = ("__transmit",)

    def __init__(self, transmit: "TransmitFunc") -> None:
        self.__transmit = transmit

    def __call__(self, state: Optional[str], old_state: Optional[str]) -> None:
        data = StatePayload(
            state=state,
            old_state=old_state
        )
        self.__transmit(data, msg_type=EMsgType.STATE)


class PipeFacade:
    __slots__ = ("__transmit",)

    def __init__(self, transmit: "TransmitFunc") -> None:
        self.__transmit = transmit

    # def send_data(self, data: Union[Dict, BaseModel]) -> None:
    #     self.__transmit(data, msg_type=EMsgType.DATA)

    def send_statistics(self, data: Union[Dict, BaseModel]) -> None:
        self.__transmit(data, msg_type=EMsgType.STATISTICS)

    def send_progress(self, progress: int) -> None:
        self.__transmit(progress, msg_type=EMsgType.PROGRESS)

    def send_warning(self, worning: Exception) -> None:
        self.__transmit(str(worning), msg_type=EMsgType.WARNING)

    def send_error(self, error: Exception) -> None:
        self.__transmit(str(error), msg_type=EMsgType.ERROR)
