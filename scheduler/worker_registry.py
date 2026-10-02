import time, threading

class WorkerRegistry:
    def __init__(self, heartbeat_timeout=5):
        self.heartbeat_timeout=heartbeat_timeout; self.workers={}; self.lock=threading.RLock()
    def register(self,w):
        with self.lock: self.workers[w.worker_id]=w
    def heartbeat(self,wid):
        with self.lock:
            w=self.workers.get(wid)
            if w: w.last_heartbeat=time.monotonic(); w.alive=True
            return w
    def get(self,wid):
        with self.lock: return self.workers.get(wid)
    def all(self):
        with self.lock: return list(self.workers.values())
    def mark_dead(self):
        dead=[]; now=time.monotonic()
        with self.lock:
            for w in self.workers.values():
                if w.alive and now-w.last_heartbeat>self.heartbeat_timeout:
                    w.alive=False; dead.append(w)
        return dead
