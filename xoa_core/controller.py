from __future__ import annotations

import typing
from pathlib import Path

from typing_extensions import Self

from .core import const
from .core.executors.executor import SuiteExecutor
from .core.executors.manager import ExecutorsManager
from .core.messenger.handler import OutMessagesHandler
from .core.messenger.misc import Message
from .core.resources.controller import ResourcesController
from .core.resources.storage import PrecisionStorage
from .core.resources.types import Credentials, TesterInfoModel
from .core.test_suites.controller import PluginController
from .types import TesterID

if typing.TYPE_CHECKING:
    from .types import EMsgType


class MainController:
    """MainController - A main class of XOA-Core framework."""

    __slots__ = ("__is_started", "__publisher", "__resources", "suites_library", "__execution_manager")

    def __init__(self, *, storage_path: Path | str | None = None, mono: bool = False) -> None:
        self.__is_started = False
        __storage_path = Path.cwd() / "store" if not storage_path else Path(storage_path)

        self.__publisher = OutMessagesHandler()
        resources_pipe = self.__publisher.get_pipe(const.PIPE_RESOURCES)
        storage = PrecisionStorage(str(__storage_path))
        self.__resources = ResourcesController(resources_pipe, storage)

        executor_pipe = self.__publisher.get_pipe(const.PIPE_EXECUTOR)
        self.__execution_manager = ExecutorsManager(executor_pipe, mono)

        self.suites_library = PluginController()

    def listen_changes(self, *names: str, _filter: set["EMsgType"] | None = None) -> typing.AsyncGenerator[Message, None]:
        """Subscribe to the messages from different subsystems and test-suites."""
        return self.__publisher.changes(*names, _filter=_filter)

    def __await__(self) -> typing.Generator[typing.Any, None, Self]:
        return self.__setup().__await__()

    async def __setup(self) -> Self:
        if not self.__is_started:
            await self.__resources.start()
            self.__is_started = True
        return self

    def register_lib(self, path: str | Path) -> None:
        """Register lookup path of custom test suites library.

        :param path: lookup path of custom test suites library
        :type path: str | Path
        """
        self.suites_library.register_path(path)

    def get_available_test_suites(self) -> list[str]:
        """Get a list of available test suite names.

        :return: a list of available test suites
        :rtype: list[str]
        """
        return self.suites_library.available_test_suites()

    def get_test_suite_info(self, name: str) -> dict[str, typing.Any] | None:
        """Get the info of a test suite.

        :param name: name of the test suite
        :type name: str

        :return: dict of testsuite info or None
        :rtype: dict[str, typing.Any] | None
        """
        return self.suites_library.suite_info(name)

    async def list_testers_info(self) -> list[TesterInfoModel]:
        """List of info of known testers.

        :return: list of testers
        :rtype: list["TesterInfoModel"]
        """
        return await self.__resources.list_testers_info()

    async def get_tester_info(self, tester_id: TesterID) -> TesterInfoModel | None:
        """Info of an tester.

        :return: tester info
        :rtype: "TesterInfoModel"
        """
        return await self.__resources.get_tester_info(tester_id)

    async def add_tester(self, credentials: Credentials) -> TesterID:
        """Add a tester.

        :param credentials: tester login credentials
        :type credentials: credentials.Credentials
        :return: success or failure
        :rtype: bool
        """
        return await self.__resources.add_tester(credentials)

    async def remove_tester(self, tester_id: TesterID) -> None:
        """Remove a tester.

        :param tester_id: tester id
        :type tester_id: TesterID
        """
        await self.__resources.remove_tester(tester_id)

    async def connect_tester(self, tester_id: TesterID) -> None:
        """Establis connection to a disconnected tester.

        :param tester_id: tester id
        :type tester_id: TesterID
        """
        await self.__resources.connect(tester_id)

    async def disconnect_tester(self, tester_id: TesterID) -> None:
        """Disconnect from a tester.

        :param tester_id: tester id
        :type tester_id: TesterID
        """
        await self.__resources.disconnect(tester_id)

    def start_test_suite(self, test_suite_name: str, config: dict[str, typing.Any], *, debug_connection: bool = False) -> str:
        """Start test suite execution

        :param test_suite_name: test suite name
        :type test_suite_name: str
        :param config: test configuration data
        :type config: dict[str, typing.Any]
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
