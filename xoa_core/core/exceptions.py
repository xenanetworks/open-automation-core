from xoa_core import __version__


class TestSuiteNotExistError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        self.msg = f"Test Suite: <{self.name}> is not exist."
        super().__init__(self.msg)


class TestSuiteVersionError(Exception):
    def __init__(self, name: str, required_version: str) -> None:
        self.name = name
        self.required_version = required_version
        self.msg = f"Test Suite: <{self.name}> require framework version of <{self.required_version}> current is: <{__version__}>"
        super().__init__(self.msg)


class MultiModeError(Exception):
    def __init__(self) -> None:
        self.msg = "Only single Test suite execution is permited."
        super().__init__(self.msg)


class InvalidPluginError(ValueError):
    def __init__(self, value, expected) -> None:
        self.value = value
        self.expected = expected
        self.msg = f"Invalid plugin. Plugin Entry Class {self.value} must be a subclass of {self.expected}."
        super().__init__(self.msg)
