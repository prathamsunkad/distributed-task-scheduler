import math,time

def execute(task_type,payload):
    if task_type=="sleep":
        x=float(payload.get("seconds",1));time.sleep(x);return {"slept":x}
    if task_type=="cpu":
        x=float(payload.get("seconds",1));end=time.monotonic()+x;v=0
        while time.monotonic()<end:
            for i in range(1000):v+=math.sin(i)*math.cos(i)
        return {"cpu_seconds":x,"checksum":v}
    if task_type=="fibonacci":
        n=int(payload.get("n",30));a,b=0,1
        for _ in range(n):a,b=b,a+b
        return {"n":n,"value":a}
    raise ValueError(f"unknown task type: {task_type}")
