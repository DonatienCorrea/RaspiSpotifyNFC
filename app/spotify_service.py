from typing import Optional

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from .config import settings


def build_spotify_client() -> Spotify:
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        raise RuntimeError("Missing Spotify credentials in .env")

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
