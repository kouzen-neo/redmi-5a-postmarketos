"""TubeMobile Home & Trending Video Feed View"""
import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from tubemobile.core.api import YouTubeAPI
from tubemobile.ui.views.video_card import VideoCard

class HomeView(Gtk.Box):
    def __init__(self, on_video_select, is_trending=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_video_select = on_video_select
        self.is_trending = is_trending

        # Header Box with Refresh Button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_start(16)
        header_box.set_margin_end(16)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(8)

        title_text = "Trending YouTube" if is_trending else "Rekomendasi Video"
        title_label = Gtk.Label(label=title_text)
        title_label.add_css_class("title-2")
        title_label.set_hexpand(True)
        title_label.set_xalign(0)
        header_box.append(title_label)

        # Refresh button
        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_btn.add_css_class("flat")
        refresh_btn.add_css_class("circular")
        refresh_btn.connect("clicked", lambda b: self.load_feed())
        header_box.append(refresh_btn)

        self.append(header_box)

        # Loading Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(36, 36)
        self.spinner.set_margin_top(30)
        self.spinner.set_margin_bottom(30)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.append(self.spinner)

        # Scrolled Feed Container
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.scroll.set_hexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Inner Box for Video Cards
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.list_box.set_margin_top(4)
        self.list_box.set_margin_bottom(20)
        self.scroll.set_child(self.list_box)
        self.append(self.scroll)

        # Auto-load feed on init
        self.load_feed()

    def load_feed(self):
        """Fetch feed asynchronously without freezing UI"""
        self.spinner.set_visible(True)
        self.spinner.start()

        # Clear existing cards
        while self.list_box.get_first_child():
            self.list_box.remove(self.list_box.get_first_child())

        def _fetch_worker():
            videos = YouTubeAPI.get_trending()
            GLib.idle_add(self._on_feed_loaded, videos)

        threading.Thread(target=_fetch_worker, daemon=True).start()

    def _on_feed_loaded(self, videos):
        self.spinner.stop()
        self.spinner.set_visible(False)

        if not videos:
            empty_status = Adw.StatusPage(
                title="Tidak Ada Video",
                description="Periksa koneksi internet Anda dan coba lagi.",
                icon_name="network-offline-symbolic"
            )
            self.list_box.append(empty_status)
            return

        for v in videos:
            card = VideoCard(v, self.on_video_select)
            self.list_box.append(card)
