from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
import asyncio
import json
from pathlib import Path

PLUGINS_PATH = Path(__file__).parent
XOA_2544_CONFIG = "xoa_2544_config.json"
XOA_2889_CONFIG = "xoa_2889_config.json"


async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )

    # Create a default instance of the controller class.
    ctrl = await controller.MainController()

    # Register the plugins folder.
    ctrl.register_lib(str(PLUGINS_PATH))

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await ctrl.add_tester(my_tester_credential)

    # Subscribe to test resource notifications.
    async for msg in ctrl.listen_changes(types.PIPE_RESOURCES):
        print(msg)

    # Load your XOA 2544 config and run.
    with open(XOA_2544_CONFIG, "r") as f:

        # get rfc2544 test suite information from the core's registration
        info = ctrl.get_test_suite_info("RFC-2544")
        if not info:
            print("Test suite RFC-2544 is not recognized.")
            return None

        # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
        test_exec_id = ctrl.start_test_suite("RFC-2544", json.load(f))
    
        # The example here only shows a print of test result data.
        async for stats_data in ctrl.listen_changes(test_exec_id, _filter={types.EMsgType.STATISTICS}):
            print(stats_data)


if __name__ == "__main__":
    asyncio.run(main())
