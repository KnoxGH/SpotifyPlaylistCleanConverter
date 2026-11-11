import time

from .matcher import find_clean_version


def fetch_playlist_tracks(sp, playlist_id: str) -> list:
    tracks = []
    results = sp.playlist_items(
        playlist_id,
        fields=(
            "items(track(id,uri,name,explicit,duration_ms,is_local,"
            "artists(name),album(name))),next"
        ),
        additional_types=["track"],
    )
    while results:
        for item in results["items"]:
            track = item.get("track")
            if track is not None:
                tracks.append(track)
        results = sp.next(results) if results.get("next") else None
    return tracks


def build_plan(sp, tracks: list, sleep: float = 0.05) -> list:
    plan = []
    for track in tracks:
        replacement = None
        if not track.get("is_local") and track.get("explicit"):
            replacement = find_clean_version(sp, track)
            time.sleep(sleep)
        plan.append({"original": track, "replacement": replacement})
    return plan


def plan_summary(plan: list) -> tuple:
    total_explicit = sum(1 for e in plan if e["original"].get("explicit"))
    replaced = sum(1 for e in plan if e["replacement"])
    unresolved = total_explicit - replaced
    return total_explicit, replaced, unresolved


def resulting_uris(plan: list) -> list:
    return [
        entry["replacement"]["uri"] if entry["replacement"] else entry["original"]["uri"]
        for entry in plan
    ]


def apply_uris(sp, playlist_id: str, uris: list) -> None:
    sp.playlist_replace_items(playlist_id, uris[:100])
    for i in range(100, len(uris), 100):
        sp.playlist_add_items(playlist_id, uris[i : i + 100])
