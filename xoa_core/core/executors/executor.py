import asyncio
import contextlib
from enum import Enum
import queue
import time
import uuid
import typing
from pydantic import BaseModel
from multiprocessing import Process, Value, Manager, Pipe, SimpleQueue
from multiprocessing.managers import BaseManager, NamespaceProxy

from xoa_core.core.generic_types import (
    TObserver,
    TMesagesPipe,
)
from xoa_core.types import PluginAbstract, EMsgType, Progress

if typing.TYPE_CHECKING:
    from pydantic import BaseModel
    from xoa_core.types import PluginAbstract
    from xoa_core.core.plugin_abstract import (
        PStateConditionsFacade,
        PPipeFacade,
        TransmitFunc,
    )


from .executor_info import ExecutorInfo
from . import exceptions
from ._events import Event
from .executor_state import ExecutorState
# from .executor_state_conditions import StateConditions
from .executor_state_conditions import StateConditionsFacade

from loguru import logger

logger.add("core.log")

class MessageFromSubProcess(BaseModel):
    msg_type: EMsgType
    msg: typing.Any


class PPlugin(typing.Protocol):
    def create_test_suite(self, state_conditions: "PStateConditionsFacade", xoa_out: "PPipeFacade") -> "PluginAbstract": ...  # noqa: E704

class RelayXOAOut:
    def __init__(self, transmit: "TransmitFunc", suite_name: str) -> None: # noqa: E704
        self.transmit = transmit

    def send_statistics(self, data: typing.Union[typing.Dict, "BaseModel"]) -> None:
        """Method used for push statistics data into the messages pipe for future distribution"""
        self.transmit(data, msg_type=EMsgType.STATISTICS)

    def send_progress(self, current: int, total: int = 100) -> None:
        self.transmit(Progress(current=current, total=total), msg_type=EMsgType.PROGRESS)

    def send_warning(self, warning: Exception) -> None:
        logger.debug(warning)

    def send_error(self, error: Exception) -> None:
        logger.debug(error)


def root_call(suite_executor: "SuiteExecutor"):
    ts = suite_executor.plugin.create_test_suite(
        state_conditions=suite_executor.state_conditions.get_facade(),
        # xoa_out=suite_executor.msg_pipe.get_facade(suite_executor.suite_name)
        xoa_out=RelayXOAOut(lambda: 1, suite_executor.suite_name)
    )
    asyncio.run(ts.start())


class ExecuteEvent(Enum):
    PAUSE = 'PAUSE'
    STOP = 'STOP'

class EventFromParent(BaseModel):
    event_type: ExecuteEvent
    is_event_set: bool

class StateConditions:
    __slots__ = ("continue_event", "stop_event")

    def __init__(self) -> None:
        manager = Manager()
        self.continue_event = manager.Event()
        self.continue_event.set()
        self.stop_event = manager.Event()

    @property
    async def wait_if_paused(self) -> None:
        """Wait till user toggle pause state."""
        logger.debug('wait_if_paused')
        return await asyncio.sleep(1)
        # await self.continue_event.wait()

    async def stop_if_stopped(self) -> None:
        if self.stop_event.is_set():
            raise exceptions.StopPlugin()

    def get_facade(self) -> StateConditionsFacade:
        return StateConditionsFacade(
            self.wait_if_paused,
            self.stop_if_stopped
        )

    def pause(self) -> None:
        self.continue_event.clear()

    def resume(self) -> None:
        self.continue_event.set()

    def stop(self) -> None:
        self.stop_event.set()

class SuiteExecutor:
    # __slots__ = ("suite_name", "state", "__id", "__observer", "msg_pipe", "__test_suite", "__task", "state_conditions", "plugin", "event_pipe", "message_pipe")

    def __init__(self, suite_name: str) -> None:
        self.__id = str(uuid.uuid4())
        self.suite_name = suite_name
        self.state = ExecutorState()
        self.state_conditions = StateConditions()
        self.event_pipe_parent, self.event_pipe_child = Pipe()
        self.message_pipe_parent, self.message_pipe_child = Pipe()

    @property
    def id(self) -> str:
        return self.__id

    def __on_execution_terminated(self, task: "asyncio.Task") -> None:
        logger.debug('terminated')
        if not self.state.is_stoped:
            self.state.set_stop()
        self.__observer.emit(Event.STOPPED, self.id)
        asyncio.create_task(self.msg_pipe.disable())  # In rare case raise error but it's not break anything.
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            e = task.exception()
            if e is None:
                return None
            self.__observer.emit(Event.ERROR, task.get_name(), e)
            raise e

    def get_info(self) -> ExecutorInfo:
        return ExecutorInfo(
            id=self.__id,
            suite_name=self.suite_name,
            state=self.state.current_state,
        )

    def assign_pipe(self, pipe: "TMesagesPipe") -> None:
        self.msg_pipe = pipe
        self.state.assign_senders(pipe.get_state_facade())

    def assign_plugin(self, plugin: PPlugin) -> None:
        self.plugin = plugin
        self.__test_suite = plugin.create_test_suite(
            state_conditions=self.state_conditions.get_facade(),
            xoa_out=self.msg_pipe.get_facade(self.suite_name)
        )

    async def fake_test(self) -> None:
        logger.debug(self.state_conditions.continue_event.is_set())
        await asyncio.sleep(10)
        logger.debug('awake')
        logger.debug(self.state_conditions.continue_event.is_set())

    async def fake_send_msg(self):
        count = 0
        await asyncio.sleep(5)
        xoa_out = self.msg_pipe.get_facade(self.suite_name)
        while count < 10:
            self.message_pipe_child.send(
                MessageFromSubProcess(msg_type=EMsgType.WARNING, payload=Exception('test'))
            )
            await asyncio.sleep(0.1)
            count += 1
            if self.event_pipe_child.poll():
                msg = self.event_pipe_child.recv()
                logger.debug('*'*40)
                logger.debug(msg)
        self.event_pipe_child.close()

    def create_test_suite(self):
        test_suite = self.plugin.create_test_suite(self.state_conditions.get_facade(), xoa_out=RelayXOAOut(self.send_message_from_child, self.suite_name))
        return test_suite

    def sub_process_func(self, num: int, state) -> None:
        xoa_out = self.msg_pipe.get_facade(self.suite_name)
        logger.debug('sub process run')
        loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.fake_test(state, pipe))
        # loop.run_until_complete(self.__test_suite.start())
        # asyncio.run(self.fake_test())
        # asyncio.run(self.__test_suite.start())
        # asyncio.run(self.fake_send_msg())
        asyncio.run(self.create_test_suite().start())
        # relay_state.change_state('stop', True)
        state.set()
        logger.debug(state)
        logger.debug('set stop')
        state.clear()
        logger.debug(state)
        logger.debug('sub process end')


    async def wrap_test(self) -> None:
        # while True:
        #     xoa_out.send_statistics({'k': time.time()})
        #     await asyncio.sleep(0.5)
        manager = Manager()
        inter_state = manager.Event()

        p = Process(target=self.sub_process_func, args=(333, inter_state), daemon=True)
        p.start()
        while p.is_alive():
            await asyncio.sleep(0.01)
        else:
            self.message_pipe_child.close()
            self.event_pipe_child.close()
            logger.debug('wrap end')
            return
        # await asyncio.sleep(10)

    def send_message_from_child(self, msg: typing.Any, msg_type: EMsgType):
        self.message_pipe_child.send(MessageFromSubProcess(msg=msg, msg_type=msg_type))

    async def poll_child_sended_message(self):
        xoa_out = self.msg_pipe.get_facade(self.suite_name)
        while True:
            if self.message_pipe_child.closed:
                break
            if self.message_pipe_parent.poll():
                msg = self.message_pipe_parent.recv()
                xoa_out.send_statistics(msg)
            await asyncio.sleep(0.01)

    async def test_pause(self):
        await asyncio.sleep(3)
        self.__send_pause_event()

    def run(self, observer: TObserver) -> None:
        self.__observer = observer
        self.state.set_run()

        # self.__task = asyncio.create_task(
        #     self.__test_suite.start(),
        #     name=f"{self.suite_name}[{self.id}]"
        # )
        # self.__task.add_done_callback(self.__on_execution_terminated)
        # inter_state = manager.Event()
        # p = Process(target=self.ttt, args=(333, inter_state, pipe), daemon=True)
        # p.start()
        t = asyncio.create_task(self.wrap_test())
        t = asyncio.create_task(self.poll_child_sended_message())
        t.add_done_callback(self.__on_execution_terminated)
        asyncio.create_task(self.test_pause())

        # xoa_out = self.msg_pipe.get_facade(self.suite_name)
        # while p.is_alive():
        #     xoa_out.send_statistics({'t': time.time()})
            # time.sleep(1)
        # self.__on_execution_terminated(asyncio.create_task(asyncio.sleep(1)))
        # manager.shutdown()

    def __send_pause_event(self) -> None:
        self.state_conditions.pause()
        logger.debug('pause event sended')

    async def toggle_pause(self) -> None:
        """User interface toggle pause."""
        if self.state.is_running:
            self.state.set_pause()
            # self.state_conditions.pause()
            self.__send_pause_event()
            await self.__test_suite.on_pause()
        elif self.state.is_paused:
            self.state.set_run()
            self.__send_pause_event()
            await self.__test_suite.on_continue()

    async def stop(self) -> None:
        """User interface stop the test suite."""
        self.state.set_stop()
        self.state_conditions.stop()
        await self.__test_suite.on_stop()
        self.__task.cancel()
        with contextlib.suppress(asyncio.CancelledError, exceptions.StopPlugin):
            await self.__task
