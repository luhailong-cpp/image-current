"""Validate a separate recorded playback review against the current runtime files.

This validates the review's coverage and file binding; it does not perform or
authenticate visual observation. Missing, stale or malformed evidence is ignored.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PLAYBACK_RECORD = "qa/native-playback-review.json"
PLAYBACK_SEQUENCE = "ordered-contact-sheet-reviewed; native-live-playback-sampled-normal-and-0.25"
PENDING_SEQUENCE = "ordered-contact-sheet-reviewed; continuous-playback-not-observed"
_COUNTS = {"hit": 6, "attack": 12, "cast": 16}


def load_playback_review(root: Path) -> dict | None:
    """Return the manual record only when all six groups and 68 current SHAs match."""
    try:
        root = Path(root).resolve()
        record = root / PLAYBACK_RECORD
        if not record.resolve().is_relative_to(root):
            return None
        review = json.loads(record.read_text(encoding="utf-8-sig"))
        if not isinstance(review, dict):
            return None
        if review.get("status") != "observed_native_live_samples" or review.get("reviewer") != "root":
            return None

        groups = review.get("groups")
        if not isinstance(groups, list) or len(groups) != 6:
            return None
        expected_groups = {(action, direction) for action in _COUNTS for direction in ("E", "W")}
        seen_groups = set()
        for group in groups:
            if not isinstance(group, dict):
                return None
            action, direction = group.get("action"), group.get("direction")
            if not isinstance(action, str) or not isinstance(direction, str):
                return None
            pair = (action, direction)
            speeds = group.get("speedsReviewed")
            if pair not in expected_groups or pair in seen_groups:
                return None
            if not isinstance(speeds, list) or speeds != [1, 0.25] or any(type(s) not in (int, float) for s in speeds):
                return None
            seen_groups.add(pair)

        expected = {
            f"runtime/{action}/{direction}/{n:02d}.png"
            for action, count in _COUNTS.items()
            for direction in ("E", "W")
            for n in range(1, count + 1)
        }
        current = {p.relative_to(root).as_posix() for p in (root / "runtime").rglob("*.png")}
        if current != expected:
            return None
        sources = review.get("sourceFrames")
        if not isinstance(sources, list) or len(sources) != 68:
            return None
        seen_files = set()
        for source in sources:
            if not isinstance(source, dict):
                return None
            name, digest = source.get("file"), source.get("sha256")
            if not isinstance(name, str) or name not in expected or name in seen_files:
                return None
            if not isinstance(digest, str) or len(digest) != 64:
                return None
            path = root / name
            if not path.resolve().is_relative_to(root) or not path.is_file():
                return None
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest.lower():
                return None
            seen_files.add(name)
        return review if seen_files == expected else None
    except (OSError, ValueError, TypeError):
        return None
