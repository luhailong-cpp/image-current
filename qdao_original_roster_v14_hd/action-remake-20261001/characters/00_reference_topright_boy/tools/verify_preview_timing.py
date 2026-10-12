"""Check actual animated WebP durations and source hashes against the current manifest."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def durations(path):
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", path
    pos, result = 12, []
    while pos + 8 <= len(data):
        size = struct.unpack_from("<I", data, pos + 4)[0]
        if data[pos:pos + 4] == b"ANMF":
            result.append(int.from_bytes(data[pos + 20:pos + 23], "little"))
        pos += 8 + size + size % 2
    return result


def main():
    manifest = read(ROOT / "manifest.json")
    by_file = {f["file"]: f for f in manifest["frames"]}
    results = []
    for product in read(ROOT / "review/animations/index.json")["products"]:
        if product["kind"] != "animated_preview":
            continue
        path = ROOT / product["file"]
        multiplier = 4 if path.stem.endswith("-slow") else 1
        sources = product["derivedFrom"]
        expected = [by_file[s["file"]]["frameDurationMs"] * multiplier for s in sources]
        actual = durations(path)
        stale = [s["file"] for s in sources if sha(ROOT / s["file"]) != s["sha256"]]
        passed = actual == expected and not stale and sha(path) == product["sha256"]
        results.append({"file": product["file"], "encodedMs": actual,
                        "expectedMs": expected, "cycleMs": sum(actual),
                        "sourceHashMismatches": stale, "passed": passed})
    result = {"scope": "Encoding and current-source check; not dynamic visual acceptance.",
              "manifestSha256": sha(ROOT / "manifest.json"), "animations": len(results),
              "passed": len(results) == 28 and all(x["passed"] for x in results), "results": results}
    (ROOT / "review/animations/timing-validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "results"}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
