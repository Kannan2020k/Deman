#!/usr/bin/env python3
import os
from yt_dlp import YoutubeDL
from asyncio import get_event_loop
from functools import partial

from bot import LOGGER


# Default yt-dlp options (ANTI-BOT SAFE)
BASE_YTDLP_OPTS = {
    "cookiefile": "cookies.txt",        # ✅ REQUIRED
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "retries": 10,
    "fragment_retries": 10,
    "continuedl": True,
    "merge_output_format": "mp4",
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]  # ✅ reduces bot detection
        }
    }
}


class YoutubeDLHelper:
    def __init__(self, options=None):
        self.options = BASE_YTDLP_OPTS.copy()

        # Merge user options safely
        if isinstance(options, dict):
            self.options.update(options)

        # Safety check
        if not os.path.exists(self.options.get("cookiefile", "")):
            LOGGER.warning("⚠ cookies.txt not found! YouTube may block downloads.")

    # -------------------- INFO --------------------

    def _extract_info_sync(self, link):
        with YoutubeDL(self.options) as ydl:
            return ydl.extract_info(link, download=False)

    async def extract_info(self, link):
        loop = get_event_loop()
        try:
            return await loop.run_in_executor(
                None, partial(self._extract_info_sync, link)
            )
        except Exception as e:
            err = str(e)
            if "Sign in to confirm" in err or "not a bot" in err:
                raise Exception(
                    "YouTube blocked this request.\n"
                    "Cookies expired or invalid.\n"
                    "Please update cookies.txt"
                )
            raise

    # -------------------- DOWNLOAD --------------------

    def _download_sync(self, link):
        with YoutubeDL(self.options) as ydl:
            return ydl.download([link])

    async def download(self, link):
        loop = get_event_loop()
        return await loop.run_in_executor(
            None, partial(self._download_sync, link)
        )
