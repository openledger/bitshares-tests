class BitshareBaseException(Exception):
    pass


class BitshareRequestError(BitshareBaseException):
    pass


class BitshareConditionError(BitshareBaseException):
    pass


class BitshareStatusCodeError(BitshareRequestError):
    def __init__(self, msg, *args, **kwargs):
        super(BitshareStatusCodeError, self).__init__(msg, *args, **kwargs)
