import argparse,socket,threading
from protocols.messages import encode,decode
from .executor import execute

class Worker:
    def __init__(self,wid,host,port,cpu,memory,interval=1):self.wid=wid;self.host=host;self.port=port;self.cpu=cpu;self.memory=memory;self.interval=interval;self.sock=None;self.stop=threading.Event();self.lock=threading.Lock()
    def send(self,m):
        with self.lock:self.sock.sendall(encode(m))
    def heartbeat(self):
        while not self.stop.wait(self.interval):
            try:self.send({"type":"heartbeat","worker_id":self.wid})
            except OSError:return
    def run_job(self,j):
        try:r=execute(j["task_type"],j.get("payload",{}));self.send({"type":"result","job_id":j["job_id"],"worker_id":self.wid,"status":"success","result":r})
        except Exception as e:self.send({"type":"result","job_id":j["job_id"],"worker_id":self.wid,"status":"failed","error":repr(e)})
    def run(self):
        self.sock=socket.create_connection((self.host,self.port));self.send({"type":"register","worker_id":self.wid,"cpu":self.cpu,"memory":self.memory});threading.Thread(target=self.heartbeat,daemon=True).start()
        try:
            for line in self.sock.makefile("rb"):
                m=decode(line)
                if m.get("type")=="job":threading.Thread(target=self.run_job,args=(m["job"],),daemon=True).start()
        finally:self.stop.set();self.sock.close()

def main():
    p=argparse.ArgumentParser();p.add_argument("--worker-id",required=True);p.add_argument("--scheduler",default="127.0.0.1:9000");p.add_argument("--cpu",type=int,default=2);p.add_argument("--memory",type=int,default=2048);p.add_argument("--heartbeat-interval",type=float,default=1);a=p.parse_args();h,po=a.scheduler.rsplit(":",1);Worker(a.worker_id,h,int(po),a.cpu,a.memory,a.heartbeat_interval).run()
if __name__=="__main__":main()
