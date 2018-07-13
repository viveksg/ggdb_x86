import os
import time
import signal
from core.constants import Constants
from subprocess import Popen, PIPE, STDOUT
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
    utils = None
    result_event = None

    def __init__(self, op_queue, op_event):
        self.gdb_process = Popen(["gdb"], stdin=PIPE, stderr=STDOUT, stdout=PIPE, bufsize=Constants.BUFF_SIZE)
        self.pid = self.gdb_process.pid
        self.read_fd = self.gdb_process.stdout.fileno()
        self.write_fd = self.gdb_process.stdin.fileno()
        self.read_queue = Queue()
        self.write_queue = Queue()
        self.result_queue = op_queue
        self.result_event = op_event
        self.event = Event()
        self.write_worker = WriteWorker(self.write_queue, self.read_queue, self.write_fd, self.event)
        self.read_worker = ReadWorker(self.read_queue, self.read_fd, self.event, self.result_queue, self.result_event)
        self.read_worker.start()
        self.write_worker.start()

    def send_command(self, line_no, output_target, command):
        self.write_queue.put((str(int(time.time())), line_no, output_target, command + '\n', False))

    def kill_gdb_process(self):
        print('killed called')
        self.write_queue.put((str(int(time.time())), -1, None, "Break", True))
        self.write_queue.join()
        self.read_queue.put((str(int(time.time())), -1, None, "Break", True))
        self.read_queue.join()
        os.kill(self.pid, signal.SIGTERM)
