"""Read tile-local selected cores and write mechanical QA evidence only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image

T = Path(__file__).resolve().parent
Q = T / "qa" / "internal"
Q.mkdir(parents=True, exist_ok=True)
read = lambda p: json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


selection = read(T / "selected-patches.json")
plan = read(T / "coordinate-plan.json")
assert selection["tile"] == plan["tile"] == T.name
assert (plan["corePixels"], plan["haloPixels"], plan["expectedNativeSize"]) == (1024, 115, [1254, 1254])
ox, oy, _, _ = plan["tileCoreBox"]
coordinates = {p["id"]: p for p in plan["patches"]}
cores, sources = {}, {}
canvas = Image.new("RGB", (4096, 4096))
for pid, relative in selection["patches"].items():
    path = T / relative
    r, c = int(pid[1]) - 1, int(pid[2]) - 1
    with Image.open(path) as im:
        assert im.size == (1254, 1254), (pid, im.size)
        if "A" in im.getbands():
            assert im.getchannel("A").getextrema() == (255, 255)
        core = im.convert("RGB").crop((115, 115, 1139, 1139))
    expected = [ox+c*1024, oy+r*1024, ox+(c+1)*1024, oy+(r+1)*1024]
    assert coordinates[pid]["coreBox"] == expected
    canvas.paste(core, (c*1024, r*1024))
    cores[pid] = core
    sources[pid] = {"patch": pid, "path": str(path), "sha256": sha(path), "coreBoxGlobal": expected,
                    "cropNative": [115, 115, 1139, 1139], "coordinatePlan": str(T / "coordinate-plan.json")}


def evidence(identifier, pids, box, extra):
    file = Q / (identifier + ".png")
    image = canvas.crop(tuple(box))
    image.save(file)
    item = {"id": identifier, "file": str(file), "sha256": sha(file), "dimensions": list(image.size),
            "globalBox": [box[0]+ox, box[1]+oy, box[2]+ox, box[3]+oy], "tileBox": box,
            "sources": [sources[p] for p in pids], "operation": "exact native core crops joined at [115:1139] midpoint; no blending or pixel resampling",
            "resamplingApplied": False, "visualStatus": "pending", "formalAccepted": False, **extra}
    write(file.with_suffix(".png.derivation.json"), item)
    return item


seams, crossings, pending = [], [], []
for r in range(1, 5):
    for c in range(1, 5):
        a = f"p{r}{c}"
        for dr, dc, axis in [(0, 1, "vertical"), (1, 0, "horizontal")]:
            if r+dr > 4 or c+dc > 4:
                continue
            b = f"p{r+dr}{c+dc}"
            if a not in cores or b not in cores:
                pending.append({"id": f"{a}--{b}", "missing": [p for p in [a, b] if p not in cores]})
                continue
            if axis == "vertical":
                box = [c*1024-256, (r-1)*1024, c*1024+256, r*1024]
            else:
                box = [(c-1)*1024, r*1024-256, c*1024, r*1024+256]
            seams.append(evidence(f"{a}--{b}", [a, b], box, {"axis": axis, "seamCoordinateInCrop": 256}))
for r in range(1, 4):
    for c in range(1, 4):
        pids = [f"p{rr}{cc}" for rr in (r, r+1) for cc in (c, c+1)]
        if not all(p in cores for p in pids):
            continue
        box = [c*1024-256, r*1024-256, c*1024+256, r*1024+256]
        crossings.append(evidence(f"cross-r{r}-c{c}", pids, box, {"intersectionInCrop": [256, 256]}))
summary = {"tile": T.name, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
           "selectedManifest": str(T / "selected-patches.json"), "selectedManifestSha256": sha(T / "selected-patches.json"),
           "script": str(Path(__file__).resolve()), "scriptSha256": sha(Path(__file__).resolve()),
           "selectedCount": len(cores), "seams": seams, "crossings": crossings, "pendingMissingSources": pending,
           "formalAccepted": False, "status": "mechanical QA only; visual review required; missing cores are not synthesized"}
write(Q / "manifest.json", summary)
print(json.dumps({"selectedCount": len(cores), "seams": len(seams), "crossings": len(crossings), "pendingSeams": len(pending)}))
