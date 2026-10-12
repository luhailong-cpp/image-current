"""Preserve root's 2026-10-08 actual live-window observations.

This is a one-time transcription of observations, not an automatic visual test.
Do not reuse it to approve changed images or future playback sessions.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
session_path = root / "qa/native-playback-session.json"
session = json.loads(session_path.read_text(encoding="utf-8"))
assert session["closed"]
assert session["startedAt"] == "2026-10-08T06:15:27.943414+00:00", "This transcript binds one observed session only."
assert len(session["sourceFrames"]) == 68
for source in session["sourceFrames"]:
    assert hashlib.sha256((root / source["file"]).read_bytes()).hexdigest() == source["sha256"]
samples = {
    "hit": {"normal": [2, 3, 4, 5], "slow025": [1, 4, 1, 3, 5]},
    "attack": {"normal": [9, 5, 3, 8, 1], "slow025": [2, 5, 8, 11, 2, 5]},
    "cast": {"normal": [2, 8, 14, 4, 11, 2], "slow025": [1, 3, 5, 7, 9, 12, 15]},
}
observations = {
    ("hit", "E"): "Front view recoil/closed-eye peak and recovery remain legible; anatomical right fan retained, left empty; bent hovering legs recover without a walking cycle.",
    ("hit", "W"): "Rear hair/back/shoe soles remain rear-facing through recoil and rebound; bent left arm transitions to the open recovery pose, right fan retained.",
    ("attack", "E"): "Right fan progresses from shoulder windup across chest into lower-right follow-through and returns to the side; left empty balancing hand remains distinct.",
    ("attack", "W"): "True rear view preserved; right fan travels around the head toward upper-left and retracts. Head/arm occlusion is consistent with the separately reviewed original frames.",
    ("cast", "E"): "Lift, bell illumination, forward release and lowering/return are visible; fan remains in anatomical right hand. Bell light stays within canvas; narrowing fan during return is perspective.",
    ("cast", "W"): "Rear shoulder lift, illuminated three bells, outward release and return retain identity and direction; light and trailing costume stay inside the canvas.",
}
groups = []
for action, count in [("hit", 6), ("attack", 12), ("cast", 16)]:
    for speed in (1, .25):
        assert session["coverage"][f"{action}:{speed:g}"]["framesSeen"] == list(range(1, count + 1))
    for direction in ("E", "W"):
        groups.append({"action": action, "direction": direction, "speedsReviewed": [1, .25],
                       "sampledLiveFrameLabels": samples[action], "observation": observations[action, direction],
                       "result": "no_new_asset_defect_identified_in_live_samples"})
review = {
    "status": "observed_native_live_samples", "reviewer": "root",
    "reviewedAt": session["events"][-1]["at"], "recordedAt": datetime.now(timezone.utc).isoformat(),
    "method": "Root inspected successive sky.get_window_state screenshots of the running offline Tk PNG renderer. E/W were displayed side by side; all three actions were explicitly selected at 1x and 0.25x, with changing frame labels/cycle counters and visible pose changes. Independent still-frame/contact-sheet reviews remain the source for every individual frame.",
    "limitations": [
        "This is visual sampling of real live playback, not a continuous video recording or observation of every normal-speed transition.",
        "Window captures can straddle GUI paint boundaries; frame labels describe capture context, not pixel-perfect capture synchronization.",
        "The monotonic-clock native preview targets 40/30/45 ms (slow:160/120/180 ms); desktop scheduling and capture timing are not game-engine frame-time benchmarks.",
        "No client was read or integrated. Actual game size/pivot, rendering order, events and transitions to external idle assets remain integration work."
    ],
    "previewProgram": "tools/preview_native.py", "previewProgramSha256": hashlib.sha256((root / "tools/preview_native.py").read_bytes()).hexdigest(),
    "sessionRecord": "qa/native-playback-session.json", "sessionSha256": hashlib.sha256(session_path.read_bytes()).hexdigest(),
    "sourceFrames": session["sourceFrames"], "groups": groups,
    "controlsObserved": "Pause froze cast at 04; Right advanced to05 while paused; Left returned to04; Escape exited normally and finalized the session.",
    "browserPolicy": "The earlier file-protocol rejection was respected. This viewer renders only the fixed local PNG set through Tk/Pillow, with no HTML, URL navigation, server or network capability; no blocked browser action was retried.",
    "runtimeChangesThisReview": "none; all 68 existing final PNG hashes unchanged",
    "newRepairsRequired": [], "clientReview": "not_tested"
}
(root / "qa/native-playback-review.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
print("Recorded root's observed native playback samples: six groups, both speeds, 68 unchanged source hashes.")
