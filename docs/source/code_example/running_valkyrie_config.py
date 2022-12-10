from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
from pathlib import Path
import asyncio
import json
from xoa_converter.entry import converter
from xoa_converter.types import TestSuiteType

BASE_PATH = Path.cwd()
PLUGINS_PATH = BASE_PATH / "pluginlib"
TEST_CONFIG_PATH = BASE_PATH / "my2544_data.json"
OLD_CONFIG_FILE = BASE_PATH / "my_old2544_config.v2544" 
T_SUITE_NAME = "RFC-2544"

async def listen_messages(ctrl: controller.MainController, identifier: str, filter: set[types.EMsgType] | None = None) -> None:
    async for msg in ctrl.listen_changes(identifier, _filter=filter):
        print(msg)


async def main() -> None:
    # Create a default instance of the controller class.
    c = await controller.MainController()

    # Register the plugins folder.
    c.register_lib(str(PLUGINS_PATH))

    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40",
        password="xena"
    )

    # Subscribe to all message from test resources.
    asyncio.create_task(listen_messages(c, types.PIPE_RESOURCES))

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await c.add_tester(my_tester_credential)

    # Get currently available test suites names
    print(c.get_available_test_suites())

    # Convert Valkyrie test config into XOA test config and run.
    with open(TEST_CONFIG_PATH, "r") as f:
        config = json.load(f)

        # get rfc2544 test suite information from the core's registration
        info = c.get_test_suite_info(T_SUITE_NAME)
        if not info:
            print("Test suite is not recognized.")
            return None
        
        # convert the old config file into new config file
        new_data = converter(TestSuiteType.RFC2544, config, info["schema"])

        # you can use the config file below to start the test
        new_config = json.loads(new_data)

        # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
        test_id = c.start_test_suite("RFC-2544", new_config)

        # Subscribe to statistic messages.
        await listen_messages(c, test_id, {types.EMsgType.STATISTICS})


if __name__ == "__main__":
    asyncio.run(main())
