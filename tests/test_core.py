from scheduler.models import Job,WorkerInfo
from scheduler.queue import JobQueue
from scheduler.policies import FIFOPolicy,PriorityPolicy,PriorityResourcePolicy

def j(p=0):return Job("j","sleep",{},priority=p)
def test_queue_priority():
 q=JobQueue();q.put(j(1));q.put(j(10));assert q.get_nowait().priority==10
def test_fifo():
 w=[WorkerInfo("a",4,4096,("x",1)),WorkerInfo("b",4,4096,("x",2))];assert FIFOPolicy().choose(j(),w).worker_id=="a"
def test_priority():
 w=[WorkerInfo("a",4,4096,("x",1)),WorkerInfo("b",4,4096,("x",2))];w[0].active_jobs.add("old");assert PriorityPolicy().choose(j(),w).worker_id=="b"
def test_resource():
 w=[WorkerInfo("a",4,4096,("x",1)),WorkerInfo("b",2,2048,("x",2))];assert PriorityResourcePolicy().choose(j(),w).worker_id=="a"
