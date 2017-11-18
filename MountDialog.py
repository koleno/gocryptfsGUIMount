import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Constants import APP_NAME, WINDOW_BORDER, WIDGET_SPACING


class MountDialog(Gtk.Dialog):
    """ Shows spinner while running gocryptfs mount """

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, APP_NAME, parent)
        self.set_border_width(WINDOW_BORDER)
        self.set_resizable(False)
        self.connect('delete_event', self.quit)

        self.box = self.get_content_area()
        self.box.set_spacing(WIDGET_SPACING)

        self.spinner = Gtk.Spinner()
        self.spinner.start()
        self.box.add(self.spinner)

        self.label = Gtk.Label("Mounting ...")
        self.box.add(self.label)

    def quit(self, widget, event=None):
        return True # prevent closing

    def run(self):
        self.show_all()
        self.set_modal(True)

