import asyncio
from contextlib import suppress
import time
from xoa_core.core.resources.resource import Resource
# from xoa_core.core.resources.datasets.internal.credentials import CredentialsModel

# from xoa_core.controller import MainController
from xoa_core.types import (
    Credentials,
    EProductType,
    PIPE_RESOURCES
)


def disconnected(t):
    print("Disconnected", t)


def func():
    for i in range(5):
        yield i
        time.sleep(1)

async def main() -> None:
    _loop = asyncio.get_event_loop()
    gen = await _loop.run_in_executor(None, func)
    for i in gen:
        print(i)
    # credentials = Credentials(product=EProductType.VALKYRIE, host="192.168.1.198")
    # resource = Resource(credentials, disconnected)
    # print(resource.as_dict)
    # await resource.connect()
    # print(resource.as_dict)
    # await resource.disconnect()
    # print(resource.as_dict)
    # await resource.connect()
    # print(resource.as_dict)
    # await asyncio.sleep(1)
    # controller = await MainController()
    # await controller.add_tester(
    #     Credentials(product=EProductType.VALKYRIE, host="192.168.1.198")
    # )
    # avaliable_resources = controller.list_testers()
    # print(avaliable_resources)
    # async for info in controller.listen_changes(PIPE_RESOURCES):
    #     print(info)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, RuntimeError):
        asyncio.run(main())
