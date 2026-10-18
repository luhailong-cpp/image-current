"""Independently replay two raw images through saved binary masks, read-only art."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json

import numpy as np
from PIL import Image

Q = Path(__file__).resolve().parent
T = Q.parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rgb(path):
    with Image.open(path) as image:
        assert image.size == (1254, 1254), (path, image.size)
        return np.array(image.convert("RGB"))


def binary(path):
    with Image.open(path) as image:
        assert image.size == (1254, 1254)
        data = np.array(image.convert("L"))
    assert set(np.unique(data)).issubset({0, 255}), "Mask is not binary"
    return data == 255


def selected_path(entry):
    if isinstance(entry, dict):
        entry = entry.get("file") or entry.get("path")
    p = Path(entry)
    return p if p.is_absolute() else T / p


def verify_current():
    start = datetime.now(timezone.utc).isoformat()
    selection_path = T / "selected-patches.json"
    snapshot = selection_path.read_bytes()
    snapshot_sha = hashlib.sha256(snapshot).hexdigest()
    selection = json.loads(snapshot.decode("utf-8-sig"))
    assert selection["tile"] == "r09_c08"
    recipe = read(Q / "bracket-joint-v2-proof.json")
    context = read(Q / "joint-input-v1.json")
    source_records = []

    # Rebuild the saved edit input independently from the original selected cores.
    context_replay = np.zeros((1254, 1254, 3), dtype=np.uint8)
    context_coverage = np.zeros((1254, 1254), dtype=np.uint8)
    for piece in context["sources"]:
        assert sha(piece["file"]) == piece["sha256"]
        source = rgb(piece["file"])
        x0, y0, x1, y1 = piece["sourceCrop"]
        assert 115 <= x0 < x1 <= 1139 and 115 <= y0 < y1 <= 1139
        dx, dy = piece["destination"]
        context_replay[dy:dy+y1-y0, dx:dx+x1-x0] = source[y0:y1, x0:x1]
        context_coverage[dy:dy+y1-y0, dx:dx+x1-x0] += 1
        source_records.append(dict(file=piece["file"], sha256=piece["sha256"]))
    assert np.all(context_coverage == 1)
    assert np.array_equal(context_replay, rgb(context["image"]))

    layers = []
    for item, mask_path in zip(recipe["rawSources"], [recipe["upperMask"], recipe["cupMask"]]):
        assert sha(item["file"]) == item["sha256"]
        layers.append((rgb(item["file"]), binary(mask_path)))
        source_records.extend([dict(file=item["file"], sha256=item["sha256"]),
                               dict(file=mask_path, sha256=sha(mask_path))])
    union = layers[0][1] | layers[1][1]
    assert not union[540:].any(), "Protected shaft and lower scene must be outside masks"
    joint_replay = context_replay.copy()
    for raw, mask in layers:
        joint_replay[mask] = raw[mask]
    assert np.array_equal(joint_replay, rgb(recipe["joint"]))
    assert np.array_equal(joint_replay[~union], context_replay[~union])

    fx, fy = recipe["frameGlobalBox"][:2]
    records, reconstructed = [], {}
    for item in recipe["candidates"]:
        pid = item["patch"]
        current = selected_path(selection["patches"][pid])
        assert sha(current) == item["originalSha256"], f"Canonical source changed: {pid}"
        assert sha(item["original"]) == item["originalSha256"]
        assert sha(item["file"]) == item["sha256"]
        original = rgb(current)
        replay = original.copy()
        coverage = np.zeros((1254, 1254), dtype=bool)
        nx, ny, nx1, ny1 = item["globalBox"]
        assert (nx1 - nx, ny1 - ny) == (1254, 1254)
        # Copy directly from each raw image into native coordinates, in layer order.
        # This deliberately does not read the cached joint when rebuilding natives.
        for raw, mask in layers:
            rows, cols = np.where(mask)
            wx, wy = cols + fx, rows + fy
            inside = (wx >= nx) & (wx < nx1) & (wy >= ny) & (wy < ny1)
            xx, yy = wx[inside] - nx, wy[inside] - ny
            replay[yy, xx] = raw[rows[inside], cols[inside]]
            coverage[yy, xx] = True
        assert np.array_equal(coverage, binary(item["mask"]))
        candidate = rgb(item["file"])
        assert np.array_equal(replay, candidate), f"Raw/mask replay differs: {pid}"
        assert np.array_equal(original[~coverage], candidate[~coverage])
        core_changed = np.any(replay[115:1139, 115:1139] != original[115:1139, 115:1139], axis=2)
        records.append(dict(patch=pid, currentCanonicalSource=str(current),
                            currentCanonicalSha256=sha(current), canonicalMatchesExpected=True,
                            candidate=item["file"], candidateSha256=sha(item["file"]),
                            rawMaskNativeReplayExact=True, savedMaskMatchesCoordinateMapping=True,
                            outsideMaskExact=True, coreChangedPixels=int(core_changed.sum())))
        reconstructed[pid] = replay
    seam = np.concatenate([reconstructed["p43"][115:1139, 883:1139],
                           reconstructed["p44"][115:1139, 115:371]], axis=1)
    with Image.open(Q / "p43--p44-bracket-joint-v2-100pct.png") as im:
        assert im.size == (512, 1024)
        assert np.array_equal(seam, np.array(im.convert("RGB")))
    assert selection_path.read_bytes() == snapshot, "Canonical selection changed during verification"
    for item in source_records:
        assert sha(item["file"]) == item["sha256"], "An input changed during verification"
    report = dict(startedAtUtc=start, completedAtUtc=datetime.now(timezone.utc).isoformat(),
                  status="independent_pixel_replay_passed_current_canonical_matches",
                  canonicalSelection=str(selection_path), canonicalSelectionSha256=snapshot_sha,
                  currentSelectedPositions=len(selection["patches"]),
                  currentOtherPatchEntries={k: v for k, v in selection["patches"].items() if k not in ("p43", "p44")},
                  inputSelectedCoreReplayExact=True, rawCount=2,
                  binaryMaskFiles=[recipe["upperMask"], recipe["cupMask"]],
                  jointRawMaskReplayExact=True, nativeRecords=records, seamCoreReplayExact=True,
                  protectedShaftAndLowerSceneUnchanged=True, sourceInputsStableDuringVerification=True,
                  sourceRecords=source_records, sourceResampling=False, sourceBlur=False,
                  sourcePixelBlending=False, sourceCoordinateMovement=False,
                  canonicalModified=False, imagesModified=False, adoptionExecuted=False,
                  formalAccepted=False, actualModel=None, actualQuality=None)
    return report, snapshot, selection


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Q / "independent-replay-20261013-v3.json")
    args = ap.parse_args()
    assert not args.output.exists(), "Use a new versioned proof path"
    report, _, _ = verify_current()
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"proof": str(args.output), "proofSha256": sha(args.output),
                      "status": report["status"], "nativeRecords": report["nativeRecords"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
