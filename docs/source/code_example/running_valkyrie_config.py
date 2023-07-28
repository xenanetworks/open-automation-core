from __future__ import annotations
import sys
from xoa_core import (
    controller,
    types,
)
import asyncio
import json
from pathlib import Path
# XOA Converter is an independent module and it needs to be installed via `pip install xoa-converter`
try:
    from xoa_converter.entry import converter
    from xoa_converter.types import TestSuiteType
except ImportError:
    print("XOA Converter is an independent module and it needs to be installed via `pip install xoa-converter`")
    sys.exit()

PROJECT_PATH = Path(__file__).parent
OLD_2544_CONFIG = PROJECT_PATH / "old_2544_config.v2544"
OLD_2889_CONFIG = PROJECT_PATH / "old_2889_config.v2889"
PLUGINS_PATH = PROJECT_PATH / "test_suites"


async def subscribe(ctrl: "controller.MainController", channel_name: str, fltr: set["types.EMsgType"] | None = None) -> None:
    async for msg in ctrl.listen_changes(channel_name, _filter=fltr):
        print(msg)



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
    asyncio.create_task(subscribe(ctrl, channel_name=types.PIPE_RESOURCES))

    # Convert Valkyrie 2544 config into XOA 2544 config and run.
    with open(OLD_2544_CONFIG, "r") as f:
        # get rfc2544 test suite information from the core's registration
        info = ctrl.get_test_suite_info("RFC-2544")
        if not info:
            print("Test suite is not recognized.")
            return None

        # convert the old config file into new config file
        new_data = converter(TestSuiteType.RFC2544, f.read())

        # you can use the config file below to start the test
        new_config = json.loads(new_data)

        # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
        execution_id = ctrl.start_test_suite("RFC-2544", new_config)


        # The example here only shows a print of test result data.
        asyncio.create_task(
            subscribe(ctrl, channel_name=execution_id, fltr={types.EMsgType.STATISTICS})
        )

    # By the next line, we prevent the script from being immediately
    # terminated as the test execution and subscription are non blockable, and they ran asynchronously,
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
