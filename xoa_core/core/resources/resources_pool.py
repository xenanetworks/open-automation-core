import collections
from functools import partial
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    Set,
)
if TYPE_CHECKING:
    from xoa_core.core.utils import observer
    from .datasets.external.tester import TesterExternalModel
from .datasets import enums
from . import misc
from . import exceptions
from . import resource


class ResourcesPool:
    __slots__ = ("__resources", "__observer",)

    def __init__(self, observer: "observer.SimpleObserver") -> None:
        self.__resources: Dict[str, "resource.Resource"] = collections.defaultdict()
        self.__observer = observer

    @property
    def avaliable_resources(self) -> Dict[str, "TesterExternalModel"]:
        return {r.id: r.as_pydantic for r in self.__resources.values()}

    @property
    def res_identifiers(self) -> Set[str]:
        return set(self.__resources.keys())

    def use_resource(self, id: str) -> Optional["resource.Resource"]:
        return self.__resources.get(id, None)

    async def suspend(self, id: str) -> None:
        if tester := self.__resources.get(id, None):
            await tester.logoff()  # After call of this function will be triggered <on_disconnected> event
        return None

    async def add(self, props: misc.IProps) -> None:
        tester = misc.get_tester_inst(props)
        if not tester:
            raise exceptions.InvalidTesterTypeError(props)
        try:
            await tester
        except Exception as e:
            raise exceptions.TesterCommunicationError(props, e)
        else:
            notifier = partial(self.__observer.emit, enums.EResourcesEvents.INFO_CHANGE_TESTER)

            res = resource.Resource(tester, notifier)
            await res.init_dataset(props.id, props.product)
            res.on_disconnect_action(self._tester_disconnected)

            self.__resources[res.id] = res
            self.__observer.emit(enums.EResourcesEvents.ADDED, res.as_pydantic)

    async def _tester_disconnected(self, id: str, *args) -> None:
        if id not in self.__resources:
            return None
        self.__resources.pop(id)
        self.__observer.emit(enums.EResourcesEvents.EXCLUDED, id)

    def __len__(self) -> int:
        return len(self.__resources)
