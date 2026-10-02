from dataclasses import dataclass, field
from time import monotonic

@dataclass
class Job:
    job_id: str
    task_type: str
    payload: dict
    priority: int = 0
    required_cpu: int = 1
    required_memory: int = 128
    max_retries: int = 2
    attempts: int = 0
    status: str = "queued"
    worker_id: str | None = None
    created_at: float = field(default_factory=monotonic)
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None

    def to_dict(self):
        return self.__dict__.copy()

@dataclass
class WorkerInfo:
    worker_id: str
    cpu_capacity: int
    memory_capacity: int
    address: tuple
    last_heartbeat: float = field(default_factory=monotonic)
    active_jobs: set = field(default_factory=set)
    used_cpu: int = 0
    used_memory: int = 0
    alive: bool = True

    def can_run(self, job):
        return (self.alive and self.used_cpu + job.required_cpu <= self.cpu_capacity
                and self.used_memory + job.required_memory <= self.memory_capacity)

    @property
    def cpu_utilization(self):
        return self.used_cpu / max(self.cpu_capacity, 1)
