import sys
sys.path.append("../")
import gi
from core.utils import Utils
from core.constants import Constants
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gio,GObject


class MainWindow(Gtk.ApplicationWindow):
    code = None
    registers = None
    stack = None
    memory = None 
    current_file_loc = None
    tags = dict()
    tags_selection = dict()
    utils = None
    colors = ["orange","white"]
    file_opened = False
    current_line = -1
    highest_line_reached = -1;
    reg_cache = dict()
    stack_cache = dict()
    mem_cache = dict()
    run = None
    prev = None
    next = None
    stop = None
    open = None
    def __init__(self, app):
        Gtk.Window.__init__(self,title = "GGDB_X86",application = app)
        self.set_border_width(10)
        self.set_default_size(800,800)
        self.addHeaderBar()
        self.addScrolledWindows()

    def addHeaderBar(self):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props_title = "ToolBar"
        self.set_titlebar(header)

        left_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 6)
        right_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 6)

        self.open = Gtk.Button.new_with_label('Open')
        self.open.connect('clicked',self.handleOpenClick)
        left_box.add(self.open)

        self.run = ImageButton("system-run-symbolic")
        self.run.connect('clicked',self.handle_run_clicked)
        self.prev = ImageButton("go-previous-symbolic")
        self.prev.connect('clicked',self.handle_prev_clicked)
        self.next = ImageButton("go-next-symbolic")
        self.next.connect('clicked',self.handle_next_clicked)
        self.stop = ImageButton("process-stop-symbolic")
        self.stop.connect('clicked',self.handle_stop_clicked)
        
        right_box.add(self.run)
        right_box.add(self.prev)
        right_box.add(self.next)
        right_box.add(self.stop)
        
        
        header.pack_start(left_box)
        header.pack_end(right_box)
    
    def handle_run_clicked(self, widget):
        print('run called')
        self.disable_controls_after_start()
        self.utils.set_up_debugger()

    def handle_prev_clicked(self, widget):
        if self.current_line == 0:
            return
        self.disable_step_controls()
        self.current_line = self.current_line -1
        self.show_register_output(self.current_line,None)
        print(str(self.current_line))

    def handle_next_clicked(self, widget):
        if self.current_line == self.code.total_lines:
            return
        self.disable_step_controls()
        self.current_line = self.current_line + 1
        if self.current_line <= self.highest_line_reached:
            self.show_register_output(self.current_line,None)
        else:
           self.utils.execute_next_statement(self.current_line)
           self.highest_line_reached = self.current_line
        print(str(self.current_line))

    def handle_stop_clicked(self, widget):
        self.enable_controls_after_stop()
        print('stop called')

    def handleOpenClick(self,widget):
        file_chooser = Gtk.FileChooserDialog("Select File",self,Gtk.FileChooserAction.OPEN,     
                                            (Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        response = file_chooser.run()
        if response == Gtk.ResponseType.OK:
            self.addFileToCodeWindow(file_chooser)
        elif response == Gtk.ResponseType.CANCEL:
            print("No File Selected ...")
        
        file_chooser.destroy()
    
    def addFileToCodeWindow(self,dialog):
        self.current_file_loc = dialog.get_filename()
        if self.utils is None:
            self.utils = Utils(self.current_file_loc,self)
        else:
            self.utils.set_data(self.current_file_loc)
  
        if self.utils.extension != Constants.ASM:
            self.show_error("File format should be .asm")
            return
        
        file = open(self.current_file_loc,"r")
        if self.file_opened is True:
            self.code.removeTags(self.tags)
        self.code.set_text_from_file(file)
        self.file_opened = True
        self.initTags()
        self.clean()
        file.close()
    
    def initTags(self):
        buffer = self.code.getTextBuffer()
        total_line = buffer.get_line_count()
        for i in range(total_line+1):
           self.tags[i] = None
           self.tags_selection[i] = -1   
    
    def clean(self):
        self.current_line = -1
        self.highest_line_reached  = -1
    
    def addScrolledWindows(self):
       grid = Gtk.Grid()
       box_primary = Gtk.Box()
       box_secondary = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
       self.code = ScrollWindow()
       self.code.registerCallback(self.codeClickedHandler)
       self.registers = ScrollWindow()
       self.memory = ScrollWindow()
       self.stack = ScrollWindow()

       grid.add(box_primary)
       grid.add(Gtk.Separator(orientation = Gtk.Orientation.VERTICAL))
       grid.attach_next_to(box_secondary,box_primary,Gtk.PositionType.RIGHT,1,1)
       
       box_primary.add(self.code)
       box_secondary.add(self.registers)
       box_secondary.add(Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL))
       box_secondary.add(self.memory)
       box_secondary.add(Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL))
       box_secondary.add(self.stack)
       self.add(grid)    
  
    def codeClickedHandler(self,widget,data):
       if not self.file_opened:
           return
       buffer = self.code.getTextBuffer()
       current_line = self.getCurrentLine(buffer)
       self.addTag(buffer, current_line)
   
    def getCurrentLine(self,buffer):
       buffer_props = buffer.props
       current_iter = buffer.get_iter_at_offset(buffer_props.cursor_position)
       current_line = current_iter.get_line()
       return current_line
   
    def addTag(self,buffer,current_line):
       self.tags_selection[current_line] = (self.tags_selection[current_line] + 1) % 2
       if self.tags[current_line] is None:
           self.tags[current_line]  = buffer.create_tag("tag_"+str(current_line),background = "orange")
           buffer.apply_tag(self.tags[current_line],buffer.get_iter_at_line(current_line),buffer.get_iter_at_line(current_line + 1)) 
           return
       self.tags[current_line].props.background = self.colors[self.tags_selection[current_line]]

    def show_error(self, message):
        error = Gtk.MessageDialog(self,0,Gtk.MessageType.ERROR,Gtk.ButtonsType.CANCEL,message)
        error.run()
        error.destroy()
    
    def show_stack_output(self,line_no,output):
        self.stack.set_text(output)
   
    def show_memory_output(self,line_no,output):
        self.memory.set_text(output) 
        
    def show_register_output(self,line_no,output):
        self.enable_step_controls()
        if output is None:
           output = self.reg_cache[line_no]
        else:
           self.reg_cache[line_no] = output
        self.registers.set_text(output)
        
    def disable_step_controls(self):
        self.next.set_sensitive(False)
        self.prev.set_sensitive(False)
    
    def enable_step_controls(self):
        self.next.set_sensitive(True)
        self.prev.set_sensitive(True)
       
    def disable_controls_after_start(self):
        self.open.set_sensitive(False)
        self.run.set_sensitive(False)
        self.next.set_sensitive(True)
        self.prev.set_sensitive(False)
        self.stop.set_sensitive(True)

    def enable_controls_after_stop(self):
        self.open.set_sensitive(True)
        self.run.set_sensitive(True)
        self.next.set_sensitive(False)
        self.prev.set_sensitive(False)
        self.stop.set_sensitive(False)

    def close_gdb(self):
        print('closing gdb')
        self.utils.quit_gdb()

class ImageButton(Gtk.Button):
    def __init__(self,icon_name):
         Gtk.Button.__init__(self)
         icon = Gio.ThemedIcon(name = icon_name)
         image = Gtk.Image.new_from_gicon(icon,Gtk.IconSize.BUTTON)
         self.add(image)

class ScrollWindow(Gtk.ScrolledWindow):
    text_view = None
    total_lines = 0
    def __init__(self):
         Gtk.ScrolledWindow.__init__(self)
         self.set_vexpand(True)
         self.set_hexpand(True)
         self.text_view = Gtk.TextView()
         self.add(self.text_view)

    def set_text_from_file(self,file):
         buffer = self.text_view.get_buffer()
         buffer.set_text(file.read())
         self.total_lines = buffer.get_line_count()

    def set_text(self,data):
         buffer = self.text_view.get_buffer()
         buffer.set_text(data)
    
    def registerCallback(self,handler):
         window = self.text_view.get_window(Gtk.TextWindowType.TEXT)
         self.connect('button-press-event', handler)

    def getTextBuffer(self):
         buffer = self.text_view.get_buffer()
         return buffer   
   
    def removeTags(self,tags):
         buffer = self.text_view.get_buffer()
         tag_table = buffer.get_tag_table()
         for i in range(self.total_lines + 1):
            if tags[i] is not None:
                tag_table.remove(tags[i])

         
class MainApp(Gtk.Application):
    main_window = None
    def __init__(self):
        Gtk.Application.__init__(self)
    
    def do_activate(self):
        self.main_window = MainWindow(self)
        self.main_window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)     

    def do_shutdown(self):
        print("app quit_called..")
        self.main_window.close_gdb()
        Gtk.Application.do_shutdown(self)

if __name__ == "__main__":
     app = MainApp()
    # GObject.threads_init()
     exit_status = app.run(sys.argv)
     sys.exit(exit_status)       
