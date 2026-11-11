import os

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

SCOPES = (
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-public "
    "playlist-modify-private"
)


def get_spotify_client() -> Spotify:
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

    if not client_id or not client_secret:
        raise SystemExit(
            "Missing SPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET.\n"
            "Create an app at https://developer.spotify.com/dashboard, then set these "
            "as environment variables (see .env.example)."
        )

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPES,
        cache_path=os.environ.get("SPOTIPY_CACHE_PATH", ".spotify_cache"),
        open_browser=True,
    )
    return Spotify(auth_manager=auth_manager)
