"""TubeMobile Main Application Window with Mobile Bottom Navigation"""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk
from tubemobile.ui.views.home_view import HomeView
from tubemobile.ui.views.search_view import SearchView
from tubemobile.ui.views.player_view import PlayerView

CSS_STYLES = """
/* TubeMobile Modern Dark Mobile Theme */
window {
    background-color: #0f0f0f;
    color: #f1f1f1;
}

.rounded-thumbnail {
    border-radius: 12px;
    background-color: #1f1f1f;
}

.duration-badge {
    background-color: rgba(0, 0, 0, 0.85);
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    padding: 3px 6px;
    border-radius: 6px;
}

.video-title {
    font-weight: 600;
    font-size: 14px;
    color: #f1f1f1;
}

.dim-label {
    color: #aaaaaa;
    font-size: 12px;
}

.card {
    background-color: transparent;
    border: none;
    box-shadow: none;
}

.card:hover {
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 12px;
}
"""

class TubeMobileWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="TubeMobile")

        # Set default smartphone window size (720x1280 scale)
        self.set_default_size(360, 680)

        # Apply Mobile CSS
        self._load_css()

        # Root Box Container
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header Bar (Minimalist YouTube Red Header)
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_show_title(False)

        # Header Logo & Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        logo_icon = Gtk.Image.new_from_icon_name("video-x-generic-symbolic")
        logo_icon.set_icon_size(Gtk.IconSize.LARGE)
        title_box.append(logo_icon)

        app_title = Gtk.Label(label="TubeMobile")
        app_title.add_css_class("heading")
        title_box.append(app_title)

        self.header_bar.set_title_widget(title_box)
        root_box.append(self.header_bar)

        # Master Page Stack (Main Navigation vs Full Player)
        self.master_stack = Gtk.Stack()
        self.master_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.master_stack.set_vexpand(True)

        # 1. Main Feed View with Bottom Navigation Bar
        main_page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)

        # Subviews
        self.home_view = HomeView(on_video_select=self._on_video_selected, is_trending=False)
        self.view_stack.add_titled_with_icon(self.home_view, "home", "Beranda", "user-home-symbolic")

        self.trending_view = HomeView(on_video_select=self._on_video_selected, is_trending=True)
        self.view_stack.add_titled_with_icon(self.trending_view, "trending", "Trending", "starred-symbolic")

        self.search_view = SearchView(on_video_select=self._on_video_selected)
        self.view_stack.add_titled_with_icon(self.search_view, "search", "Cari", "system-search-symbolic")

        main_page_box.append(self.view_stack)

        # Android-Style Bottom Navigation Bar (ViewSwitcherBar)
        self.switcher_bar = Adw.ViewSwitcherBar()
        self.switcher_bar.set_stack(self.view_stack)
        self.switcher_bar.set_reveal(True)
        main_page_box.append(self.switcher_bar)

        self.master_stack.add_named(main_page_box, "main_feed")

        # 2. Player Page View
        self.player_view = PlayerView(on_back_callback=self._on_back_to_feed)
        self.master_stack.add_named(self.player_view, "player_page")

        root_box.append(self.master_stack)
        self.set_content(root_box)

    def _on_video_selected(self, video_data):
        """Navigate to video player page and load video"""
        self.player_view.load_video(video_data)
        self.header_bar.set_visible(False) # Hide top bar for player immersion
        self.master_stack.set_visible_child_name("player_page")

    def _on_back_to_feed(self):
        """Return from player back to feed view"""
        self.header_bar.set_visible(True)
        self.master_stack.set_visible_child_name("main_feed")

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_string(CSS_STYLES)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
