from xoa_driver import testers
from xoa_driver import modules
from xoa_driver import ports


def is_tester(inst) -> bool:
    cmp_types = (
        testers.L23Tester,
        testers.L47Tester,
        testers.L47VeTester
    )
    return isinstance(inst, cmp_types)


def is_module(inst) -> bool:
    cmp_types = (
        modules.ModuleL23,
        modules.ModuleL23VE,
        modules.ModuleChimera,
        modules.ModuleL47,
        modules.ModuleL47VE,
    )
    return isinstance(inst, cmp_types)


def is_port(inst) -> bool:
    cmp_types = (
        ports.BasePortL23,
        ports.PortL23VE,
        ports.PortChimera,
        ports.PortL47,
    )
    return isinstance(inst, cmp_types)
