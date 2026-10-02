import argparse,socket,threading
from protocols.messages import encode,decode
from .models import WorkerInfo
from .worker_registry import WorkerRegistry
from .policies import build_policy
from .scheduler import Scheduler

class Conn:
    def __init__(self,sock):self.sock=sock;self.lock=threading.Lock()
    def send(self,job):
        with self.lock:self.sock.sendall(encode({"type":"job","job":job}))

class Server:
    def __init__(self,args):
        self.registry=WorkerRegistry(args.heartbeat_timeout);self.scheduler=Scheduler(self.registry,build_policy(args.policy));self.host=args.host;self.port=args.port
    def start(self):
        self.scheduler.start(); s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind((self.host,self.port));s.listen();print(f"Scheduler listening on {self.host}:{self.port}")
        try:
            while True:
                c,a=s.accept();threading.Thread(target=self.handle,args=(c,a),daemon=True).start()
        except KeyboardInterrupt:pass
        finally:self.scheduler.stop();s.close()
    def handle(self,c,a):
        wid=None
        try:
            for line in c.makefile("rb"):
                m=decode(line);t=m.get("type")
                if t=="register":
                    wid=m["worker_id"];self.registry.register(WorkerInfo(wid,int(m.get("cpu",1)),int(m.get("memory",128)),a));self.scheduler.attach(wid,Conn(c));c.sendall(encode({"type":"registered","worker_id":wid}))
                elif t=="heartbeat":self.registry.heartbeat(m["worker_id"])
                elif t=="result":self.scheduler.complete(m["job_id"],m["worker_id"],m["status"],m.get("error"))
                elif t=="submit":
                    j=self.scheduler.submit(m.get("task_type","sleep"),m.get("payload",{}),int(m.get("priority",0)),int(m.get("required_cpu",1)),int(m.get("required_memory",128)),int(m.get("max_retries",2)));c.sendall(encode({"type":"submitted","job":j.to_dict()}))
                elif t=="status":c.sendall(encode({"type":"status","status":self.scheduler.status()}))
        except (OSError,ConnectionResetError):pass
        finally:
            if wid:self.scheduler.detach(wid)
            c.close()

def main():
    p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9000);p.add_argument("--policy",choices=["fifo","priority","priority_resource"],default="priority_resource");p.add_argument("--heartbeat-timeout",type=float,default=5);a=p.parse_args();Server(a).start()
if __name__=="__main__":main()
