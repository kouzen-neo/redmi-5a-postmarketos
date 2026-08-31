"""TubeMobile Touch Video Card Component"""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Pango
from tubemobile.core.cache import ThumbnailCache

class VideoCard(Gtk.Box):
    def __init__(self, video_data, on_click_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.video_data = video_data
        self.on_click_callback = on_click_callback

        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(6)
        self.set_margin_bottom(14)
        self.add_css_class("card")
        self.add_css_class("activatable")

        # 1. Thumbnail Container with Duration Overlay
        overlay = Gtk.Overlay()
        overlay.set_hexpand(True)

        # Picture / Thumbnail
        self.picture = Gtk.Picture()
        self.picture.set_content_fit(Gtk.ContentFit.COVER)
        self.picture.set_size_request(-1, 195) # 16:9 proportional height for 720px width
        self.picture.add_css_class("rounded-thumbnail")
        overlay.set_child(self.picture)

        # Duration Badge Overlay
        if video_data.get("duration"):
            duration_label = Gtk.Label(label=video_data["duration"])
            duration_label.add_css_class("duration-badge")
            duration_label.set_halign(Gtk.Align.END)
            duration_label.set_valign(Gtk.Align.END)
            duration_label.set_margin_end(8)
            duration_label.set_margin_bottom(8)
            overlay.add_overlay(duration_label)

        self.append(overlay)

        # 2. Video Info (Title, Author, Views)
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        info_box.set_margin_start(8)
        info_box.set_margin_end(8)
        info_box.set_margin_bottom(6)

        # Channel Avatar placeholder
        avatar = Adw.Avatar(size=36, text=video_data.get("author", "Y"))
        avatar.set_valign(Gtk.Align.START)
        avatar.set_margin_top(2)
        info_box.append(avatar)

        # Details Text Box
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        text_box.set_hexpand(True)

        # Title
        title_label = Gtk.Label(label=video_data.get("title", ""))
        title_label.set_wrap(True)
        title_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        title_label.set_max_width_chars(32)
        title_label.set_lines(2)
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_xalign(0)
        title_label.add_css_class("video-title")
        text_box.append(title_label)

        # Channel + Views Subtitle
        meta_parts = []
        if video_data.get("author"):
            meta_parts.append(video_data["author"])
        if video_data.get("views"):
            meta_parts.append(video_data["views"])
        if video_data.get("published"):
            meta_parts.append(video_data["published"])
        
        meta_text = " • ".join(meta_parts)
        meta_label = Gtk.Label(label=meta_text)
        meta_label.set_xalign(0)
        meta_label.set_ellipsize(Pango.EllipsizeMode.END)
        meta_label.add_css_class("dim-label")
        meta_label.add_css_class("caption")
        text_box.append(meta_label)

        info_box.append(text_box)
        self.append(info_box)

        # 3. Touch Gesture Click Recognizer
        gesture = Gtk.GestureClick()
        gesture.connect("released", self._on_card_clicked)
        self.add_controller(gesture)

        # 4. Asynchronously Load Thumbnail
        thumb_url = video_data.get("thumbnail_url", "")
        if thumb_url:
            ThumbnailCache.get_thumbnail_async(thumb_url, self._on_thumbnail_loaded)

    def _on_thumbnail_loaded(self, local_path):
        try:
            texture = Gdk.Texture.new_from_filename(local_path)
            self.picture.set_paintable(texture)
        except Exception:
            pass

    def _on_card_clicked(self, gesture, n_press, x, y):
        if self.on_click_callback:
            self.on_click_callback(self.video_data)
