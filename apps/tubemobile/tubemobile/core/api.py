"""TubeMobile Core API with Lazy yt_dlp Extraction"""
import os
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TubeMobile.API")

class YouTubeAPI:
    _executor = ThreadPoolExecutor(max_workers=4)

    @classmethod
    def get_trending(cls, max_results=15):
        """Fetch trending/popular Indonesian videos"""
        return cls._search_videos("trending indonesia", max_results=max_results)

    @classmethod
    def search(cls, query, max_results=15):
        """Search videos on YouTube"""
        if not query or not query.strip():
            return []
        return cls._search_videos(query.strip(), max_results=max_results)

    @classmethod
    def _search_videos(cls, query, max_results=15):
        # Lazy import yt_dlp inside background thread so app starts in <0.1 second!
        try:
            import yt_dlp
        except ImportError:
            logger.error("yt_dlp not installed")
            return []

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }
        search_query = f"ytsearch{max_results}:{query}"
        videos = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(search_query, download=False)
                entries = res.get("entries", [])
                for item in entries:
                    if not item:
                        continue
                    vid_id = item.get("id", "")
                    title = item.get("title", "Video YouTube")
                    author = item.get("uploader", item.get("channel", "Channel"))
                    duration = item.get("duration_string", "")
                    
                    # Views formatting
                    view_count = item.get("view_count")
                    views_str = ""
                    if view_count:
                        if view_count >= 1_000_000:
                            views_str = f"{view_count / 1_000_000:.1f}M views"
                        elif view_count >= 1_000:
                            views_str = f"{view_count / 1_000:.1f}K views"
                        else:
                            views_str = f"{view_count} views"

                    # Thumbnail
                    thumbnails = item.get("thumbnails", [])
                    thumb_url = ""
                    if thumbnails:
                        thumb_url = thumbnails[-1].get("url", "")
                    if not thumb_url and vid_id:
                        thumb_url = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"

                    if vid_id and title:
                        videos.append({
                            "id": vid_id,
                            "title": title,
                            "author": author,
                            "views": views_str,
                            "duration": duration,
                            "published": "",
                            "thumbnail_url": thumb_url,
                            "description": item.get("description", "")
                        })
            logger.info(f"Loaded {len(videos)} videos for '{query}'")
            return videos
        except Exception as e:
            logger.error(f"Error fetching YouTube videos: {e}")
            return []
