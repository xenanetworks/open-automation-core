from typing import Callable, Optional
from enum import Enum
from functools import partialmethod


class EState(Enum):
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    RUN = "RUN"


SenderType = Callable[[Optional[str], Optional[str]], None]


def no_sender(status: Optional[str], old_status: Optional[str]) -> None:
    return None


class ExecutorState:
    __slots__ = ("__state", "__sender", "__sender_is_set")

    def __init__(self) -> None:
        self.__state = EState.STOPPED
        self.__sender = no_sender
        self.__sender_is_set = False

    def assign_senders(self, sender: "SenderType") -> None:
        if self.__sender_is_set:
            return None
        self.__sender = sender
        self.__sender_is_set = True

    @property
    def is_stoped(self) -> bool:
        return self.__state is EState.STOPPED

    @property
    def is_paused(self) -> bool:
        return self.__state is EState.PAUSED

    @property
    def is_running(self) -> bool:
        return self.__state is EState.RUN

    def __set_state(self, new_state: EState) -> None:
        self.__sender(new_state.value, self.__state.value)
        self.__state = new_state

    set_stop = partialmethod(__set_state, new_state=EState.STOPPED)
    set_run = partialmethod(__set_state, new_state=EState.RUN)
    set_pause = partialmethod(__set_state, new_state=EState.PAUSED)
