# Spotify Playlist Clean Converter

Converts an explicit Spotify playlist to clean versions **on Spotify itself** —
it edits the actual playlist via the Spotify Web API, swapping each explicit
track for its clean counterpart (when one exists in Spotify's catalog).
No downloads, no local files — just the playlist on your account, cleaned up.

## How it works

1. Reads every track in the target playlist.
2. For each track flagged `explicit`, searches Spotify for a non-explicit
   track by the same artist with a matching title (ignoring parenthetical
   bits like "(feat. ...)") and similar duration.
3. Shows you the full replacement plan and asks for confirmation.
4. Replaces the playlist's contents in place (same order), or — with
   `--copy-to` — builds a new playlist instead of touching the original.

Tracks with no clean match on Spotify are left untouched and listed as
"no match" so you know which ones still need manual attention.

## Setup

1. Create a Spotify app at https://developer.spotify.com/dashboard
   - Add a redirect URI of `http://127.0.0.1:8888/callback`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your client ID/secret, then
   export them (or use a tool like `direnv`/`python-dotenv`):
   ```bash
   export SPOTIPY_CLIENT_ID=...
   export SPOTIPY_CLIENT_SECRET=...
   export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

## Usage

Preview changes without modifying anything:

```bash
python main.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --dry-run
```

Apply the changes in place (prompts for confirmation):

```bash
python main.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

Skip the confirmation prompt:

```bash
python main.py <playlist> --yes
```

Leave the original playlist alone and create a new clean copy instead:

```bash
python main.py <playlist> --copy-to "My Playlist (Clean)"
```

The playlist argument can be a Spotify URL, URI (`spotify:playlist:...`), or
bare playlist ID.

## Limitations

- Only works for tracks that actually have a clean version in Spotify's
  catalog. Some explicit tracks simply have none — these are reported and
  left as-is.
- Local files (uploaded MP3s in a playlist) are skipped.
- Matching is heuristic (title/artist/duration similarity), so always check
  the printed plan — or run with `--dry-run` first — before applying.
