import random

def generate_workload(count,seed=7):
    r=random.Random(seed);out=[]
    for i in range(count):
        t=r.choice(["sleep","cpu","fibonacci"]);p={"seconds":round(r.uniform(.05,.5),3)} if t!="fibonacci" else {"n":r.randint(28,34)}
        out.append({"task_type":t,"payload":p,"priority":10 if r.random()<.15 else r.randint(0,5),"required_cpu":r.choice([1,1,2]),"required_memory":r.choice([128,256,512])})
    return out
