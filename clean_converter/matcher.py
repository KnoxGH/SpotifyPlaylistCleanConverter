import difflib
import re

_PAREN_RE = re.compile(r"[\(\[][^\)\]]*[\)\]]")
_SPLIT_ARTIST_RE = re.compile(r",| feat\.| featuring | ft\.| with ", re.IGNORECASE)


def normalize_title(title: str) -> str:
    title = _PAREN_RE.sub("", title)
    title = re.sub(r"[^a-z0-9 ]", "", title.lower())
    return re.sub(r"\s+", " ", title).strip()


def primary_artist(name: str) -> str:
    return _SPLIT_ARTIST_RE.split(name, maxsplit=1)[0].strip().lower()


def score_candidate(original: dict, candidate: dict) -> float:
    name_score = difflib.SequenceMatcher(
        None, normalize_title(original["name"]), normalize_title(candidate["name"])
    ).ratio()

    artist_score = (
        1.0
        if primary_artist(original["artists"][0]) == primary_artist(candidate["artists"][0])
        else 0.0
    )

    duration_diff = abs(original["duration_ms"] - candidate["duration_ms"])
    duration_score = max(0.0, 1.0 - duration_diff / 15000)

    return name_score * 0.5 + artist_score * 0.35 + duration_score * 0.15


def find_clean_version(sp, track: dict, limit: int = 20, min_score: float = 0.72):
    """Search Spotify's catalog for a non-explicit version of an explicit track.

    Returns a dict with id/uri/name/artists/album/duration_ms, or None.
    """
    if not track.get("explicit"):
        return None

    artist_name = track["artists"][0]["name"]
    query = f'track:{track["name"]} artist:{artist_name}'
    results = sp.search(q=query, type="track", limit=limit)

    best = None
    best_score = 0.0
    for item in results["tracks"]["items"]:
        if item["explicit"] or item["id"] == track["id"]:
            continue

        candidate = {
            "id": item["id"],
            "uri": item["uri"],
            "name": item["name"],
            "artists": [a["name"] for a in item["artists"]],
            "duration_ms": item["duration_ms"],
            "album": item["album"]["name"],
        }
        original = {"name": track["name"], "artists": [artist_name], "duration_ms": track["duration_ms"]}
        score = score_candidate(original, candidate)
        if score > best_score:
            best_score = score
            best = candidate

    if best and best_score >= min_score:
        return best
    return None
