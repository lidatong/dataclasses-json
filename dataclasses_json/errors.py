class DataclassSerializationException(KeyError):
    def __init__(self, *args, **kwargs) -> None:
        super(DataclassSerializationException, self).__init__(*args, **kwargs)
