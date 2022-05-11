import os
import typing
from .core.executors.manager import ExecutorsManager
from .core.executors.executor import SuiteExecutor

from .core.messanger.handler import OutMessagesHandler
from .core.resources.manager import ResourcesManager, AllTesterTypes
from .core.test_suites.controler import PluginController

from .core import const


if typing.TYPE_CHECKING:
    from .types import EMsgType
    from .core.resources.datasets.external import credentials

T = typing.TypeVar("T", bound="MainController")

class MainController:
    __slots__ = ("__publisher", "__resources", "suites_library", "__execution_manager")

    def __init__(self, *, storage_path: typing.Optional[str] = None, mono: bool = False) -> None:
        __storage_path = os.path.join(os.getcwd(), "store") if not storage_path else storage_path

        self.__publisher = OutMessagesHandler()
        resources_pipe = self.__publisher.get_pipe(const.PIPE_RESOURCES)
        self.__resources = ResourcesManager(resources_pipe, __storage_path)

        executor_pipe = self.__publisher.get_pipe(const.PIPE_EXECUTOR)
        self.__execution_manager = ExecutorsManager(executor_pipe, mono)
        
        self.suites_library = PluginController()


    def listen_changes(self, *names: str, _filter: typing.Optional[typing.Set["EMsgType"]] = None):
        return self.__publisher.changes(*names, _filter=_filter)

    def __await__(self):
        return self.__setup().__await__()

    async def __setup(self: T) -> T:
        await self.__resources
        return self

    def register_lib(self, path: str) -> None:
        """Register lookup path of custom Test Suites librarry"""
        self.suites_library.register_path(path)


    def get_avaliable_test_suites(self) -> typing.List[str]:
        return self.suites_library.avaliable_test_suites()

    def get_test_suite_info(self, name: str):
        return self.suites_library.suite_info(name)

    async def list_testers(self) -> typing.Dict[str, "AllTesterTypes"]:
        return await self.__resources.get_all_testers()

    async def add_tester(self, credentials: "credentials.Credentials") -> bool:
        return await self.__resources.add_tester(credentials)

    async def remove_tester(self, tester_id: str) -> None:
        await self.__resources.remove_tester(tester_id)

    async def connect_tester(self, tester_id: str) -> None:
        await self.__resources.connect(tester_id)

    async def disconnect_tester(self, tester_id: str) -> None:
        await self.__resources.disconnect(tester_id)

    def start_test_suite(self, test_suite_name: str, config: typing.Dict[str, typing.Any]) -> str:
        plugin = self.suites_library.get_plugin(test_suite_name, False)
        plugin.parse_config(config)
        plugin.assign_testers(self.__resources.get_testers_by_id)
        executor = SuiteExecutor(test_suite_name)
        executor.assign_pipe(
            self.__publisher.get_pipe(executor.id)
        )
        executor.assign_plugin(plugin)
        return self.__execution_manager.run(executor)

    async def running_test_stop(self, execution_id: str) -> None:
        return await self.__execution_manager.stop(execution_id)

    async def running_test_toggle_pause(self, execution_id: str) -> None:
        return await self.__execution_manager.toggle_pause(execution_id)