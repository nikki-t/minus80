class ErrorAfterCall(object):
    """Callable that raises CallableExhausted exception after call limit reached"""

    def __init__(self, limit):
        self.limit = limit
        self.calls = 0
    
    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted
    
class CallableExhausted(Exception):
    """Exception used to intercept inifinite loop during testing"""
    pass