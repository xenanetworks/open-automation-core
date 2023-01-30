import functools
from typing import TYPE_CHECKING, Callable
from dataclasses import asdict
if TYPE_CHECKING:
    from xoa_driver import testers
    from .datasets import enums
from .datasets.internal.tester import TesterModel
from .datasets.internal.credentials import CredentialsModel
from .datasets.external.tester import TesterExternalModel


class Resource:
    __slots__ = ("tester", "dataset", "notify_updates",)

    def __init__(self, tester: "testers.GenericAnyTester", on_update: Callable) -> None:
        self.tester = tester
        self.notify_updates = on_update

    async def init_dataset(self, id: str, product_type: "enums.EProductType") -> None:
        self.dataset = await TesterModel.from_tester(id, product_type, self.tester, self.__updated)

    def on_disconnect_action(self, action: Callable) -> None:
        self.tester.on_disconnected(
            functools.partial(action, self.id)
        )

    def __updated(self) -> None:
        self.notify_updates(TesterExternalModel.construct(**asdict(self.dataset)))

    async def logoff(self) -> None:
        await self.tester.session.logoff()

    @property
    def id(self) -> str:
        return self.dataset.id

    @property
    def as_pydantic(self) -> TesterExternalModel:
        return TesterExternalModel.construct(**asdict(self.dataset))

    @property
    def credentials(self) -> CredentialsModel:
        return CredentialsModel.construct(**asdict(self.dataset))
