from __future__ import annotations
import asyncio
import json
import sys
import os
from contextlib import suppress
from typing import Any
from pprint import pp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xoa_core import controller  # noqa: E402
from xoa_core import types  # noqa: E402


def bprint(*args):
    print(json.dumps(*args, indent=4))


LIB_PATH = "./examples/billet_plugin_example"
TEST_CONFIG_PATH = "./tests/frameloss_config.json"


async def add_testers(ctr: "controller.MainController", credentials: list["types.Credentials"]) -> None:
    for tester_cred in credentials:
        if await ctr.add_tester(tester_cred):
            print(f"Added: {tester_cred}")
        else:
            print(f"Tester offline or already exists: {tester_cred}")


def load_test_config(file_path: str) -> dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def playground():
    new_testers = [
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.114"),
        # types.Credentials(product=types.EProductType.VALKYRIE, host="192.168.1.198"),
        types.Credentials(product=types.EProductType.VALKYRIE, host="demo.xenanetworks.com"),
        # types.Credentials( product=types.EProductType.VALKYRIE, host="192.168.1.197"),
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.118"),
    ]

    ctrl = await controller.MainController()
    ctrl.register_lib(LIB_PATH)
    await add_testers(ctrl, new_testers)

    # print(await ctrl.list_testers_info())

    test_config = load_test_config(TEST_CONFIG_PATH)
    id = ctrl.start_test_suite("RFC-2544[Frame Loss]", test_config, debug_connection=True)
    async for msg in ctrl.listen_changes(id):
        pp(msg.dict(), indent=2, width=80)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(playground())
