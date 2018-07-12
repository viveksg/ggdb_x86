

class Output:
    execution_no = None
    line_no = None
    reg_data = None
    mem_data = None
    stack_data = None
     
    def __init__(self,req_no, lno):
        self.execution_no = req_no
        self.line_no = lno

    def set_reg_data(self, data):
        self.reg_data = data
   
    def set_mem_data(self, data):
        self.mem_data = data
    
    def set_stack_data(self, data):
        self.stack_data = data
