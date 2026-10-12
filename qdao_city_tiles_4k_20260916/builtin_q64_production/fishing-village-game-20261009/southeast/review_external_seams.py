"""Build exact-pixel external tile seam evidence from tile-local selections.

Only writes seam-qa/. Missing sources stay pending; no synthetic fill is saved.
Coordinates are global, half-open boxes. All art pixels come from [115:1139]
native cores, including intersections between internal and external seams.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from PIL import Image

BASE = Path(__file__).resolve().parent
TILE_SIZE, CORE_SIZE, HALO, NATIVE_SIZE = 4096, 1024, 115, 1254


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def tile_indices(name):
    match = re.fullmatch(r"r(\d{2})_c(\d{2})", name)
    if not match:
        raise ValueError(f"Invalid tile name: {name}")
    return tuple(map(int, match.groups()))


class Sources:
    def __init__(self):
        self.tiles, self.images = {}, {}

    def tile(self, tile_id):
        if tile_id in self.tiles:
            return self.tiles[tile_id]
        folder = BASE / tile_id
        selected_path = folder / "selected-patches.json"
        plan_path = folder / "coordinate-plan.json"
        # The first tile's original plan predates per-tile plans.
        if not plan_path.exists() and (BASE / "coordinate-plan.json").exists():
            legacy = read_json(BASE / "coordinate-plan.json")
            if legacy.get("tile") == tile_id:
                plan_path = BASE / "coordinate-plan.json"
        result = {"id": tile_id, "folder": folder}
        if not selected_path.exists() or not plan_path.exists():
            result["error"] = "missing_tile_local_selection" if not selected_path.exists() else "missing_coordinate_plan"
        else:
            selected, plan = read_json(selected_path), read_json(plan_path)
            row, col = tile_indices(tile_id)
            origin = [(col - 1) * TILE_SIZE, (row - 1) * TILE_SIZE]
            expected_tile = origin + [origin[0] + TILE_SIZE, origin[1] + TILE_SIZE]
            if selected.get("tile") != tile_id or plan.get("tile") != tile_id:
                raise ValueError(f"Mismatched tile metadata: {tile_id}")
            if plan["tileCoreBox"] != expected_tile:
                raise ValueError(f"Unexpected global tile box: {tile_id}")
            if (plan["corePixels"], plan["haloPixels"], plan["expectedNativeSize"]) != (CORE_SIZE, HALO, [NATIVE_SIZE, NATIVE_SIZE]):
                raise ValueError(f"Unsupported native/core layout: {tile_id}")
            patches = {p["id"]: p for p in plan["patches"]}
            for patch_id, patch in patches.items():
                pr, pc = int(patch_id[1]) - 1, int(patch_id[2]) - 1
                x, y = origin[0] + pc * CORE_SIZE, origin[1] + pr * CORE_SIZE
                if patch["coreBox"] != [x, y, x + CORE_SIZE, y + CORE_SIZE]:
                    raise ValueError(f"Unexpected patch core: {tile_id}/{patch_id}")
                if patch["globalBox"] != [x - HALO, y - HALO, x + CORE_SIZE + HALO, y + CORE_SIZE + HALO]:
                    raise ValueError(f"Unexpected patch context: {tile_id}/{patch_id}")
            result.update(selection=selected, plan=plan, patches=patches,
                          selectedPath=selected_path, selectedSha256=sha(selected_path),
                          planPath=plan_path, planSha256=sha(plan_path))
        self.tiles[tile_id] = result
        return result

    def source(self, tile_id, patch_id):
        tile = self.tile(tile_id)
        if "error" in tile:
            return None, {"tile": tile_id, "patch": patch_id, "reason": tile["error"]}
        entry = tile["selection"]["patches"].get(patch_id)
        if entry is None:
            return None, {"tile": tile_id, "patch": patch_id, "reason": "patch_not_selected"}
        if isinstance(entry, dict):
            entry = entry.get("file") or entry.get("path")
        path = Path(entry)
        if not path.is_absolute():
            path = tile["folder"] / path
        path = path.resolve()
        if not path.exists():
            return None, {"tile": tile_id, "patch": patch_id, "reason": "selected_source_missing", "file": str(path)}
        if path not in self.images:
            with Image.open(path) as source:
                if source.size != (NATIVE_SIZE, NATIVE_SIZE):
                    return None, {"tile": tile_id, "patch": patch_id, "reason": "wrong_native_size", "dimensions": list(source.size)}
                if "A" in source.getbands() and source.getchannel("A").getextrema() != (255, 255):
                    return None, {"tile": tile_id, "patch": patch_id, "reason": "nonopaque_source"}
                self.images[path] = source.convert("RGB").copy()
        patch = tile["patches"][patch_id]
        return {"tile": tile_id, "patch": patch_id, "file": str(path), "sha256": sha(path),
                "selectedManifest": str(tile["selectedPath"]), "selectedManifestSha256": tile["selectedSha256"],
                "coordinatePlan": str(tile["planPath"]), "coordinatePlanSha256": tile["planSha256"],
                "coreBoxGlobal": patch["coreBox"], "nativeBoxGlobal": patch["globalBox"]}, None

    def extract(self, box):
        x0, y0, x1, y1 = box
        pieces, missing = [], []
        for gy in range(y0 // CORE_SIZE, (y1 - 1) // CORE_SIZE + 1):
            for gx in range(x0 // CORE_SIZE, (x1 - 1) // CORE_SIZE + 1):
                tile_id = f"r{gy // 4 + 1:02d}_c{gx // 4 + 1:02d}"
                patch_id = f"p{gy % 4 + 1}{gx % 4 + 1}"
                source, error = self.source(tile_id, patch_id)
                if error:
                    missing.append(error)
                    continue
                cx0, cy0, cx1, cy1 = source["coreBoxGlobal"]
                ix0, iy0, ix1, iy1 = max(x0, cx0), max(y0, cy0), min(x1, cx1), min(y1, cy1)
                nx0, ny0 = source["nativeBoxGlobal"][:2]
                crop = [ix0 - nx0, iy0 - ny0, ix1 - nx0, iy1 - ny0]
                assert HALO <= crop[0] < crop[2] <= HALO + CORE_SIZE
                assert HALO <= crop[1] < crop[3] <= HALO + CORE_SIZE
                pieces.append(dict(source, sourceCrop=crop, destination=[ix0 - x0, iy0 - y0]))
        if missing:
            return None, pieces, missing
        result = Image.new("RGB", (x1 - x0, y1 - y0))
        for piece in pieces:
            result.paste(self.images[Path(piece["file"])].crop(piece["sourceCrop"]), tuple(piece["destination"]))
        return result, pieces, []


def write_evidence(sources, folder, identifier, box, geometry):
    path = folder / (identifier + ".qa.json")
    old = read_json(path) if path.exists() else {}
    image, pieces, missing = sources.extract(box)
    signature = [{k: p[k] for k in ("tile", "patch", "file", "sha256", "sourceCrop", "destination")} for p in pieces]
    review = {"status": "pending_missing_sources" if missing else "pending_view_image_review",
              "structuralBlockers": [], "colorOnlyRisks": [], "candidateUsable": None, "formalAccepted": False,
              "note": "Empty issue arrays do not imply visual acceptance."}
    if not missing and old.get("sourcePixelSignature") == signature and old.get("globalBox") == box:
        review = old.get("visualReview", review)
    record = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "id": identifier,
              "globalBox": box, "coordinateConvention": "global pixels, half-open boxes",
              "geometry": geometry, "sourcePixelSignature": signature, "sources": pieces,
              "missingSources": missing, "sourceComplete": not missing,
              "operation": "paste exact native core crops; no resampling, movement, synthesis, color processing, blending or feathering",
              "image": None, "visualReview": review}
    if image is not None:
        output = folder / (identifier + "-100pct.png")
        image.save(output)
        record["image"] = {"file": str(output), "sha256": sha(output), "dimensions": list(image.size), "resized": False}
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"report": str(path), "id": identifier, "globalBox": box, "sourceComplete": not missing,
            "missingSources": missing, "image": record["image"], "visualReview": review}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", default="r10_c09")
    parser.add_argument("--edges", nargs="+", choices=["east", "south", "west", "north"], default=["east", "south", "west"])
    parser.add_argument("--strip-width", type=int, default=512)
    parser.add_argument("--intersection-width", type=int, default=768)
    args = parser.parse_args()
    if any(w <= 0 or w % 2 or w > 1024 for w in (args.strip_width, args.intersection_width)):
        raise ValueError("Crop widths must be even and between 2 and 1024")
    row, col = tile_indices(args.center)
    x, y = (col - 1) * TILE_SIZE, (row - 1) * TILE_SIZE
    folder = BASE / "seam-qa" / args.center
    folder.mkdir(parents=True, exist_ok=True)
    sources, edges, corners = Sources(), [], {}
    half, ch = args.strip_width // 2, args.intersection_width // 2
    for edge in args.edges:
        vertical = edge in ("east", "west")
        seam = x + TILE_SIZE if edge == "east" else x if edge == "west" else y + TILE_SIZE if edge == "south" else y
        start = y if vertical else x
        def box_at(lo, hi):
            return [seam - half, lo, seam + half, hi] if vertical else [lo, seam - half, hi, seam + half]
        geometry = {"edgeOfCenterTile": edge, "seamAxis": "x" if vertical else "y", "seamGlobalCoordinate": seam,
                    "seamCoordinateInStrip": half, "width": args.strip_width}
        full = write_evidence(sources, folder, edge + "-full", box_at(start, start + TILE_SIZE), geometry)
        segments = []
        for index in range(4):
            segments.append(write_evidence(sources, folder, f"{edge}-segment-{index + 1}",
                                          box_at(start + index * CORE_SIZE, start + (index + 1) * CORE_SIZE), geometry))
        edges.append({"edge": edge, "full": full, "segments": segments})
        for index in range(5):
            px, py = (seam, start + index * CORE_SIZE) if vertical else (start + index * CORE_SIZE, seam)
            key = f"intersection-x{px}-y{py}"
            if key not in corners:
                corners[key] = write_evidence(sources, folder, key, [px - ch, py - ch, px + ch, py + ch],
                                              {"intersectionGlobal": [px, py], "intersectionInImage": [ch, ch]})
    summary = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "centerTile": args.center,
               "tileCoreBox": [x, y, x + TILE_SIZE, y + TILE_SIZE], "script": str(Path(__file__).resolve()),
               "scriptSha256": sha(Path(__file__).resolve()), "coreCropNative": [115, 115, 1139, 1139],
               "edges": edges, "intersections": list(corners.values()), "formalAccepted": False,
               "status": "mechanical_evidence_ready_or_pending_by_source; visual review required"}
    (folder / "external-seam-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(folder), "edges": [{"edge": e["edge"], "fullSourceComplete": e["full"]["sourceComplete"],
                      "readySegments": sum(s["sourceComplete"] for s in e["segments"])} for e in edges],
                      "readyIntersections": sum(c["sourceComplete"] for c in corners.values()), "totalIntersections": len(corners)}))


if __name__ == "__main__":
    main()
