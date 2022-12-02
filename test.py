from __future__ import annotations
import asyncio
from contextlib import suppress
from pathlib import Path
from typing import Any, TypedDict
from xoa_core.core.resources.types import TesterID
from xoa_core.controller import MainController
from xoa_core.types import (
    Credentials,
    EProductType,
    PIPE_RESOURCES
)


async def disconnected(publisher) -> None:
    async for info in publisher(PIPE_RESOURCES):
        print(info.payload.action)


async def func(dataset: dict[str, Any], event: str) -> None:
    print(dataset, event)


async def main() -> None:
    credentials = Credentials(product=EProductType.VALKYRIE, host="192.168.1.198")
    ctrl = await MainController(storage_path=Path.cwd() / "store")
    asyncio.create_task(disconnected(ctrl.listen_changes))
    await ctrl.add_tester(credentials)
    await ctrl.disconnect_tester(TesterID("2906f8d041e9fd07191d6a37ef5785b2"))
    await ctrl.connect_tester(TesterID("2906f8d041e9fd07191d6a37ef5785b2"))
    await ctrl.remove_tester(TesterID("2906f8d041e9fd07191d6a37ef5785b2"))
    print("\n", await ctrl.list_testers())
    await asyncio.sleep(1)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, RuntimeError):
        asyncio.run(main())
