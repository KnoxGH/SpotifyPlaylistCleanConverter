import argparse

from clean_converter.auth import get_spotify_client
from clean_converter.converter import (
    apply_uris,
    build_plan,
    fetch_playlist_tracks,
    plan_summary,
    resulting_uris,
)


def extract_playlist_id(value: str) -> str:
    if value.startswith("http"):
        return value.split("/playlist/", 1)[-1].split("?", 1)[0]
    if value.startswith("spotify:playlist:"):
        return value.rsplit(":", 1)[-1]
    return value


def describe_track(track: dict) -> str:
    artists = ", ".join(a["name"] for a in track["artists"])
    return f"{artists} - {track['name']}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Replace explicit tracks in a Spotify playlist with their clean "
            "versions, directly on Spotify."
        )
    )
    parser.add_argument("playlist", help="Spotify playlist URL, URI, or ID")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would change; make no changes"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Apply changes without a confirmation prompt"
    )
    parser.add_argument(
        "--copy-to",
        metavar="NAME",
        help="Create a new playlist with this name instead of modifying the original",
    )
    args = parser.parse_args()

    sp = get_spotify_client()
    playlist_id = extract_playlist_id(args.playlist)
    playlist = sp.playlist(playlist_id, fields="id,name,owner(display_name)")
    print(f'Playlist: "{playlist["name"]}" (owner: {playlist["owner"]["display_name"]})')

    tracks = fetch_playlist_tracks(sp, playlist_id)
    print(f"Fetched {len(tracks)} tracks. Searching for clean versions of explicit tracks...")
    plan = build_plan(sp, tracks)

    total_explicit, replaced, unresolved = plan_summary(plan)
    print(f"\nExplicit tracks found: {total_explicit}")
    print(f"Clean replacements found: {replaced}")
    print(f"Left explicit (no clean match): {unresolved}\n")

    for entry in plan:
        original = entry["original"]
        if entry["replacement"]:
            replacement = entry["replacement"]
            print(f"  [REPLACE] {describe_track(original)}")
            artists = ", ".join(replacement["artists"])
            print(f"       with {artists} - {replacement['name']} (album: {replacement['album']})")
        elif original.get("explicit"):
            print(f"  [KEEP-EXPLICIT, no match] {describe_track(original)}")

    if replaced == 0:
        print("\nNothing to change.")
        return

    if args.dry_run:
        print("\nDry run only, no changes made.")
        return

    if not args.yes:
        answer = input(f"\nApply {replaced} replacement(s)? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    uris = resulting_uris(plan)

    if args.copy_to:
        me = sp.current_user()
        new_playlist = sp.user_playlist_create(me["id"], args.copy_to, public=False)
        for i in range(0, len(uris), 100):
            sp.playlist_add_items(new_playlist["id"], uris[i : i + 100])
        print(f'\nCreated new playlist "{args.copy_to}": {new_playlist["external_urls"]["spotify"]}')
    else:
        apply_uris(sp, playlist_id, uris)
        print(f'\nUpdated playlist "{playlist["name"]}" in place.')


if __name__ == "__main__":
    main()
