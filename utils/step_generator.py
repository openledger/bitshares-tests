class StepGenerator(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StepGenerator, cls).__new__(
                cls, *args, **kwargs)
            cls._instance._step_number = 0
        return cls._instance

    def reset(self):
        self._step_number = 0

    def increment(self):
        self._step_number += 1
        return self._step_number
