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
    ON_PAUSE = 'ON_PAUSE'
    ON_CONTINUE = 'ON_CONTINUE'
    ON_STOP = 'ON_STOP'

    @property
    def is_pause(self) -> bool:
        return self == ExecuteEvent.PAUSE

    @property
    def is_stop(self) -> bool:
        return self == ExecuteEvent.STOP

    @property
    def is_cancel(self) -> bool:
        return self == ExecuteEvent.CANCEL

    @property
    def is_on_pause(self) -> bool:
        return self == ExecuteEvent.ON_PAUSE

    @property
    def is_on_continue(self) -> bool:
        return self == ExecuteEvent.ON_CONTINUE

    @property
    def is_on_stop(self) -> bool:
        return self == ExecuteEvent.ON_STOP


class EventFromParent(BaseModel):
    event_type: ExecuteEvent
    is_event_set: bool


class MessageFromSubProcess(BaseModel):
    msg_type: EMsgType
    msg: Any

