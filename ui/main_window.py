import sys
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gio

class MainWindow(Gtk.ApplicationWindow):
    code = None
    registers = None
    stack = None
    memory = None 
    current_file_loc = None
    tags = dict()
    tags_selection = dict()
    colors = ["orange","white"]
    file_opened = False
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

        open = Gtk.Button.new_with_label('Open')
        open.connect('clicked',self.handleOpenClick)
        left_box.add(open)

        run = ImageButton("system-run-symbolic")
        prev = ImageButton("go-previous-symbolic")
        next = ImageButton("go-next-symbolic")
        stop = ImageButton("process-stop-symbolic")
        
        right_box.add(run)
        right_box.add(prev)
        right_box.add(next)
        right_box.add(stop)
        
        
        header.pack_start(left_box)
        header.pack_end(right_box)
    
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
        file = open(self.current_file_loc,"r")
        self.code.setText(file)
        self.file_opened = True
        self.initTags()
        file.close()
    
    def initTags(self):
        buffer = self.code.getTextBuffer()
        total_line = buffer.get_line_count()
        for i in range(total_line+1):
           self.tags[i] = None
           self.tags_selection[i] = -1    
    
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

class ImageButton(Gtk.Button):
    def __init__(self,icon_name):
         Gtk.Button.__init__(self)
         icon = Gio.ThemedIcon(name = icon_name)
         image = Gtk.Image.new_from_gicon(icon,Gtk.IconSize.BUTTON)
         self.add(image)

class ScrollWindow(Gtk.ScrolledWindow):
    text_view = None
    def __init__(self):
         Gtk.ScrolledWindow.__init__(self)
         self.set_vexpand(True)
         self.set_hexpand(True)
         self.text_view = Gtk.TextView()
         self.add(self.text_view)

    def setText(self,file):
         buffer = self.text_view.get_buffer()
         buffer.set_text(file.read())
    
    def registerCallback(self,handler):
         window = self.text_view.get_window(Gtk.TextWindowType.TEXT)
         #self.add_events(Gdk.BUTTON_PRESS_MASK)
         self.connect('button-press-event', handler)
         #self.connect('clicked',handler)
    def getTextBuffer(self):
         buffer = self.text_view.get_buffer()
         return buffer    
         
class MainApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
    
    def do_activate(self):
        main_window = MainWindow(self)
        main_window.show_all()
    def do_startup(self):
        Gtk.Application.do_startup(self)     

if __name__ == "__main__":
     app = MainApp()
     exit_status = app.run(sys.argv)
     sys.exit(exit_status)       
