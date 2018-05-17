import subprocess
from core.constants import Constants
from core.gdbcontroller import GDBController

class Utils:
    parent_dir = None
    file_name = None
    extension = None
    gdb_controller = None
    gdb_running = False
    executable = None
    def __init__(self, full_file_path):
        self.set_data(full_file_path)
        self.start_gdb_process()

    def set_data(self, file_path):
        data = self.extract_data(file_path)
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
    
    def extract_data(self,data):
        length = len(data)
        dot_found = False
        fname = ""
        ext = ""
        location = ""
        for i in range(length-1,-1,-1):
           if data[i] == '.' and not dot_found:
               dot_found = True
               ext = "." + ext
               continue
           if data[i] == '/':
               break
           if dot_found:
               fname = data[i] + fname
           else:
               ext = data[i] + ext
        location = data[0:i]
        extracted_data = dict()
        extracted_data[Constants.FILE_PATH] = location 
        extracted_data[Constants.FILE_NAME] = fname
        extracted_data[Constants.FILE_EXTENSION] = ext
        return extracted_data
      
    def start_gdb_process(self):
        if not self.gdb_running:
            self.gdb_controller = GDBController()
            self.gdb_running = True
    
    def set_up_debugger(self):
        self.generate_object_and_exec_files()
        self.add_executable_to_gdb()
        self.add_breakpoints()
        self.start_execution()

    def add_executable_to_gdb(self):
        self.gdb_controller.send_command("file "+self.executable)

    def add_breakpoints(self):
        self.gdb_controller.send_command("break _start")
   
    def start_execution(self):
        self.gdb_controller.send_command("run")

    def execute_next_statement(self):
        self.gdb_controller.send_command("next")
        self.gdb_controller.send_command("info registers")  
 
    def quit_gdb(self):
       # self.gdb_controller.send_command("quit")
        self.gdb_controller.kill_gdb_process()
    

   
          



   
    
