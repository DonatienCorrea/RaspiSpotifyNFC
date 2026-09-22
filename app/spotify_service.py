from __future__ import annotations

from typing import Any, Optional

try:
    from spotipy import Spotify
    from spotipy.oauth2 import SpotifyOAuth
except ModuleNotFoundError:  # pragma: no cover - exercised when the optional dependency is absent.
    Spotify = None
    SpotifyOAuth = None

from .config import settings


class FakeSpotifyClient:
    def __init__(self):
        self.is_playing = False
        self.current_uri = "spotify:track:demo"
        self.position_ms = 0

    def start_playback(self, uris=None, context_uri=None, position_ms=0):
        if uris:
            self.current_uri = uris[0]
        elif context_uri:
            self.current_uri = context_uri
        else:
            self.current_uri = "spotify:track:demo"
        self.position_ms = position_ms
        self.is_playing = True
        return {
            "status": "ok",
            "mode": "fake",
            "uri": self.current_uri,
            "position_ms": self.position_ms,
        }

    def pause_playback(self):
        self.is_playing = False
        return {"status": "ok", "mode": "fake", "paused": True}

    def next_track(self):
        self.is_playing = True
        return {"status": "ok", "mode": "fake", "action": "next"}

    def current_playback(self):
        return {
            "is_playing": self.is_playing,
            "item": {"uri": self.current_uri},
            "position_ms": self.position_ms,
            "mode": "fake",
        }


def is_live_spotify_configured() -> bool:
    return bool(settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET and settings.SPOTIFY_REFRESH_TOKEN)


def build_spotify_client() -> Any:
    if not is_live_spotify_configured():
        return FakeSpotifyClient()

    if Spotify is None or SpotifyOAuth is None:
        raise RuntimeError(
            "Spotify support requires the 'spotipy' dependency. "
            "Install it with 'pip install -r requirements.txt' or 'pip install -r requirements-pi.txt'."
        )

    auth_manager = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state",
        cache_path=None,
    )
    auth_manager.refresh_access_token(settings.SPOTIFY_REFRESH_TOKEN)
    return Spotify(auth_manager=auth_manager)


def play_content(uri: str, position_ms: int = 0) -> dict:
    spotify = build_spotify_client()
    if uri.startswith("spotify:track:"):
        return spotify.start_playback(uris=[uri], position_ms=position_ms)
    if uri.startswith("spotify:playlist:") or uri.startswith("spotify:album:"):
        return spotify.start_playback(context_uri=uri, position_ms=position_ms)
    return {"status": "unsupported_uri", "uri": uri}


def toggle_playback() -> dict:
    spotify = build_spotify_client()
    current = spotify.current_playback()
    if not current or not current.get("is_playing"):
        return spotify.start_playback()
    return spotify.pause_playback()


def next_track() -> dict:
    spotify = build_spotify_client()
    return spotify.next_track()


def get_current_playback() -> Optional[dict]:
    spotify = build_spotify_client()
    return spotify.current_playback()


def dispatch_tag_value(value: str) -> dict:
    if value.startswith("spotify:"):
        return play_content(value)
    if value == "action:play_pause":
        return toggle_playback()
    if value == "action:next":
        return next_track()
    return {"status": "unsupported_action", "value": value}
