
class WrongModuleTypeError(Exception):
    def __init__(self, module) -> None:
        self.module_type = type(module)
        self.msg = f"Provided module of: {self.module_type} can't be used."
        super().__init__(self.msg)

class NoRxDataError(Exception):
    def __init__(self) -> None:
        self.msg = "No RX DATA"
        super().__init__(self.msg)

class PeerNotSpecifiedError(Exception):
    def __init__(self) -> None:
        self.msg = "Port Resource are not contain a Peer Port Resource"
        super().__init__(self.msg)