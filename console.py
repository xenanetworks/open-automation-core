import sys, os
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "xmp-truck"
    )
)
import json
import asyncio
import aioconsole
from xoa_core import ChassisInfo, ID
from main import ValhallaCore

class BreakException(Exception):
    pass

async def ainput(message):
    input = await aioconsole.ainput(message)
    if input == 'exit': 
        exit()
    elif input == 'break':
        raise BreakException()
    else:
        return input

async def test(vc):
    input_message = """
        Please input a code of the command:
        1. run a test
        2. stop a test
        3. show supported plugins
        4. add a tester
        5. delete a tester
        6. show current working test
        7. show all testers
        """
    while True:
        try:
            code = await ainput(input_message)
            print(f'Your code is: {code}')
            if code == '1': 

                plugins = vc.plugin_controller.list_plugins()

                for i in range(len(plugins)):
                    print(f"{i + 1}: {plugins[i]}")
                plugin_key = await ainput('Please input the Plugin code You want to run: ')
                config_file = await ainput('Please input the config file You want to run: ')
                with open(config_file, 'r') as f:
                    d = json.load(f)
                # print(json.dumps(d))
                print(plugins)
                print(plugins[int(plugin_key) - 1])
                for i in (
                    "xoa_core.log",
                    "xoa_driver.log",
                    "debug.log",
                    "info.log",
                    "error.log",
                    "log/plugin.log",
                    "resource_pool.log"
                ):
                    with open(i, "w") as f:
                        pass
                vc.execute_pool.add(plugins[int(plugin_key) - 1], d )
            elif code == '2':
                task_id = await ainput('Please input the id of the task you want to stop: ')
                await vc.execute_pool.stop(task_id)
                print(f'Successfully stop the task: {task_id}')
            elif code == '3': 
                plugins = vc.plugin_controller.list_plugins()
                print(f"{plugins}")
            elif code == '4': 
                host = await ainput('Please input host name: ')
                port = await ainput('Please input port number: ')
                password = await ainput('Please input password: ')
                tester = await vc.tester_handler.add_tester(ChassisInfo(
                    host=host, port=port, password=password
                ))
                print(f"successfully add tester! {tester}")
            elif code == '5': 
                tester_id = await ainput('Please input id of the tester you want to delete: ')
                tester = await vc.tester_handler.remove_tester(tester_id)
                print(f"successfully delete tester! {tester}")
            elif code == '6': 
                workers = vc.execute_pool.all()
                print(f"current workers: {workers}")
            elif code == '7': 
                # print('get all testers!')
                testers = await vc.tester_handler.get_all_testers()
                print(type(testers))
                print(json.dumps(testers, indent=2))

        except BreakException as e:
            continue
        except Exception as e:
            print(e)
            continue

if __name__  == '__main__':
    for i in (
        "debug.log",
        "info.log",
        "error.log",
        "log/plugin.log",
        "test.log"
    ):
        with open(i, "w") as f:
            pass
    loop = asyncio.get_event_loop()
    vc = ValhallaCore(loop)
    vc.start()
    # open ui
    # ui fetch avaliable testers
    loop.create_task(test(vc))
    # loop.call_later(1, test, vc)
    loop.run_forever()