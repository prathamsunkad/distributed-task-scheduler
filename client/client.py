import argparse,socket
from protocols.messages import encode,decode

def request(host,port,m):
    with socket.create_connection((host,port)) as s:s.sendall(encode(m));return decode(s.makefile("rb").readline())

def main():
    p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9000);sp=p.add_subparsers(dest="cmd",required=True)
    q=sp.add_parser("submit");q.add_argument("--type",choices=["sleep","cpu","fibonacci"],default="sleep");q.add_argument("--seconds",type=float,default=1);q.add_argument("--n",type=int,default=30);q.add_argument("--priority",type=int,default=0);q.add_argument("--cpu",type=int,default=1);q.add_argument("--memory",type=int,default=128);q.add_argument("--max-retries",type=int,default=2);sp.add_parser("status");a=p.parse_args()
    if a.cmd=="submit":m={"type":"submit","task_type":a.type,"payload":{"seconds":a.seconds,"n":a.n},"priority":a.priority,"required_cpu":a.cpu,"required_memory":a.memory,"max_retries":a.max_retries}
    else:m={"type":"status"}
    print(request(a.host,a.port,m))
if __name__=="__main__":main()
