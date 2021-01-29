"""
    Simple GUI for mounting gocrypfts folders written in Python3 and GTK.
    Author: Dusan Koleno
    Licence: GNU General Public License v2.0
"""

import threading
import gi
from MountDialog import MountDialog
from gi.repository import Gtk, GLib
import subprocess
from Constants import APP_NAME, WINDOW_BORDER, WIDGET_SPACING, LABEL_SIZE, GOCRYPTFS_CMD, ICON
from Config import Config

gi.require_version("Gtk", "3.0")


class Window(Gtk.Window):
    """ Creates main window """

    mount_dialog = None

    def __init__(self):
        Gtk.Window.__init__(self, title=APP_NAME)
        self.set_icon_from_file(ICON)
        self.set_border_width(WINDOW_BORDER)
        self.set_resizable(False)
        self.connect("delete_event", Gtk.main_quit)

        self.config = Config()
        self.mount_folder = self.config.mount_folder
        self.cipher_folder = self.config.cipher_folder

        button_box = Gtk.HBox(False, 0)
        ok_button = Gtk.Button("Mount")
        ok_button.connect("clicked", self.mount_clicked)
        cancel_button = Gtk.Button("Close")
        cancel_button.connect("clicked", Gtk.main_quit)
        button_box.pack_start(ok_button, expand=True, fill=True, padding=WIDGET_SPACING)
        button_box.pack_end(cancel_button, expand=True, fill=True, padding=WIDGET_SPACING)

        cipher_box = Gtk.HBox(False, 0)
        self.cipher_button = Gtk.Button("Choose...")
        if len(self.cipher_folder) > 0:
            self.cipher_button.set_label(self.cipher_folder)
        self.cipher_button.connect("clicked", self.show_chooser_dialog)
        cipher_label = Gtk.Label("gocryptfs Folder:")
        cipher_label.set_alignment(1, 0.5)
        cipher_label.set_width_chars(LABEL_SIZE)
        cipher_box.pack_start(cipher_label, expand=False, fill=False, padding=WIDGET_SPACING)
        cipher_box.pack_end(self.cipher_button, expand=False, fill=False, padding=WIDGET_SPACING)

        mount_box = Gtk.HBox(False, 0)
        self.mount_button = Gtk.Button("Choose...")
        if len(self.mount_folder) > 0:
            self.mount_button.set_label(self.mount_folder)
        self.mount_button.connect("clicked", self.show_chooser_dialog)
        mount_label = Gtk.Label("Mount Folder:")
        mount_label.set_alignment(1, 0.5)
        mount_label.set_width_chars(LABEL_SIZE)
        mount_box.pack_start(mount_label, expand=False, fill=False, padding=WIDGET_SPACING)
        mount_box.pack_end(self.mount_button, expand=False, fill=False, padding=WIDGET_SPACING)

        pass_box = Gtk.HBox(False, 0)
        pass_label = Gtk.Label("Password:")
        pass_label.set_alignment(1, 0.5)
        pass_label.set_width_chars(LABEL_SIZE)
        self.pass_entry = Gtk.Entry()
        self.pass_entry.set_visibility(False)
        self.pass_entry.connect("activate", self.mount_clicked)  # enter pressed in pass_entry
        pass_box.pack_start(pass_label, expand=False, fill=False, padding=WIDGET_SPACING)
        pass_box.pack_end(self.pass_entry, expand=True, fill=True, padding=WIDGET_SPACING)

        main_box = Gtk.VBox(False, WIDGET_SPACING)
        main_box.add(cipher_box)
        main_box.add(mount_box)
        main_box.add(pass_box)
        main_box.add(button_box)

        self.add(main_box)
        self.show_all()

        self.pass_entry.grab_focus()  # set focus to password entry

    def show_chooser_dialog(self, widget):
        chooser = Gtk.FileChooserDialog("Choose Folder", self, Gtk.FileChooserAction.SELECT_FOLDER,
                                        (Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
                                         Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        response = chooser.run()

        if response == Gtk.ResponseType.OK:
            widget.set_label(chooser.get_filename())
            if widget == self.mount_button:
                self.mount_folder = chooser.get_filename()
            else:
                self.cipher_folder = chooser.get_filename()

        chooser.destroy()

    def mount_clicked(self, widget, data=None):
        if len(self.cipher_folder) == 0 or len(self.mount_folder) == 0:
            self.show_dialog("Select both folders")
            return

        if self.cipher_folder == self.mount_folder:
            self.show_dialog("Folders cannot be the same")
            return

        if self.pass_entry.get_text_length() == 0:
            self.show_dialog("Password cannot be empty")
            return

        self.config.save(self.cipher_folder, self.mount_folder)

        self.mount_dialog = MountDialog(self)
        self.mount_dialog.run()

        thread = threading.Thread(target=self.mount)
        thread.daemon = True
        thread.start()

    def mount(self):
        cmd = subprocess.run((GOCRYPTFS_CMD, self.cipher_folder, self.mount_folder), stdout=subprocess.PIPE,
                             input=self.pass_entry.get_text().encode("ascii"))

        GLib.idle_add(self.mount_dialog.destroy)  # dismiss mount dialog

        if cmd.returncode > 0:
            GLib.idle_add(self.show_dialog, "Cannot mount! Check your folders and password.")
        else:
            GLib.idle_add(self.show_dialog, "Folder has been mounted successfully.", Gtk.MessageType.INFO)
            GLib.idle_add(Gtk.main_quit)

    def show_dialog(self, message, dialog_type=Gtk.MessageType.ERROR):
        dialog = Gtk.MessageDialog(self, 0, dialog_type, Gtk.ButtonsType.OK, message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    window = Window()
    Gtk.main()
