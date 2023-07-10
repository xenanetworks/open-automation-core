class ExecutorError(Exception):
    pass


class StopPlugin(ExecutorError):
    def __init__(self) -> None:
        self.msg = "Plugin execution is stopped by user."
        super().__init__(self.msg)


class ExecutionError(ExecutorError):
    def __init__(self, plugin_name: str) -> None:
        self.plugin_name = plugin_name
        self.msg = f"During of the execution Plugin: <{plugin_name}> raised the error."
        super().__init__(self.msg)
