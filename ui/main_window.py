import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gio

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,title = "GGDB_X86")
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
        ''' Todo add later '''
        print(dialog.get_filename())
    
    def addScrolledWindows(self):
       grid = Gtk.Grid()
       box_primary = Gtk.Box()
       box_secondary = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
       code = ScrollWindow()
       registers = ScrollWindow()
       memory = ScrollWindow()
       stack = ScrollWindow()

       grid.add(box_primary)
       grid.add(Gtk.Separator(orientation = Gtk.Orientation.VERTICAL))
       grid.attach_next_to(box_secondary,box_primary,Gtk.PositionType.RIGHT,1,1)
       
       box_primary.add(code)
       box_secondary.add(registers)
       box_secondary.add(Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL))
       box_secondary.add(memory)
       box_secondary.add(Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL))
       box_secondary.add(stack)
       self.add(grid)       


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
         
     
         
window  = MainWindow()
window.connect('destroy',Gtk.main_quit)
window.show_all()
Gtk.main()
