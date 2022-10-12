from __future__ import annotations
from xoa_core import (
    controller,
    types,
)
from pathlib import Path
import asyncio
import json

BASE_PATH = Path.cwd()
PLUGINS_PATH = BASE_PATH / "plugins"
TEST_CONFIG_PATH = BASE_PATH / "my2544_data.json"


async def do_test(tester: types.Credentials, suite_name, data):
    ctrl = await controller.MainController()
    ctrl.register_lib(PLUGINS_PATH)
    await ctrl.add_tester(tester)
    execution_id = ctrl.start_test_suite(suite_name, data)
    async for msg in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(msg)


async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )
    # Load your test configuration data into the test suite and run.
    with open(TEST_CONFIG_PATH, "r") as f:
        data = json.load(f)
        await do_test(my_tester_credential, "RFC-2544", data)


if __name__ == "__main__":
    asyncio.run(main())
