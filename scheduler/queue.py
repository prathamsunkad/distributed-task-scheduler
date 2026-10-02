import heapq, itertools, threading

class JobQueue:
    def __init__(self):
        self._heap=[]; self._counter=itertools.count(); self._lock=threading.Condition()
    def put(self, job):
        with self._lock:
            heapq.heappush(self._heap, (-job.priority, next(self._counter), job)); self._lock.notify()
    def get_nowait(self):
        with self._lock:
            return heapq.heappop(self._heap)[2] if self._heap else None
    def qsize(self):
        with self._lock: return len(self._heap)
