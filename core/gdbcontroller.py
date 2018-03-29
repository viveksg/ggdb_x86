import os
import time
import signal
from core.constants import Constants
from subprocess import Popen,PIPE,STDOUT
from queue import Queue
from threading import Event
from core.workers import ReadWorker
from core.workers import WriteWorker

class GDBController:
    gdb_process = None
    pid = None
    read_fd = None
    write_fd = None
    read_queue = None
    write_queue = None
    result_queue = None
    event = None
    read_worker = None
    write_worker = None
    
    def __init__(self):
        self.gdb_process = Popen(["gdb"],stdin = PIPE, stderr = STDOUT,stdout = PIPE,bufsize = Constants.BUFF_SIZE)
        self.pid =  self.gdb_process.pid
        self.read_fd = self.gdb_process.stdout.fileno()
        self.write_fd = self.gdb_process.stdin.fileno()
        self.read_queue = Queue()
        self.write_queue = Queue()
        self.result_queue = Queue()
        self.event = Event()
        self.write_worker = WriteWorker(self.write_queue,self.read_queue,self.write_fd,self.event)
        self.read_worker = ReadWorker(self.read_queue,self.result_queue,self.read_fd,self.event)
        self.read_worker.start()
        self.write_worker.start()

    def send_command(self,command):
        self.write_queue.put((str(int(time.time())),command+'\n',False))

    def kill_gdb_process(self):
        print('killed called')
        self.write_queue.put((str(int(time.time())),"Break",True))
        self.write_queue.join()
        self.read_queue.put((str(int(time.time())),"Break",True))
        self.read_queue.join()
        os.kill(self.pid,signal.SIGTERM)
                             
        
