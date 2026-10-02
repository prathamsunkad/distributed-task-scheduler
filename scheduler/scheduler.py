import threading,time,uuid
from .models import Job
from .queue import JobQueue

class Scheduler:
    def __init__(self,registry,policy,heartbeat_interval=1):
        self.registry=registry; self.policy=policy; self.queue=JobQueue(); self.jobs={}; self.connections={}
        self.lock=threading.RLock(); self.stop_event=threading.Event(); self.interval=heartbeat_interval
        self.thread=threading.Thread(target=self._loop,daemon=True)
    def start(self): self.thread.start()
    def stop(self): self.stop_event.set(); self.thread.join(timeout=2)
    def submit(self,task_type,payload,priority=0,required_cpu=1,required_memory=128,max_retries=2):
        j=Job(str(uuid.uuid4()),task_type,payload,priority,required_cpu,required_memory,max_retries)
        with self.lock: self.jobs[j.job_id]=j
        self.queue.put(j); return j
    def attach(self,wid,conn):
        with self.lock: self.connections[wid]=conn
    def detach(self,wid):
        with self.lock: self.connections.pop(wid,None)
    def _release(self,w,j):
        w.active_jobs.discard(j.job_id); w.used_cpu=max(0,w.used_cpu-j.required_cpu); w.used_memory=max(0,w.used_memory-j.required_memory)
    def _retry(self,j,error):
        j.error=error
        if j.attempts<=j.max_retries:
            j.status="queued"; j.worker_id=None; self.queue.put(j)
        else:
            j.status="failed"; j.finished_at=time.monotonic()
    def complete(self,jid,wid,status,error=None):
        with self.lock:
            j=self.jobs.get(jid); w=self.registry.get(wid)
            if not j:return
            if w:self._release(w,j)
            j.finished_at=time.monotonic(); j.status=status; j.error=error
            if status!="success": self._retry(j,error or "task failed")
    def _dispatch(self,j):
        with self.lock:
            w=self.policy.choose(j,self.registry.all()); conn=self.connections.get(w.worker_id) if w else None
            if not w or not conn:return False
            j.status="running"; j.worker_id=w.worker_id; j.attempts+=1; j.started_at=j.started_at or time.monotonic()
            w.active_jobs.add(j.job_id); w.used_cpu+=j.required_cpu; w.used_memory+=j.required_memory
        try: conn.send(j.to_dict()); return True
        except Exception as e:
            with self.lock:self._release(w,j); self._retry(j,str(e))
            return True
    def _fail_workers(self):
        for w in self.registry.mark_dead():
            with self.lock:
                for jid in list(w.active_jobs):
                    j=self.jobs.get(jid)
                    if j:self._release(w,j); self._retry(j,f"worker {w.worker_id} heartbeat timeout")
    def _loop(self):
        last=0
        while not self.stop_event.is_set():
            j=self.queue.get_nowait()
            if j is not None and not self._dispatch(j): self.queue.put(j)
            if time.monotonic()-last>=self.interval:self._fail_workers();last=time.monotonic()
            time.sleep(.005)
    def status(self):
        with self.lock:
            counts={}
            for j in self.jobs.values():counts[j.status]=counts.get(j.status,0)+1
            return {"jobs":counts,"queued":self.queue.qsize(),"workers":[{"worker_id":w.worker_id,"alive":w.alive,"active_jobs":len(w.active_jobs),"cpu_utilization":w.cpu_utilization} for w in self.registry.all()]}
