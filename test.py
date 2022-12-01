import asyncio
from contextlib import suppress
from pathlib import Path
from xoa_core.core.messenger.handler import OutMessagesHandler
from xoa_core.core.resources.storage import PrecisionStorage
from xoa_core.core.resources.manager import ResourcesManager
from xoa_core.core.resources.types import TesterID
# from xoa_core.core.resources.datasets.internal.credentials import CredentialsModel

# from xoa_core.controller import MainController
from xoa_core.types import (
    Credentials,
    EProductType,
    PIPE_RESOURCES
)


async def disconnected(publisher) -> None:
    async for info in publisher.changes(PIPE_RESOURCES):
        print("Disconnected\n\r", info)


async def main() -> None:
    publisher = OutMessagesHandler()
    resources_pipe = publisher.get_pipe(PIPE_RESOURCES)

    credentials = Credentials(product=EProductType.VALKYRIE, host="192.168.1.198")
    store = PrecisionStorage(Path.cwd() / "store")
    rm = ResourcesManager(resources_pipe, store)
    await rm.start()
    asyncio.create_task(disconnected(publisher))
    res = await rm.add_tester(credentials)
    print(res)
    print(await rm.get_all_testers())
    await rm.disconnect(TesterID("2906f8d041e9fd07191d6a37ef5785b2"))
    await asyncio.sleep(1)
    await rm.connect(TesterID("2906f8d041e9fd07191d6a37ef5785b2"))
    print("\n", await rm.get_all_testers())
    await asyncio.sleep(1)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, RuntimeError):
        asyncio.run(main())
