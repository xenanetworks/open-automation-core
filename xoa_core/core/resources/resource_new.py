import functools
from typing import TYPE_CHECKING, Callable
from dataclasses import asdict
if TYPE_CHECKING:
    from xoa_driver import testers
    from .datasets import enums
from .datasets.internal.tester import TesterModel
from .datasets.internal.credentials import CredentialsModel
from .datasets.external.tester import TesterExternalModel
from .types import TesterID
from .exceptions import (
    InvalidTesterTypeError,
    TesterCommunicationError,
)
from .misc import get_tester_inst


class Resource:
    __slots__ = ("tester", "dataset", "credentials", "notify_updates")

    def __init__(self, credentials: CredentialsModel, on_update: Callable) -> None:
        if tester_ := get_tester_inst(credentials):
            self.tester = tester_
        else:
            raise InvalidTesterTypeError(credentials)
        self.credentials = credentials
        self.notify_updates = on_update

    async def init_dataset(self) -> None:
        try:
            await self.tester
        except Exception as e:
            raise TesterCommunicationError(self.credentials, e) from None
        self.dataset = await TesterModel.from_tester(
            self.credentials.id,
            self.credentials.product,
            self.tester,
            self.__updated
        )

    def on_disconnect_action(self, action: Callable) -> None:
        self.tester.on_disconnected(
            functools.partial(action, self.id)
        )

    def __updated(self) -> None:
        self.notify_updates(TesterExternalModel.construct(**asdict(self.dataset)))

    async def logoff(self) -> None:
        await self.tester.session.logoff()

    @property
    def id(self) -> TesterID:
        return self.dataset.id

    @property
    def as_pydantic(self) -> TesterExternalModel:
        return TesterExternalModel.parse_obj(self.dataset)
