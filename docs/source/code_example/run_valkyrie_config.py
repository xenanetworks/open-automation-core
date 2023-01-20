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
OLD_CONFIG_FILE = BASE_PATH / "my2544_data.v2544" 

CHASSIS_IP = "10.10.10.10"
TEST_SUITE_REG_NAME = "RFC-2544"

async def main() -> None:
    # Define your tester login credentials
    tester_cred = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host=CHASSIS_IP
    )

    # Create a default instance of the controller class.
    ctrl = await controller.MainController()

    # Register the plugins folder.
    ctrl.register_lib(str(PLUGINS_PATH))

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await ctrl.add_tester(tester_cred)

    # convert the old config file into new config file
    with open(OLD_CONFIG_FILE, "r") as f:
        old_data = f.read()

        # get rfc2544 test suite information from the core's registration
        info = ctrl.get_test_suite_info(TEST_SUITE_REG_NAME)
        if not info:
            print("Test suite is not recognized. Check its registration name in the meta.yml file.")
            return None

        # convert old data into new data
        new_data = converter(TestSuiteType.RFC2544, old_data, info["schema"])

        # save new data in xoa json
        with open(TEST_CONFIG_PATH, "w") as f:
            f.write(new_data)

        # from json string to Python dict
        new_config = json.loads(new_data)

        # start the test and get test id
        test_id = ctrl.start_test_suite(TEST_SUITE_REG_NAME, new_config)

        # subscribe to statistics of the test
        async for msg in ctrl.listen_changes(test_id, _filter={types.EMsgType.STATISTICS}):
            print(msg)


if __name__ == "__main__":
    asyncio.run(main())
