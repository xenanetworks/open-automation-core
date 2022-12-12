from .misc import Credentials


class InvalidTesterTypeError(ValueError):
    def __init__(self, props: Credentials) -> None:
        self.props = props
        self.msg = f"Can't identify Tester Type: {props.product}"
        super().__init__(self.msg)


class TesterCommunicationError(Exception):
    def __init__(self, props: Credentials, error: Exception) -> None:
        self.props = props
        self.error = error
        self.msg = f"Tester with credentials: {props} encountering communication error: {error}"
        super().__init__(self.msg)


class IsDisconnectedError(Exception):
    """Raises when tester is already disconnected."""
    def __init__(self, tester_id) -> None:
        self.tester_id = tester_id
        self.msg = f"Tester: <{self.tester_id}> is already disconnected."
        super().__init__(self.msg)


class IsConnectedError(Exception):
    """Raises when tester is already connected."""
    def __init__(self, tester_id) -> None:
        self.tester_id = tester_id
        self.msg = f"Tester: <{self.tester_id}> is already connected."
        super().__init__(self.msg)


# region Pool Exceptions

class UnknownResourceError(Exception):
    """Raises when user trying to get acces to resource which is not known."""
    def __init__(self, tester_id) -> None:
        self.tester_id = tester_id
        self.msg = f"Unknown tester of id: <{self.tester_id}>."
        super().__init__(self.msg)

# endregion
