
import numpy as np
import time

class Statistics(object):
    def __init__(self, batchsize=10):
        self.BatchSize = batchsize
        self.reset()

    def reset(self):
        self.Samples = np.r_[[np.NaN] * self.BatchSize]
        self.Idx = 0

    def add(self, val):
        self.Samples[self.Idx] = val
        self.Idx = (self.Idx + 1) % self.BatchSize

    def _get_NotNan(self):
        return self.Samples[np.isnan(self.Samples) == False]

    def mean(self):
        v = self._get_NotNan()
        return v.mean() if len(v) > 0 else np.NaN

    def std(self):
        v = self._get_NotNan()
        return v.std() if len(v) > 0 else np.NaN

    def min(self):
        v = self._get_NotNan()
        return v.min() if len(v) > 0 else np.NaN

    def max(self):
        v = self._get_NotNan()
        return v.max() if len(v) > 0 else np.NaN

    def last(self):
        LastIdx = self.Idx - 1 if self.Idx > 0 else self.BatchSize - 1
        return self.Samples[LastIdx]


class StatisticsTimer(Statistics):
    def __init__(self, batchsize=10):
        Statistics.__init__(self, batchsize=batchsize)
        self.Started = 0.0

    def start(self):
        self.Started = time.time()

    def stop(self):
        self.add(time.time() - self.Started)
        self.Started = 0.0

