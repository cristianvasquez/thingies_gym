import time

import neptune
from acme.utils.loggers import base

class NeptuneLogger(base.Logger):

    def __init__(self, label: str = 'default', time_delta=0):
        self._time = time.time()
        self._time_delta = time_delta
        self.label = label

    def write(self, values: base.LoggingData):
        now = time.time()
        if (now - self._time) > self._time_delta:
            for k in values:
                neptune.log_metric(f'[{self.label}]_{k}', float(values[k]))
            self._time = now
