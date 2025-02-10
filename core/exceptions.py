class OSError(Exception):
    pass

class OSNotSupportedError(OSError):
    def __init__(self, processor_name: str, platform: str):
        self.processor_name = processor_name
        self.platform = platform
        super().__init__(f"{processor_name} is not supported on {platform}")

class OSCompatibilityWarning(UserWarning):
    pass
