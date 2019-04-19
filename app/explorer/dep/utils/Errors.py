

class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg



class TxnValidationError(BaseException):
    pass

