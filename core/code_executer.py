import subprocess

class CodeExecuter:
    parent_dir = None
    file_name = None
    extension = None
    def __init__(self, dir_loc,fname,ext):
        self.parent_dir = dir_loc
        self.file_name = fname
        self.extension = ext

    def generate_object_and_exec_files(self):
        self.exec_command(["nasm", "-f", "elf", "-F", "dwarf", "-g", self.parent_dir+"/"+self.file_name+self.extension])
        self.exec_command(["ld", "-m", "elf_i386", "-o", self.parent_dir+"/"+self.file_name, self.parent_dir+"/"+self.file_name+".o"])

    def exec_command(self,command_params):
        subprocess.run(command_params)
    
    def extract(self,data):
        length = len(data)
        dot_found = False
        fname = ""
        for i in range(length-1,-1,-1):
           if data[i] == '.' and not dot_found:
               dot_found = True
               continue
           if data[i] == '/':
               break
           if dot_found:
               fname = data[i]+fname
        print(fname)   
          



   
    
