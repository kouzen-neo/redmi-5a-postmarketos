"""TubeMobile Thumbnail Cache Manager"""
import os
import hashlib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib

CACHE_DIR = os.path.expanduser("~/.cache/tubemobile/thumbnails")
os.makedirs(CACHE_DIR, exist_ok=True)

class ThumbnailCache:
    _executor = ThreadPoolExecutor(max_workers=6)

    @classmethod
    def get_thumbnail_async(cls, url, callback):
        """
        Download thumbnail asynchronously and call callback(local_file_path) on GTK main thread.
        """
        if not url:
            return

        # Generate unique hash for filename
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        ext = ".jpg"
        cached_file = os.path.join(CACHE_DIR, f"{url_hash}{ext}")

        # If already cached on disk, invoke callback immediately
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            GLib.idle_add(callback, cached_file)
            return

        # Otherwise download in background thread
        def _download():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "TubeMobile/1.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        with open(cached_file, "wb") as f:
                            f.write(data)
                        GLib.idle_add(callback, cached_file)
            except Exception as e:
                pass # Silently handle network hiccup

        cls._executor.submit(_download)
