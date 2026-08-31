"""TubeMobile Video Player Page with Hardware MPV Controller"""
import os
import subprocess
import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gdk
from tubemobile.core.api import YouTubeAPI
from tubemobile.core.cache import ThumbnailCache

class PlayerView(Gtk.Box):
    def __init__(self, on_back_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_back_callback = on_back_callback
        self.current_video = None
        self.player_process = None

        # 1. Header Bar with Back Button
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_start(8)
        header.set_margin_end(8)
        header.set_margin_top(8)
        header.set_margin_bottom(8)

        back_btn = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        back_btn.add_css_class("flat")
        back_btn.add_css_class("circular")
        back_btn.connect("clicked", self._on_back_clicked)
        header.append(back_btn)

        self.header_title = Gtk.Label(label="Pemutar Video")
        self.header_title.add_css_class("title-3")
        self.header_title.set_hexpand(True)
        self.header_title.set_xalign(0)
        self.header_title.set_ellipsize(Gtk.Pango.EllipsizeMode.END)
        header.append(self.header_title)

        self.append(header)

        # 2. Thumbnail & Play Banner Box
        self.media_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.media_box.set_hexpand(True)

        overlay = Gtk.Overlay()
        overlay.set_hexpand(True)

        self.preview_pic = Gtk.Picture()
        self.preview_pic.set_content_fit(Gtk.ContentFit.COVER)
        self.preview_pic.set_size_request(-1, 230)
        overlay.set_child(self.preview_pic)

        # Big Touch Play Button Overlay
        play_btn = Gtk.Button.new_from_icon_name("media-playback-start-symbolic")
        play_btn.add_css_class("suggested-action")
        play_btn.add_css_class("circular")
        play_btn.set_size_request(64, 64)
        play_btn.set_halign(Gtk.Align.CENTER)
        play_btn.set_valign(Gtk.Align.CENTER)
        play_btn.connect("clicked", lambda b: self._start_video_playback())
        overlay.add_overlay(play_btn)

        self.media_box.append(overlay)
        self.append(self.media_box)

        # 3. Action Buttons (Putar Layar Penuh / Audio Only)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_start(14)
        btn_box.set_margin_end(14)
        btn_box.set_margin_top(12)
        btn_box.set_margin_bottom(10)

        self.play_main_btn = Gtk.Button(label="▶ Putar Video (Hardware GPU)")
        self.play_main_btn.add_css_class("suggested-action")
        self.play_main_btn.add_css_class("pill")
        self.play_main_btn.set_hexpand(True)
        self.play_main_btn.connect("clicked", lambda b: self._start_video_playback())
        btn_box.append(self.play_main_btn)

        self.append(btn_box)

        # 4. Video Details Section
        detail_scroll = Gtk.ScrolledWindow()
        detail_scroll.set_vexpand(True)
        detail_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        detail_box.set_margin_start(16)
        detail_box.set_margin_end(16)
        detail_box.set_margin_top(8)
        detail_box.set_margin_bottom(20)

        # Title
        self.video_title = Gtk.Label(label="")
        self.video_title.set_wrap(True)
        self.video_title.set_xalign(0)
        self.video_title.add_css_class("title-3")
        detail_box.append(self.video_title)

        # Channel & Stats
        self.video_meta = Gtk.Label(label="")
        self.video_meta.set_xalign(0)
        self.video_meta.add_css_class("dim-label")
        detail_box.append(self.video_meta)

        # Separator
        detail_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Description Expander
        self.expander = Adw.ExpanderRow()
        self.expander.set_title("Deskripsi Video")
        self.desc_label = Gtk.Label(label="")
        self.desc_label.set_wrap(True)
        self.desc_label.set_xalign(0)
        self.desc_label.set_margin_start(12)
        self.desc_label.set_margin_end(12)
        self.desc_label.set_margin_top(8)
        self.desc_label.set_margin_bottom(8)
        self.expander.add_row(self.desc_label)
        detail_box.append(self.expander)

        detail_scroll.set_child(detail_box)
        self.append(detail_scroll)

    def load_video(self, video_data):
        """Set active video data and preview thumbnail"""
        self.current_video = video_data
        self.header_title.set_label(video_data.get("title", "Pemutar Video"))
        self.video_title.set_label(video_data.get("title", ""))
        
        meta = f"{video_data.get('author', '')} • {video_data.get('views', '')} • {video_data.get('duration', '')}"
        self.video_meta.set_label(meta)
        self.desc_label.set_label(video_data.get("description", "Tidak ada deskripsi."))

        thumb_url = video_data.get("thumbnail_url", "")
        if thumb_url:
            ThumbnailCache.get_thumbnail_async(thumb_url, self._on_thumbnail_loaded)

    def _on_thumbnail_loaded(self, local_path):
        try:
            texture = Gdk.Texture.new_from_filename(local_path)
            self.preview_pic.set_paintable(texture)
        except Exception:
            pass

    def _start_video_playback(self):
        """Launch video playback in MPV with hardware OpenGL ES GPU acceleration"""
        if not self.current_video:
            return

        video_id = self.current_video.get("id", "")
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Stop existing playback if any
        if self.player_process:
            try:
                self.player_process.terminate()
            except Exception:
                pass

        # Optimized MPV options for Redmi 5A (Qualcomm Adreno 308 & Wayland 60fps)
        cmd = [
            "mpv",
            "--vo=gpu",
            "--gpu-api=opengl",
            "--gpu-context=wayland",
            "--ytdl-format=bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "--force-window=immediate",
            "--geometry=100%:100%",
            "--osc=yes", # On-screen controller for touchscreen touch/seek
            "--input-default-bindings=yes",
            video_url
        ]

        def _run_mpv():
            try:
                self.player_process = subprocess.Popen(cmd)
                self.player_process.wait()
            except Exception as e:
                print(f"MPV Error: {e}")

        threading.Thread(target=_run_mpv, daemon=True).start()

    def _on_back_clicked(self, btn):
        if self.player_process:
            try:
                self.player_process.terminate()
            except Exception:
                pass
        if self.on_back_callback:
            self.on_back_callback()
