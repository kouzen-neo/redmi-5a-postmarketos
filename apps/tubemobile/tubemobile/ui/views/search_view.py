"""TubeMobile Search View"""
import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from tubemobile.core.api import YouTubeAPI
from tubemobile.ui.views.video_card import VideoCard

class SearchView(Gtk.Box):
    def __init__(self, on_video_select):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_video_select = on_video_select

        # Search Bar Box
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        search_box.set_margin_start(14)
        search_box.set_margin_end(14)
        search_box.set_margin_top(12)
        search_box.set_margin_bottom(8)

        # Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Telusuri YouTube...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("activate", self._on_search_submitted)
        search_box.append(self.search_entry)

        # Search Action Button
        search_btn = Gtk.Button.new_from_icon_name("system-search-symbolic")
        search_btn.add_css_class("suggested-action")
        search_btn.connect("clicked", lambda b: self._on_search_submitted(self.search_entry))
        search_box.append(search_btn)

        self.append(search_box)

        # Loading Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(32, 32)
        self.spinner.set_margin_top(20)
        self.spinner.set_margin_bottom(20)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_visible(False)
        self.append(self.spinner)

        # Scrolled Results Container
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.scroll.set_hexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.list_box.set_margin_top(4)
        self.list_box.set_margin_bottom(20)
        self.scroll.set_child(self.list_box)
        self.append(self.scroll)

        # Initial Status
        self.status_page = Adw.StatusPage(
            title="Cari Video Favorit",
            description="Ketik kata kunci pencarian di atas untuk menemukan video.",
            icon_name="system-search-symbolic"
        )
        self.list_box.append(self.status_page)

    def _on_search_submitted(self, entry):
        query = entry.get_text().strip()
        if not query:
            return

        self.spinner.set_visible(True)
        self.spinner.start()

        # Clear existing cards
        while self.list_box.get_first_child():
            self.list_box.remove(self.list_box.get_first_child())

        def _search_worker():
            results = YouTubeAPI.search(query)
            GLib.idle_add(self._on_search_completed, results)

        threading.Thread(target=_search_worker, daemon=True).start()

    def _on_search_completed(self, results):
        self.spinner.stop()
        self.spinner.set_visible(False)

        if not results:
            empty = Adw.StatusPage(
                title="Hasil Tidak Ditemukan",
                description="Coba gunakan kata kunci pencarian yang lain.",
                icon_name="edit-find-symbolic"
            )
            self.list_box.append(empty)
            return

        for v in results:
            card = VideoCard(v, self.on_video_select)
            self.list_box.append(card)
