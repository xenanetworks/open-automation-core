import typing
if typing.TYPE_CHECKING:
    from . import misc


class InvalidTesterTypeError(ValueError):
    def __init__(self, props: "misc.IProps") -> None:
        self.props = props
        self.msg = f"Can't identify Tester Type: {props.product}"
        super().__init__(self.msg)


class TesterCommunicationError(Exception):
    def __init__(self, props: "misc.IProps", error: Exception) -> None:
        self.props = props
        self.error = error
        self.msg = f"Tester with credentials: {props} encountering communication error: {error}"
        super().__init__(self.msg)


class ResourceNotAvaliableError(Exception):
    def __init__(self, tester_id) -> None:
        self.tester_id = tester_id
        self.msg = f"Tester of id: <{self.tester_id}> is not available."
        super().__init__(self.msg)
