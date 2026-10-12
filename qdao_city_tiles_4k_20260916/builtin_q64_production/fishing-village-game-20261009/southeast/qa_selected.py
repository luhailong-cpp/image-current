"""Unscaled hard-cut QA for selected native patches; never edits source artwork."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ZONE = Path(__file__).resolve().parent
TILE = ZONE / "r10_c09"
QA = TILE / "qa"
CORE, HALO, NATIVE, HALF_STRIP = 1024, 115, 1254, 256


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    if not path.resolve().is_relative_to(QA.resolve()):
        raise ValueError("QA output outside authorized directory")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def saved_image(image, path):
    if not path.resolve().is_relative_to(QA.resolve()):
        raise ValueError("QA output outside authorized directory")
    image.save(path, format="PNG")
    return {"file": str(path), "sha256": sha(path), "dimensions": list(image.size),
            "resized": False, "sourcePixelResampling": False}


def previous_review(path, sources):
    if path.is_file():
        old = read(path)
        if old.get("sources") == sources:
            return old.get("visualReview", {})
    return {"status": "pending_view_image_review", "structuralBlockers": [],
            "colorOnlyRisks": [], "candidateUsable": None,
            "formalAccepted": False,
            "note": "Empty issue arrays before visual review do not mean acceptance."}


def load_selected(path):
    data = read(path)
    tile_id = data.get("tile", "r10_c09")
    if tile_id != "r10_c09":
        raise ValueError("This QA worker is authorized only for r10_c09")
    raw = data.get("patches", data)
    if isinstance(raw, list):
        raw = {item.get("id", item.get("patchId")): item for item in raw}
    selected = {}
    for patch_id, entry in raw.items():
        match = re.fullmatch(r"p([1-4])([1-4])", patch_id)
        if match is None:
            continue
        value = entry if isinstance(entry, str) else next(
            (entry[k] for k in ("path", "file", "selectedPath", "imagePath") if k in entry), None)
        if not value:
            raise ValueError(f"No image path for {patch_id}")
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = ZONE / candidate if (ZONE / candidate).is_file() else TILE / candidate
        candidate = candidate.resolve()
        if not candidate.is_relative_to(ZONE.resolve()):
            raise ValueError(f"Source outside this zone: {candidate}")
        with Image.open(candidate) as opened:
            opened.load()
            if opened.size != (NATIVE, NATIVE):
                raise ValueError(f"Native dimensions differ from contract: {candidate}, {opened.size}")
            if opened.mode == "RGBA" and opened.getextrema()[3] != (255, 255):
                raise ValueError(f"Nonopaque source: {candidate}")
            image = opened.convert("RGB")
        row, column = map(int, match.groups())
        selected[(row, column)] = {
            "id": patch_id, "image": image,
            "source": {"id": patch_id, "file": str(candidate), "sha256": sha(candidate),
                       "dimensions": [NATIVE, NATIVE],
                       "nativeOriginGlobal": [32768 + (column-1)*CORE-HALO,
                                              36864 + (row-1)*CORE-HALO]},
        }
    if not selected:
        raise ValueError("No selected patches")
    return selected


def seam_metrics(a, b, axis):
    aa = np.asarray(a, dtype=np.int16)
    bb = np.asarray(b, dtype=np.int16)
    if axis == "horizontal":
        left, right = aa[:, CORE:], bb[:, :2*HALO]
        steps = np.abs(aa[:, CORE+HALO-1]-bb[:, HALO]).mean(axis=1)
        natural_a = np.abs(aa[:, CORE+HALO-1]-aa[:, CORE+HALO]).mean(axis=1)
        natural_b = np.abs(bb[:, HALO-1]-bb[:, HALO]).mean(axis=1)
    else:
        left, right = aa[CORE:], bb[:2*HALO]
        steps = np.abs(aa[CORE+HALO-1]-bb[HALO]).mean(axis=1)
        natural_a = np.abs(aa[CORE+HALO-1]-aa[CORE+HALO]).mean(axis=1)
        natural_b = np.abs(bb[HALO-1]-bb[HALO]).mean(axis=1)
    delta = (right-left).reshape(-1, 3)
    median = np.median(delta, axis=0)
    return {
        "diagnosticOnly": True,
        "seamMeanAbsoluteRgbStep": float(steps.mean()),
        "seamP95AbsoluteRgbStep": float(np.percentile(steps, 95)),
        "sameCoordinateOverlapMedianBMinusA": median.tolist(),
        "sameCoordinateOverlapMAD": np.median(np.abs(delta-median), axis=0).tolist(),
        "bands": [{"start": start, "endExclusive": min(start+100, NATIVE),
                   "seamMeanAbsoluteRgbStep": float(steps[start:start+100].mean()),
                   "sourceANaturalColumnOrRowStep": float(natural_a[start:start+100].mean()),
                   "sourceBNaturalColumnOrRowStep": float(natural_b[start:start+100].mean())}
                  for start in range(0, NATIVE, 100)],
        "warning": "Color metrics cannot certify geometry or visual acceptance.",
    }


def seam_report(a, b, axis, stamp):
    identity = f"selected-{a['id']}-{b['id']}-{axis}"
    report_path = QA / f"{identity}.qa.json"
    sources = [a["source"], b["source"]]
    review = previous_review(report_path, sources)
    if axis == "horizontal":
        canvas = Image.new("RGB", (NATIVE+CORE, NATIVE))
        canvas.paste(a["image"].crop((0, 0, CORE+HALO, NATIVE)), (0, 0))
        canvas.paste(b["image"].crop((HALO, 0, NATIVE, NATIVE)), (CORE+HALO, 0))
        crop = (CORE+HALO-HALF_STRIP, 0, CORE+HALO+HALF_STRIP, NATIVE)
        seam_location = {"axis": "x", "stripCoordinate": HALF_STRIP}
    else:
        canvas = Image.new("RGB", (NATIVE, NATIVE+CORE))
        canvas.paste(a["image"].crop((0, 0, NATIVE, CORE+HALO)), (0, 0))
        canvas.paste(b["image"].crop((0, HALO, NATIVE, NATIVE)), (0, CORE+HALO))
        crop = (0, CORE+HALO-HALF_STRIP, NATIVE, CORE+HALO+HALF_STRIP)
        seam_location = {"axis": "y", "stripCoordinate": HALF_STRIP}
    report = {"schemaVersion": 1, "createdAtUtc": stamp, "kind": "full_length_native_pixel_seam",
              "id": identity, "axis": axis, "sources": sources,
              "operation": "hard cut at exact overlap midpoint; crop only; no blending, feathering, resizing, color changes, or coordinate shifts",
              "overlapPixels": 2*HALO, "seam": seam_location,
              "fullPair": saved_image(canvas, QA / f"{identity}-pair.png"),
              "strip": saved_image(canvas.crop(crop), QA / f"{identity}-100pct.png"),
              "stripCropFromPair": list(crop),
              "diagnostics": seam_metrics(a["image"], b["image"], axis),
              "visualReview": review}
    write(report_path, report)
    return {"report": str(report_path), "id": identity, "sources": sources,
            "visualReview": review}


def intersection_report(quartet, stamp):
    ids = [p["id"] for p in quartet]
    identity = "selected-intersection-" + "-".join(ids)
    report_path = QA / f"{identity}.qa.json"
    sources = [p["source"] for p in quartet]
    radius = 384
    canvas = Image.new("RGB", (radius*2, radius*2))
    end = CORE+HALO
    crops = [(end-radius, end-radius, end, end),
             (HALO, end-radius, HALO+radius, end),
             (end-radius, HALO, end, HALO+radius),
             (HALO, HALO, HALO+radius, HALO+radius)]
    offsets = [(0, 0), (radius, 0), (0, radius), (radius, radius)]
    for patch, box, origin in zip(quartet, crops, offsets):
        canvas.paste(patch["image"].crop(box), origin)
    report = {"schemaVersion": 1, "createdAtUtc": stamp, "id": identity,
              "kind": "four_patch_intersection_native_pixel_crop", "sources": sources,
              "operation": "four exact 384-square source crops pasted into 768 square; no pixel processing",
              "sourceCropsInSourceOrder": [list(c) for c in crops],
              "intersectionInOutput": [radius, radius],
              "image": saved_image(canvas, QA / f"{identity}-100pct.png"),
              "visualReview": previous_review(report_path, sources)}
    write(report_path, report)
    return {"report": str(report_path), "id": identity, "sources": sources,
            "visualReview": report["visualReview"]}


def main():
    global QA
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected", type=Path, default=ZONE / "selected-patches.json")
    parser.add_argument("--output-subdir", default="", help="Separate QA run under r10_c09/qa; preserves source QA")
    args = parser.parse_args()
    qa_root = TILE / "qa"
    QA = (qa_root / args.output_subdir).resolve()
    if not QA.is_relative_to(qa_root.resolve()):
        raise ValueError("Output subdirectory escapes authorized QA root")
    selected = load_selected(args.selected)
    QA.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    seams, intersections = [], []
    for (row, column), patch in sorted(selected.items()):
        for key, axis in (((row, column+1), "horizontal"), ((row+1, column), "vertical")):
            if key in selected:
                seams.append(seam_report(patch, selected[key], axis, stamp))
        keys = [(row, column), (row, column+1), (row+1, column), (row+1, column+1)]
        if all(k in selected for k in keys):
            intersections.append(intersection_report([selected[k] for k in keys], stamp))
    summary = {"schemaVersion": 1, "createdAtUtc": stamp,
               "selectedManifest": str(args.selected.resolve()), "selectedManifestSha256": sha(args.selected),
               "script": str(Path(__file__).resolve()), "scriptSha256": sha(Path(__file__)),
               "selectedCount": len(selected), "seams": seams, "intersections": intersections,
               "formalAccepted": False,
               "note": "Only existing selected adjacencies checked; absent patches and external tile/zone edges remain unverified."}
    write(QA / "selected-qa-summary.json", summary)
    print(json.dumps({"selectedCount": len(selected), "seamCount": len(seams),
                      "intersectionCount": len(intersections), "summary": str(QA / "selected-qa-summary.json")}, indent=2))


if __name__ == "__main__":
    main()
