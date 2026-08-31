"""TubeMobile Application Entrypoint"""
import sys
import os
import signal
import gi

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib
from tubemobile.ui.window import TubeMobileWindow

class TubeMobileApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.kouzen.tubemobile",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = TubeMobileWindow(self)
        win.present()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Initialize GTK4 & Libadwaita display connection
    Gtk.init()
    Adw.init()
    
    app = TubeMobileApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
