"""Verify final files and decoded APNG contents; never performs visual playback."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
SPECS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))

def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def main():
    manifest = read("manifest.json")
    frames = manifest["frames"]
    assert len(frames) == 68
    assert len(list((ROOT / "runtime").rglob("*.png"))) == 68
    expected_hashes = dict(line.split("  ", 1)[::-1] for line in (ROOT / "SHA256SUMS").read_text().splitlines())
    previews = {}
    pixel_hashes = set()
    for frame in frames:
        file = frame["file"]
        record = read(frame["record"])
        digest = sha(file)
        assert digest == frame["sha256"] == record["sha256"] == expected_hashes[file], file
        assert (ROOT / record["prompt"]).is_file()
        assert (ROOT / record["evidence"]["receipt"]).is_file()
        with Image.open(ROOT / file) as source:
            assert source.size == (1024, 1024) and source.mode == "RGBA" and source.format == "PNG", file
            assert source.getchannel("A").getextrema() == (0, 255), file
            pixel_hashes.add(hashlib.sha256(source.tobytes()).hexdigest())
            previews[file] = source.resize((512, 512), Image.Resampling.LANCZOS).tobytes()
    assert len(pixel_hashes) == 68
    for group in manifest["groups"]:
        count, ms = SPECS[group["action"]]
        assert len(group["frames"]) == count
        assert group["durationMs"] == ms and group["totalDurationMs"] == count * ms
        for index, frame in enumerate(group["frames"], 1):
            assert frame["file"] == f"runtime/{group['action']}/{group['direction']}/{index:02}.png"
            assert frame["durationMs"] == ms

    records = read("preview/animation-records.json")
    assert len(records) == 12
    decoded_frames = 0
    animation_results = []
    for record in records:
        file = record["file"]
        action, direction = Path(file).stem.split("-")[:2]
        count, ms = SPECS[action]
        multiplier = 4 if "quarter-speed" in file else 1
        assert sha(file) == record["sha256"], file
        assert len(record["derivedFrom"]) == count
        durations = []
        with Image.open(ROOT / file) as animation:
            assert animation.n_frames == count and animation.info.get("loop") == 0, file
            for index in range(count):
                runtime = f"runtime/{action}/{direction}/{index + 1:02}.png"
                source = record["derivedFrom"][index]
                assert source["path"] == runtime and source["sha256"] == expected_hashes[runtime]
                animation.seek(index)
                assert animation.convert("RGBA").tobytes() == previews[runtime], (file, index + 1)
                duration = animation.info["duration"]
                assert duration == ms * multiplier, (file, index + 1, duration)
                durations.append(duration)
                decoded_frames += 1
        assert durations == record["durationMs"]
        animation_results.append({"file": file, "frames": count, "durationMs": durations, "decodedPixelsMatchFinalFrames": True})

    contacts = read("preview/contact-records.json")
    assert len(contacts) == 6
    for record in contacts:
        assert sha(record["file"]) == record["sha256"]
        for source in record["derivedFrom"]:
            assert source["sha256"] == expected_hashes[source["path"]]
    script = (ROOT / "preview/manifest.js").read_text(encoding="utf-8")
    assert json.loads(script.removeprefix("window.SPRITE_MANIFEST = ").strip().removesuffix(";")) == manifest
    result = {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "status": "technical-passed-playback-pending",
        "runtimeFrames": 68,
        "distinctPixelFrames": 68,
        "runtimeAndRecordHashes": "passed",
        "contactSheets": 6,
        "animationFiles": 12,
        "decodedAnimationFramesCompared": decoded_frames,
        "animationPixelsOrderAndTiming": "passed",
        "previewManifestMatches": True,
        "staticReviewStatus": manifest.get("visualStatus"),
        "acceptanceStatus": manifest.get("acceptanceStatus", "playback-pending"),
        "staticReviewRecord": manifest.get("staticReviewRecord"),
        "animations": animation_results,
        "playbackStatus": "not-verified-browser-policy-blocked",
        "playbackEvidence": "records/cast-E/browser-policy-rejection.json",
        "clientStatus": "not-integrated",
        "limits": "Lossless decoded-pixel, frame-order and timing verification does not establish visual motion quality, browser playback or client approval."
    }
    (ROOT / "delivery-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "animations"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
