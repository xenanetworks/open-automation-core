import os
import typing
from .core.executors.manager import ExecutorsManager
from .core.executors.executor import SuiteExecutor

from .core.messanger.handler import OutMessagesHandler

from .core.resources.manager import (
    ResourcesManager,
    AllTesterTypes,
)
from .core.test_suites.controler import PluginController
from .core import const


if typing.TYPE_CHECKING:
    from .types import EMsgType
    from .core.messanger.misc import Message
    from .core.resources.datasets.external import credentials

T = typing.TypeVar("T", bound="MainController")


class MainController:
    """MainController - A main class of XOA-Core framework."""

    __slots__ = ("__publisher", "__resources", "suites_library", "__execution_manager",)

    def __init__(self, *, storage_path: typing.Optional[str] = None, mono: bool = False) -> None:
        """
        :param storage_path: Custom path of where to store testers information, by default is current working dirrectory
        :type storage_path: str | None
        :param mono: Flag specify if only single Test-Suite execution can be runned at the same time
        :type mono: bool
        """
        __storage_path = os.path.join(os.getcwd(), "store") if not storage_path else storage_path

        self.__publisher = OutMessagesHandler()
        resources_pipe = self.__publisher.get_pipe(const.PIPE_RESOURCES)
        self.__resources = ResourcesManager(resources_pipe, __storage_path)

        executor_pipe = self.__publisher.get_pipe(const.PIPE_EXECUTOR)
        self.__execution_manager = ExecutorsManager(executor_pipe, mono)

        self.suites_library = PluginController()

    def listen_changes(self, *names: str, _filter: typing.Optional[typing.Set["EMsgType"]] = None) -> typing.AsyncGenerator["Message", None]:
        """Subscribe to the messages from different subsystems and test-suites."""
        return self.__publisher.changes(*names, _filter=_filter)

    def __await__(self):
        return self.__setup().__await__()

    async def __setup(self: T) -> T:
        await self.__resources
        return self

    def register_lib(self, path: str) -> None:
        """Register lookup path of custom test suites library.

        :param path: lookup path of custom test suites library
        :type path: str
        """
        self.suites_library.register_path(path)

    def get_available_test_suites(self) -> typing.List[str]:
        """Get a list of available test suite names.

        :return: a list of available test suites
        :rtype: typing.List[str]
        """
        return self.suites_library.available_test_suites()

    def get_test_suite_info(self, name: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Get the info of a test suite.

        :param name: name of the test suite
        :type name: str
        """
        return self.suites_library.suite_info(name)

    async def list_testers(self) -> typing.Dict[str, "AllTesterTypes"]:
        """List the added testers.

        :return: list of testers
        :rtype: typing.Dict[str, "AllTesterTypes"]
        """
        return await self.__resources.get_all_testers()

    async def add_tester(self, credentials: "credentials.Credentials") -> bool:
        """Add a tester.

        :param credentials: tester login credentials
        :type credentials: credentials.Credentials
        :return: success or failure
        :rtype: bool
        """
        return await self.__resources.add_tester(credentials)

    async def remove_tester(self, tester_id: str) -> None:
        """Remove a tester.

        :param tester_id: tester id
        :type tester_id: str
        """
        await self.__resources.remove_tester(tester_id)

    async def connect_tester(self, tester_id: str) -> None:
        """Establis connection to a disconnected tester.

        :param tester_id: tester id
        :type tester_id: str
        """
        await self.__resources.connect(tester_id)

    async def disconnect_tester(self, tester_id: str) -> None:
        """Disconnect from a tester.

        :param tester_id: tester id
        :type tester_id: str
        """
        await self.__resources.disconnect(tester_id)

    def start_test_suite(self, test_suite_name: str, config: typing.Dict[str, typing.Any], *, debug_connection: bool = False) -> str:
        """Start test suite execution

        :param test_suite_name: test suite name
        :type test_suite_name: str
        :param config: test configuration data
        :type config: typing.Dict[str, typing.Any]
        :return: test execution id
        :rtype: str
        """
        plugin = self.suites_library.get_plugin(test_suite_name, debug_connection)
        plugin.parse_config(config)
        plugin.assign_testers(self.__resources.get_testers_by_id)
        executor = SuiteExecutor(test_suite_name)
        executor.assign_pipe(
            self.__publisher.get_pipe(executor.id)
        )
        executor.assign_plugin(plugin)
        return self.__execution_manager.run(executor)

    async def running_test_stop(self, execution_id: str) -> None:
        """Stop a test suite execution

        :param execution_id: test execution id
        :type execution_id: str
        :return: none
        :rtype: None
        """
        return await self.__execution_manager.stop(execution_id)

    async def running_test_toggle_pause(self, execution_id: str) -> None:
        """Pause or continue execution of a test suite.

        :param execution_id: test execution id
        :type execution_id: str
        :return: none
        :rtype: None
        """
        return await self.__execution_manager.toggle_pause(execution_id)
