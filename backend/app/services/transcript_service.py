import re
import os
import json
import requests
from typing import Optional, List
from pathlib import Path


# Cache directory for transcripts
CACHE_DIR = Path(__file__).parent.parent.parent / "transcript_cache"
CACHE_DIR.mkdir(exist_ok=True)


class TranscriptService:
    """Service for handling transcripts from various sources."""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _get_cache_path(video_id: str) -> Path:
        return CACHE_DIR / f"{video_id}.txt"

    @staticmethod
    def _get_cached_transcript(video_id: str) -> Optional[str]:
        cache_path = TranscriptService._get_cache_path(video_id)
        if cache_path.exists():
            text = cache_path.read_text(encoding='utf-8')
            if text and len(text) > 500:
                print(f"Transcript loaded from cache ({len(text)} characters)")
                return text
        return None

    @staticmethod
    def _save_to_cache(video_id: str, transcript: str):
        cache_path = TranscriptService._get_cache_path(video_id)
        cache_path.write_text(transcript, encoding='utf-8')
        print(f"Transcript saved to cache")

    @staticmethod
    def _parse_json3_subtitles(data: dict) -> str:
        """Parse json3 subtitle format into plain text."""
        events = data.get('events', [])
        texts = []
        for event in events:
            for seg in event.get('segs', []):
                text = seg.get('utf8', '').strip()
                if text and text != '\n':
                    texts.append(text)
        return ' '.join(texts)

    @staticmethod
    def _get_subtitle_url(url: str) -> Optional[str]:
        """Use yt-dlp to extract subtitle URL from a YouTube video."""
        try:
            import yt_dlp
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                subs = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})

                en_subs = subs.get('en') or auto_subs.get('en')
                if not en_subs:
                    for key in subs:
                        if key.startswith('en'):
                            en_subs = subs[key]
                            break

                if not en_subs:
                    return None

                for fmt in en_subs:
                    if fmt.get('ext') == 'json3':
                        return fmt['url']
            return None
        except Exception as e:
            print(f"Failed to extract subtitle URL: {e}")
            return None

    @staticmethod
    def _fetch_subtitle_direct(json3_url: str) -> Optional[str]:
        """Try to fetch subtitle content directly."""
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                from yt_dlp.networking.common import Request
                resp = ydl.urlopen(Request(json3_url))
                data = json.loads(resp.read())
                return TranscriptService._parse_json3_subtitles(data)
        except Exception:
            pass

        try:
            resp = requests.get(json3_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if resp.status_code == 200:
                return TranscriptService._parse_json3_subtitles(resp.json())
        except Exception:
            pass

        return None

    @staticmethod
    def _fetch_subtitle_via_proxy(json3_url: str) -> Optional[str]:
        """Fetch subtitle content through free proxies when direct access is blocked."""
        print("Direct access blocked, trying proxy fallback...")

        # Check for user-configured proxy first
        proxy = os.environ.get('YOUTUBE_PROXY') or os.environ.get('HTTPS_PROXY')
        if proxy:
            try:
                proxies = {'https': proxy, 'http': proxy}
                resp = requests.get(json3_url, proxies=proxies, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if resp.status_code == 200:
                    transcript = TranscriptService._parse_json3_subtitles(resp.json())
                    if transcript and len(transcript) > 500:
                        print(f"Fetched via configured proxy")
                        return transcript
            except Exception:
                pass

        # Try to get free proxies
        try:
            proxy_resp = requests.get(
                'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies'
                '&proxy_format=protocolipport&format=json&limit=15&protocol=http&timeout=3000',
                timeout=8
            )
            proxy_list = proxy_resp.json().get('proxies', [])
        except Exception:
            proxy_list = []

        for p in proxy_list:
            proxy_url = f"http://{p['ip']}:{p['port']}"
            try:
                proxies = {'https': proxy_url, 'http': proxy_url}
                resp = requests.get(json3_url, proxies=proxies, timeout=8, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if resp.status_code == 200 and resp.text.strip().startswith('{'):
                    transcript = TranscriptService._parse_json3_subtitles(resp.json())
                    if transcript and len(transcript) > 500:
                        print(f"Fetched via proxy {p['ip']}")
                        return transcript
            except Exception:
                continue

        return None

    @staticmethod
    def _get_transcript_via_api(video_id: str) -> Optional[str]:
        """Get transcript using youtube-transcript-api."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            transcript = " ".join(entry.text for entry in transcript_list)
            return transcript
        except Exception as e:
            error_msg = str(e)
            if 'RequestBlocked' in error_msg or 'blocking' in error_msg.lower():
                print(f"youtube-transcript-api: IP blocked by YouTube.")
            else:
                print(f"youtube-transcript-api failed: {e}")
            return None

    @staticmethod
    def get_youtube_transcript(url: str) -> Optional[str]:
        """
        Get transcript from YouTube video URL.
        Strategy: cache -> direct yt-dlp -> proxy fallback -> youtube-transcript-api
        """
        video_id = TranscriptService.extract_video_id(url)
        if not video_id:
            print("Error: Invalid YouTube URL.")
            return None

        print(f"Video ID: {video_id}")

        # 1. Check cache
        cached = TranscriptService._get_cached_transcript(video_id)
        if cached:
            return cached

        # 2. Get subtitle URL via yt-dlp (metadata extraction works even when blocked)
        print("Extracting subtitle URL...")
        json3_url = TranscriptService._get_subtitle_url(url)

        if json3_url:
            # 3. Try direct fetch
            print("Fetching subtitles directly...")
            transcript = TranscriptService._fetch_subtitle_direct(json3_url)
            if transcript and len(transcript) > 500:
                print(f"Transcript fetched successfully ({len(transcript)} characters)")
                TranscriptService._save_to_cache(video_id, transcript)
                return transcript

            # 4. Try proxy fallback
            transcript = TranscriptService._fetch_subtitle_via_proxy(json3_url)
            if transcript and len(transcript) > 500:
                print(f"Transcript fetched via proxy ({len(transcript)} characters)")
                TranscriptService._save_to_cache(video_id, transcript)
                return transcript

        # 5. Last resort: youtube-transcript-api
        print("Trying youtube-transcript-api...")
        transcript = TranscriptService._get_transcript_via_api(video_id)
        if transcript and len(transcript) > 500:
            print(f"Transcript fetched ({len(transcript)} characters)")
            TranscriptService._save_to_cache(video_id, transcript)
            return transcript

        print("Failed to fetch transcript. YouTube may be rate-limiting this IP.")
        return None

    @staticmethod
    def validate_transcript(transcript: str) -> bool:
        if not transcript:
            return False
        if len(transcript.strip()) < 500:
            return False
        return True
