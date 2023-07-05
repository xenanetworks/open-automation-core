from enum import Enum
from typing import Any

from pydantic import BaseModel


from xoa_core.types import EMsgType


PIPE_CLOSE = 'PIPE_CLOSE'
POLL_MESSAGE_INTERNAL = 0.01

class ExecuteEvent(Enum):
    PAUSE = 'PAUSE'
    STOP = 'STOP'
    CANCEL = 'CANCEL'

    @property
    def is_pause(self) -> bool:
        return self == ExecuteEvent.PAUSE

    @property
    def is_stop(self) -> bool:
        return self == ExecuteEvent.STOP

    @property
    def is_cancel(self) -> bool:
        return self == ExecuteEvent.CANCEL


class EventFromParent(BaseModel):
    event_type: ExecuteEvent
    is_event_set: bool


class MessageFromSubProcess(BaseModel):
    msg_type: EMsgType
    msg: Any

