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



async def do_test(tester: types.Credentials, suite_name: str, config):
    # Create a default instance of the controller class.
    ctrl = await controller.MainController()

    # Register the plugins folder.
    ctrl.register_lib(PLUGINS_PATH)

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await ctrl.add_tester(tester)

    # get rfc2544 test suite information from the core's registration
    info = ctrl.get_test_suite_info("RFC-2544")
    if not info:
        print("Test suite is not recognized.")
        return None
    
    # convert the old config file into new config file
    new_data = converter(TestSuiteType.RFC2544, config, info["schema"])

    # you can use the config file below to start the test
    new_config = json.loads(new_data)

    # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
    execution_id = ctrl.start_test_suite(suite_name, new_config)
    
    async for msg in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(msg)


async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )
    # Convert Valkyrie test config into XOA test config and run.
    with open(TEST_CONFIG_PATH, "r") as f:
        config = json.load(f)
        await do_test(my_tester_credential, "RFC-2544", config)


if __name__ == "__main__":
    asyncio.run(main())
