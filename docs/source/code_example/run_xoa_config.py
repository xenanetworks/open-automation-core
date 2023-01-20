from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
from pathlib import Path
import asyncio
import json



BASE_PATH = Path.cwd()
PLUGINS_PATH = BASE_PATH / "pluginlib"
TEST_CONFIG_PATH = BASE_PATH / "my2544_data.json"


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

    # read the data from xoa json config file
    with open(TEST_CONFIG_PATH, "r") as f:
        data = f.read()

        # from json string to Python dict
        config = json.loads(data)

        # start the test and get test id
        test_id = ctrl.start_test_suite(TEST_SUITE_REG_NAME, config)

        # subscribe to statistics of the test
        async for msg in ctrl.listen_changes(test_id, _filter={types.EMsgType.STATISTICS}):
            print(msg)


if __name__ == "__main__":
    asyncio.run(main())
