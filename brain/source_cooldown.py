"""Per-source process-local Retry-After shared by discovery and foreground reads."""
import math
import threading
import time
from .confluence import JsonTransport, SourceRateLimited


class SourceCooldownTransport(JsonTransport):
    def __init__(self, delegate, *, clock=time.monotonic):
        self.delegate=delegate;self.clock=clock;self.lock=threading.Lock();self.until=0

    def _call(self, callback):
        with self.lock:
            remaining=self.until-self.clock()
        if remaining>0:raise SourceRateLimited(math.ceil(remaining))
        # Never hold this lock during network I/O: foreground and the single
        # discovery worker retain their bounded lanes. An already in-flight
        # request admitted before 429 may finish; subsequent admissions stop locally.
        try:
            result=callback()
            if result[0]==429:raise SourceRateLimited(60)
            return result
        except SourceRateLimited as error:
            with self.lock:self.until=max(self.until,self.clock()+error.retry_after)
            raise

    def get(self, *args, **kwargs):
        return self._call(lambda:self.delegate.get(*args,**kwargs))

    def media(self, *args, **kwargs):
        return self._call(lambda:self.delegate.media(*args,**kwargs))
