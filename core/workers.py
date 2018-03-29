import os
import re
import time
import queue
from core.constants import Constants
from threading import Thread, Event

class WriteWorker(Thread):
    write_queue = None
    read_queue = None
    write_fd = None
    event = None

    def __init__(self,write_q,read_q,wfd,evt):
        Thread.__init__(self)
        self.write_queue = write_q
        self.read_queue = read_q
        self.write_fd = wfd
        self.event = evt

    def run(self):
        timestamp = None
        command = None
        break_loop = False
        while True:
            timestamp,command,break_loop = self.write_queue.get()
            if break_loop:
                self.write_queue.task_done()
                break
            self.read_queue.put((timestamp,command,False))
            os.write(self.write_fd,command.encode('ascii'))
            os.write(self.write_fd,(Constants.SEPARATOR_COMMAND).encode('ascii'))
            self.write_queue.task_done()
            self.event.wait()
            self.event.clear()

                

class ReadWorker(Thread):
    read_queue = None
    result_queue = None
    read_fd  = None
    event = None

    def __init__(self,read_q,res_q,rfd,evt):
        Thread.__init__(self)
        self.read_queue = read_q
        self.result_queue = res_q
        self.read_fd = rfd 
        self.event = evt
        
    def run(self):
        timestamp = None
        command = None
        break_loop = False
        while True:
            timestamp,command,break_loop = self.read_queue.get()
            if break_loop:
                self.read_queue.task_done()
                break
            if command is not None:
                print(command)
                output = self.read_output()
                print(output)
                print('----------------------')
                # add code in future to put results in result queue
            self.read_queue.task_done()
            self.event.set()

    def read_output(self):
         result = ""
         data = ""
         found = False
         start_time = int(time.time())
         while True:
             data = os.read(self.read_fd,Constants.BUFF_SIZE).decode()
             if len(data) > 0:
                 found = True
                 result += data
                 search = re.search(Constants.SEPARATOR_STR,data,re.M|re.I)
                 if search:
                     break
             else:
                 found = False

             if(found == False and (int(time.time()) - start_time > 5)):
                 break
         return result 
