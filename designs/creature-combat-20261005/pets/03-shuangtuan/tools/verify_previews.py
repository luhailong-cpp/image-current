"""Verify current runtime SHA links and actual WebP animation durations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

media = json.loads((ROOT / "preview/media-manifest.json").read_text(encoding="utf-8"))
files = []
for item in media:
    for source in item["sources"]:
        assert digest(ROOT / source["file"]) == source["sha256"], source["file"]
    path = ROOT / item["file"]
    if path.suffix != ".webp":
        continue
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", str(path)
    durations = []
    offset = 12
    while offset + 8 <= len(data):
        kind = data[offset:offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = data[offset + 8:offset + 8 + size]
        if kind == b"ANMF":
            durations.append(int.from_bytes(payload[12:15], "little"))
        offset += 8 + size + (size & 1)
    assert len(durations) == item["frameCount"], item["file"]
    assert durations == [item["durationMs"]] * item["frameCount"], item["file"]
    files.append({"file": item["file"], "sha256": digest(path), "frameCount": len(durations),
                  "durationMs": durations, "totalDurationMs": sum(durations), "currentSources": True})
video = json.loads((ROOT / "preview/video/manifest.json").read_text(encoding="utf-8"))
for item in video["files"]:
    assert digest(ROOT / item["file"]) == item["sha256"], item["file"]
    for group in item["sources"]:
        for source in group["sources"]:
            assert digest(ROOT / source["path"]) == source["sha256"], source["path"]
assert len(files) == 12
report = {"createdAt": datetime.now(timezone.utc).isoformat(), "status": "passed",
          "scope": "Actual WebP frame count/durations and all preview source SHA links only; no visual approval inferred.",
          "files": files, "videoCurrentSources": True, "videoDecodeCheck": video["decodeCheck"]}
(ROOT / "qa/animation-encoding.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "passed", "webpFiles": len(files), "videoFiles": len(video["files"])}))
