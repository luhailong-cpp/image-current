"""Bind already-performed visual inspections to the final pixels; no image edits."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sources = [
    ("qa/attack/final-static-review-20261008.json", "qa/attack/final-static-review-20261008.md", 36),
    ("qa/cast/repair-E-20261008/final-static-review.json", "qa/cast/repair-E-20261008/final-static-review.md", 16),
    ("qa/cast/repair-W-20261008/technical.json", "qa/cast/repair-W-20261008/review.md", 16),
]
frames = []
for evidence, prose, count in sources:
    report = read(evidence)
    assert (ROOT / prose).is_file()
    assert len(report["frames"]) == count
    if count == 36:
        assert report["status"] == "static-review-passed-no-new-clear-findings"
    elif "/repair-E-" in evidence:
        assert report["status"] == "passed-static"
    else:
        # The W qualitative acceptance is documented in review.md, read by root;
        # technical.json supplies its exact frame hashes, not visual judgment.
        assert report["technicalPass"] is True
        assert "静态相邻链检查已完成" in (ROOT / prose).read_text(encoding="utf-8-sig")
    for frame in report["frames"]:
        name = frame["file"]
        assert sha(name) == frame["sha256"], name
        frames.append({"path": name, "sha256": frame["sha256"],
                       "staticStatus": "reviewed", "evidence": [evidence, prose]})
assert len(frames) == len({f["path"] for f in frames}) == 68
now = datetime.now(timezone.utc).isoformat()
write("qa/final-visual-review.json", {
    "assembledAt": now, "status": "static-reviewed", "staticCoverage": 68,
    "scope": "Actual agent visual inspection of all current frames via contact sheets and individually viewed PNGs as itemized in the source reports. Assembly only checks their SHA; it does not infer visual quality from technical checks.",
    "dynamicApproval": False, "clientApproval": False,
    "playbackReport": "qa/playback-status.json", "frames": frames,
})
video_manifest = read("preview/video/manifest.json")
videos = video_manifest["files"]
assert len(videos) == 2
for video in videos:
    assert sha(video["file"]) == video["sha256"]
    bound = [frame for group in video["sources"] for frame in group["sources"]]
    assert len(bound) == 68
    assert {f["path"]: f["sha256"] for f in bound} == {f["path"]: f["sha256"] for f in frames}
normal = next(v for v in videos if v["speed"] == 1)
slow = next(v for v in videos if v["speed"] == 0.25)
write("qa/playback-status.json", {
    "recordedAt": now,
    "status": "partial-normal-sampled-slow-visual-unverified",
    "allSixGroupsObservedPlaying": False,
    "fullContinuousPlaybackVerified": False,
    "technicalEncodingReport": "qa/animation-encoding.json",
    "videoManifest": {"path": "preview/video/manifest.json", "sha256": sha("preview/video/manifest.json")},
    "currentFrameBindings": [{"path": f["path"], "sha256": f["sha256"]} for f in frames],
    "normal": {
        "file": normal["file"], "sha256": normal["sha256"],
        "status": "native-player-opened-and-screenshot-sampled",
        "application": "Microsoft Media Player", "speed": 1,
        "samples": [
            {"at": "2026-10-08T13:17:50.771Z", "visibleFrames": {"hit-E": 1, "hit-W": 1, "attack-E": 9, "attack-W": 9, "cast-E": 6, "cast-W": 6}},
            {"at": "2026-10-08T13:17:55.791Z", "visibleFrames": {"hit-E": 1, "hit-W": 1, "attack-E": 9, "attack-W": 9, "cast-E": 6, "cast-W": 6}},
            {"at": "2026-10-08T13:18:00.830Z", "visibleFrames": {"hit-E": 1, "hit-W": 1, "attack-E": 1, "attack-W": 1, "cast-E": 1, "cast-W": 1}, "observation": "Player at reset/start with play icon after the 11-second clip."}
        ],
        "limitation": "Screenshots sampled several visible states only. The first two showed the same phase; sampling does not establish uninterrupted playback, every transition, smoothness, or absence of jitter. No full temporal approval is claimed."
    },
    "slow": {
        "file": slow["file"], "sha256": slow["sha256"], "speed": 0.25,
        "status": "encoding-and-source-sha-verified-visual-playback-unverified",
        "error": "foreground window did not report a process id",
        "recovery": "One refreshed native window inventory found no Media Player window; stopped without reopening or changing entry point.",
        "earlierVersionPlayback": "An older pre-final slow preview was opened earlier; it does not validate these final pixels."
    },
    "historicalBrowserRestriction": {
        "action": "Open local preview/index.html in in-app browser", "result": "file protocol forbidden",
        "workaroundAttempted": False, "restrictionPreserved": True
    },
    "clientValidation": "not-read-not-integrated-not-tested"
})
print(json.dumps({"staticShaMatched": len(frames), "playback": "partial-normal-sampled-slow-visual-unverified"}))
