import sys
import os
from typing import Any, Dict, List
from pprint import pp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from contextlib import contextmanager
from xoa_core import controller
from xoa_core import types

def bprint(*args):
    print(json.dumps(*args, indent=4))

@contextmanager
def profiler():
    import cProfile
    import pstats
    pr = cProfile.Profile()
    pr.enable()
    try:
        yield
    finally:
        pr.disable()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(20)
        # stats.dump_stats(filename='./eng_profile.prof')



LIB_PATH = "./examples/billet_plugin_example"
TEST_CONFIG_PATH = "./tests/frameloss_config.json"

async def add_testers(ctr: "controller.MainController", credentials: List["types.Credentials"]) -> None:
    for tester_cred in credentials: 
        if await ctr.add_tester(tester_cred):
            print(f"Added: {tester_cred}")
        else:
            print(f"Tester ofline or already exists: {tester_cred}")

def load_test_config(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def playground():
    new_testers = [
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.114"),
        types.Credentials(product=types.EProductType.VALKYRIE, host="192.168.1.198"),
        # types.Credentials( product=types.EProductType.VALKYRIE, host="192.168.1.197"),
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.118"), 
    ]
    
    c = await controller.MainController()
    c.register_lib(LIB_PATH)
    await add_testers(c, new_testers)
    
    test_config = load_test_config(TEST_CONFIG_PATH)
    id = c.start_test_suite("RFC-2544[Frame Loss]", test_config)
    print(id)
    async for msg in c.listen_changes(id, _filter={types.EMsgType.STATISTICS}):
        pp(msg.dict(), indent=2, width=80)


def main():
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(playground())
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()