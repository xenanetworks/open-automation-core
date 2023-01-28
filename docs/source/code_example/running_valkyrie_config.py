from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
import asyncio
import json
from xoa_converter.entry import converter
from xoa_converter.types import TestSuiteType

PLUGIN_2544_PATH = "plugin2544"
OLD_2544_CONFIG =  "old_2544_config.v2544" 
PLUGIN_2889_PATH = "plugin2889"
OLD_2889_CONFIG =  "old_2544_config.v2544" 

async def convert_run_test(tester: types.Credentials, converter_type: TestSuiteType, plugin_path: str, suite_name: str, config):
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
    
    # convert the old config file into new config file
    new_data = converter(converter_type, config, info["schema"])

    # you can use the config file below to start the test
    new_config = json.loads(new_data)

    # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
    execution_id = ctrl.start_test_suite(suite_name, new_config)
    
    # The example here only shows a print of test result data.
    async for stats_data in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(stats_data)


async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )

    # Convert Valkyrie 2544 config into XOA 2544 config and run.
    with open(OLD_2544_CONFIG, "r") as f:
        await convert_run_test(
            tester=my_tester_credential, 
            converter_type=TestSuiteType.RFC2544,
            plugin_path=PLUGIN_2544_PATH, 
            suite_name="RFC-2544", 
            config=f.read()
            )
    
    # Convert Valkyrie 2889 config into XOA 2889 config and run.
    with open(OLD_2889_CONFIG, "r") as f:
        await convert_run_test(
            tester=my_tester_credential, 
            converter_type=TestSuiteType.RFC2889,
            plugin_path=PLUGIN_2889_PATH, 
            suite_name="RFC-2889", 
            config=f.read()
            )


if __name__ == "__main__":
    asyncio.run(main())
