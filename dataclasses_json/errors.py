class DataclassJsonError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DataclassJsonSerializationException(KeyError):
    def __init__(self, *args, **kwargs) -> None:
        super(DataclassJsonSerializationException, self).__init__(*args, **kwargs)
