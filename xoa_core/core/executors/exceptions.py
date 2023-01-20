class StopPlugin(Exception):
    def __init__(self) -> None:
        self.msg = "Plugin execution is stopped by user."
        super().__init__(self.msg)
