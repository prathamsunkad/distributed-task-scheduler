from abc import ABC, abstractmethod

class SchedulingPolicy(ABC):
    @abstractmethod
    def choose(self, job, workers): ...

class FIFOPolicy(SchedulingPolicy):
    def choose(self, job, workers):
        return next((w for w in workers if w.can_run(job)), None)

class PriorityPolicy(SchedulingPolicy):
    def choose(self, job, workers):
        c=[w for w in workers if w.can_run(job)]
        return min(c, key=lambda w:(len(w.active_jobs),w.cpu_utilization), default=None)

class PriorityResourcePolicy(SchedulingPolicy):
    def choose(self, job, workers):
        c=[w for w in workers if w.can_run(job)]
        def score(w):
            cpu=1-w.cpu_utilization; mem=1-w.used_memory/max(w.memory_capacity,1)
            return (cpu+mem,cpu,-len(w.active_jobs))
        return max(c,key=score,default=None)

def build_policy(name):
    return {"fifo":FIFOPolicy,"priority":PriorityPolicy,"priority_resource":PriorityResourcePolicy}[name]()
