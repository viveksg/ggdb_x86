import subprocess
import re
from core.constants import Constants
from core.gdbcontroller import GDBController
from threading import Event
from queue import Queue

class Utils:
    current_executed_line = -1
    parent_dir = None
    file_name = None
    full_file_name = None
    extension = None
    gdb_controller = None
    gdb_running = False
    executable = None
    app_window = None
    op_queue = None
    op_event = None
    using_default_breakpoint = False
    breakpoints = dict()
    breakpoint_lines = dict()
    using_default_breakpoint = False
    def __init__(self, full_file_path, app):
        self.set_data(full_file_path)
        self.full_file_name = full_file_path
        self.app_window = app
        self.op_queue = Queue()
        self.op_event = Event()
        self.start_gdb_process()

    def set_data(self, file_path):
        data = self.extract_data(file_path)
        self.full_file_name = file_path
        self.parent_dir = data[Constants.FILE_PATH]
        self.file_name = data[Constants.FILE_NAME]
        self.extension = data[Constants.FILE_EXTENSION]
        self.executable = self.parent_dir+"/"+self.file_name
        print(self.parent_dir)
        print(self.file_name)
        print(self.extension)

    def generate_object_and_exec_files(self):
        self.exec_command(["nasm", "-f", "elf", "-F", "dwarf", "-g", self.parent_dir+"/"+self.file_name+self.extension])
        self.exec_command(["ld", "-m", "elf_i386", "-o", self.parent_dir+"/"+self.file_name, self.parent_dir+"/"+self.file_name+".o"])

    def exec_command(self,command_params):
        subprocess.run(command_params)
    
    def extract_data(self, file_path_data):
        length = len(file_path_data)
        dot_found = False
        fname = ""
        ext = ""
        location = ""
        for i in range(length-1,-1,-1):
           if file_path_data[i] == '.' and not dot_found:
               dot_found = True
               ext = "." + ext
               continue
           if file_path_data[i] == '/':
               break
           if dot_found:
               fname = file_path_data[i] + fname
           else:
               ext = file_path_data[i] + ext
        location = file_path_data[0:i]
        extracted_data = dict()
        extracted_data[Constants.FILE_PATH] = location 
        extracted_data[Constants.FILE_NAME] = fname
        extracted_data[Constants.FILE_EXTENSION] = ext
        return extracted_data
      
    def start_gdb_process(self):
        if not self.gdb_running:
            self.gdb_controller = GDBController(self.op_queue,self.op_event)
            self.gdb_running = True
    
    def set_up_debugger(self):
        self.generate_object_and_exec_files()
        self.add_executable_to_gdb()
        self.apply_breakpoints()
        self.start_execution()

    def add_executable_to_gdb(self):
        self.gdb_controller.send_command(-1,None,"file "+self.executable)
    
    def add_breakpoint(self, line_no):
        self.breakpoint_lines[line_no] = line_no
        self.breakpoints[line_no] = self.full_file_name+":"+str(line_no)

    def remove_breakpoint(self,line_no):
        del self.breakpoints[line_no]

    def apply_breakpoints(self):
        if len(self.breakpoints) > 0:
            for breakpoint in self.breakpoints:
                  self.send_breakpoint(self.breakpoints[breakpoint])
        else:
            self.using_default_breakpoint = True
            self.send_breakpoint("_start")

    def send_breakpoint(self, bp):
        self.gdb_controller.send_command(-1,None,"break "+bp)
                
    def remove_all_breakpoints(self):
        self.breakpoints.clear()
        self.breakpoint_lines.clear()
        self.using_default_breakpoint = False
    
    
    def start_execution(self):
        self.gdb_controller.send_command(-1,None,"run")
   
    def execute_next_statement(self,line_no):
        command = "next" if self.using_default_breakpoint else "continue"
        self.send_command_to_gdb(-1,Constants.TARGET_LINE_NO,"frame")
        self.send_command_to_gdb(line_no,Constants.TARGET_REGISTER,"info registers")
        self.send_command_to_gdb(-1,None,command)
    
    def send_command_to_gdb(self,req_no,request_type,command):
        self.gdb_controller.send_command(req_no,request_type, command)
        if request_type is not None:
            self.wait_for_output(req_no)
    
    def stop_current_program(self):
        self.gdb_controller.send_command(-1,None,"kill")
        self.gdb_controller.send_command(-1,None,"Y")

    def quit_gdb(self):
       # self.gdb_controller.send_command("quit")
        self.gdb_controller.kill_gdb_process()

    def wait_for_output(self, expected_line):
        while True:
             lno,op_target,op = self.op_queue.get()
             if expected_line == lno:
                self.op_event.set()
                self.op_queue.task_done()
                self.display_output(lno,op_target,op)
                break

    def display_output(self, line_no, output_target, output):
        print(output)
        if output_target == Constants.TARGET_STACK:
            self.app_window.show_stack_output(line_no, output)
        elif output_target == Constants.TARGET_MEMORY:
            self.app_window.show_memory_output(line_no, output)
        elif output_target == Constants.TARGET_REGISTER:
            self.app_window.show_register_output(line_no, output)
        elif output_target == Constants.TARGET_LINE_NO:
            line = self.get_current_executed_line(output)
            if line > -1:
                if line > self.current_executed_line:
                    self.current_executed_line = line
                    print("line no ====>"+str(line))
                    self.app_window.set_current_executed_data(self.current_executed_line)
            else:
                if line == Constants.EXECUTION_COMPLETE:
                    self.app_window.set_execution_complete()

    def get_current_executed_line(self,data):
        data = data.strip()
        if data is None or len(data) == 0:
            return -1

        no_stack = re.findall('No Stack',data,re.M|re.I)
        if no_stack:
             return Constants.EXECUTION_COMPLETE

        line = 0
        str_line = None
        lines = re.findall(':[0-9]+',data)

        if lines is not None:
            if lines[0] is not None:
                  str_line = lines[0][1:]
        if str_line is not None:
            line = int(str_line)

        return line - 1;
        
    def reset(self):
        self.current_executed_line = -1
    
    @staticmethod
    def convert_to_zero_index(value):
        if value > 0:
            return value - 1
        return 0

    @staticmethod
    def convert_to_one_index(value):
        return value + 1

   
    
