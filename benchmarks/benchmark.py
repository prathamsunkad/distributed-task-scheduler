import argparse,socket,time
from protocols.messages import encode,decode
from .workloads import generate_workload

def submit(h,p,j):
    with socket.create_connection((h,p)) as s:s.sendall(encode({"type":"submit",**j}));return decode(s.makefile("rb").readline())

def main():
    p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9000);p.add_argument("--jobs",type=int,default=100);p.add_argument("--seed",type=int,default=7);a=p.parse_args();start=time.monotonic();ids=[]
    for j in generate_workload(a.jobs,a.seed):ids.append(submit(a.host,a.port,j)["job"]["job_id"])
    print({"submitted":len(ids),"submission_seconds":round(time.monotonic()-start,4)})
if __name__=="__main__":main()
