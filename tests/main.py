import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from pprint import pprint
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


async def playground():
    new = [
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.114", password="xena"),
        types.Credentials( product=types.EProductType.VALKYRIE, host="192.168.1.198", password="xena"), # wrong password
        # types.Credentials( product=types.EProductType.VALKYRIE, host="192.168.1.197", password="xena"), # tester is turned off
        # types.Credentials( product=types.EProductType.VALKYRIE, host="87.61.110.118", password="xena"), 
    ]
    
    c = await controller.MainController()
    c.register_lib("./examples/billet_plugin_example")
    print("start")
    for t in new: await c.add_tester(t)

    with open("./tests/frameloss_config.json", "r") as f:
        data = json.load(f)
    id = c.start_test_suite("RFC-2544[Frame Loss]", data)
    print(id)
    async for msg in c.listen_changes(id, _filter={types.EMsgType.STATISTICS}):
        pprint(msg)



def main():
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(playground())
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()