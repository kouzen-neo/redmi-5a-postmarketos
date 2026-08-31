"""TubeMobile Application Entrypoint"""
import sys
import os
import signal
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib
from tubemobile.ui.window import TubeMobileWindow

class TubeMobileApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.kouzen.tubemobile",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = TubeMobileWindow(self)
        win.present()

def main():
    # Handle Ctrl+C cleanly
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = TubeMobileApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
