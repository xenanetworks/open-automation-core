from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
import asyncio
import json

PLUGIN_2544_PATH = "plugin2544"
XOA_2544_CONFIG = "xoa_2544_config.json"
PLUGIN_2889_PATH = "plugin2889"
XOA_2889_CONFIG = "xoa_2889_config.json"

async def run_test(tester: types.Credentials, plugin_path: str, suite_name: str, config):
    # Create a default instance of the controller class.
    ctrl = await controller.MainController()

    # Register the plugins folder.
    ctrl.register_lib(plugin_path)

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await ctrl.add_tester(tester)

    # get rfc2544 test suite information from the core's registration
    info = ctrl.get_test_suite_info(suite_name)
    if not info:
        print("Test suite is not recognized.")
        return None
    
    # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
    execution_id = ctrl.start_test_suite(suite_name, config)
    
    # The example here only shows a print of test result data.
    async for stats_data in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(stats_data)


async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )

    # Load your XOA 2544 config and run.
    with open(XOA_2544_CONFIG, "r") as f:
        await run_test(
            tester=my_tester_credential, 
            plugin_path=PLUGIN_2544_PATH, 
            suite_name="RFC-2544", 
            config=json.load(f)
            )
    
    # Load your XOA 2889 config and run.
    with open(XOA_2889_CONFIG, "r") as f:
        await run_test(
            tester=my_tester_credential, 
            plugin_path=PLUGIN_2889_PATH, 
            suite_name="RFC-2889", 
            config=json.load(f)
            )


if __name__ == "__main__":
    asyncio.run(main())
