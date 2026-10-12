"""Compose native repair crops with four hard minimum-error boundaries.

Run only after the manifest's repair images and SHA256 values are ready:
  python repair-compose.py --manifest repair-r09_c04-v1.manifest.json

All boxes are half-open. tileContextBox is relative to the 4096 core;
contextBox = tileContextBox + 115 in the stable 4326 context image.
The four margin bands are INSIDE repairBounds. Their half-plane
intersection chooses repair pixels; every pixel outside bounds stays old.
The source mask is provenance data, never a game image.
"""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re

import numpy as np
from PIL import Image


QA = Path(__file__).resolve().parent
ZONE = QA.parent
HELPER = ZONE / "tools" / "seam_helpers.py"
NATIVE, CONTEXT, CORE, HALO = 1254, 4326, 4096, 115


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pixel_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def input_ref(ref, label):
    path = Path(ref["path"]).resolve()
    expected = ref["sha256"]
    require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
            label + ": expected explicit lowercase SHA256")
    require(path.is_file(), label + ": missing " + str(path))
    require(sha(path) == expected, label + ": SHA256 mismatch")
    return {"path": path.as_posix(), "sha256": expected}


def load_rgb(path, size):
    with Image.open(path) as image:
        image.load()
        require(image.size == size, str(path) + ": wrong native size")
        require(image.mode in ("RGB", "RGBA"), str(path) + ": expected RGB or opaque RGBA")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), str(path) + ": non-opaque pixels")
        return np.asarray(image.convert("RGB")).copy()


def output_path(name):
    require(Path(name).name == name and name.startswith("repair-"), "Unsafe output name")
    path = QA / name
    require(not path.exists(), "Refusing to overwrite existing output: " + str(path))
    return path


def save_json(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {"path": path.as_posix(), "sha256": sha(path)}


def save_png(path, array):
    with path.open("xb") as handle:
        Image.fromarray(array).save(handle, format="PNG")
    with Image.open(path) as image:
        require(np.array_equal(np.asarray(image), array), "Saved PNG pixel mismatch")
    return {"path": path.as_posix(), "sha256": sha(path), "size": [array.shape[1], array.shape[0]]}


def save_npy(path, array):
    with path.open("xb") as handle:
        np.save(handle, array, allow_pickle=False)
    require(np.array_equal(np.load(path, allow_pickle=False), array), "Saved NPY mismatch")
    return {"path": path.as_posix(), "sha256": sha(path), "shape": list(array.shape), "dtype": str(array.dtype)}


def box(value, label):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) is int for v in value), label + ": expected four integers")
    l, t, r, b = value
    require(l < r and t < b, label + ": empty box")
    return l, t, r, b


def edge_record(side, path, index_start, strip_box, context_box):
    vertical = side in ("left", "right")
    coordinate_offset = strip_box[0] if vertical else strip_box[1]
    local = path.astype(np.int32) + coordinate_offset
    full = [None] * NATIVE
    full[index_start:index_start + len(path)] = local.tolist()
    points = [[int(v + context_box[0]), i + index_start + context_box[1]]
              if vertical else [i + index_start + context_box[0], int(v + context_box[1])]
              for i, v in enumerate(local)]
    require(len(path) > 0 and int(path.min()) >= 0, "Invalid seam")
    require(np.all(np.abs(np.diff(path)) <= 1), "Seam step exceeds one pixel")
    return {"side": side, "axis": "vertical" if vertical else "horizontal",
            "localErrorBand": strip_box, "coordinateByBandIndex": local.tolist(),
            "bandIndexRange": [index_start, index_start + len(path)],
            "xByLocalRow" if vertical else "yByLocalColumn": full,
            "contextPoints": points,
            "repairHalfPlane": {"left": "x >= seamX[y]", "right": "x < seamX[y]",
                                "top": "y >= seamY[x]", "bottom": "y < seamY[x]"}[side],
            "candidateBoundaryNote": "Four candidate paths are intersected; the complete source mask defines the actual retained boundary."}


def closed_mask(old, repair, bounds, margin, context_box, minimum_seam):
    l, t, r, b = bounds
    bands = {"left": [l, t, l + margin, b], "right": [r - margin, t, r, b],
             "top": [l, t, r, t + margin], "bottom": [l, b - margin, r, b]}
    paths, records = {}, []
    for side, strip in bands.items():
        x1, y1, x2, y2 = strip
        old_strip, new_strip = old[y1:y2, x1:x2], repair[y1:y2, x1:x2]
        if side in ("top", "bottom"):
            old_strip = old_strip.transpose(1, 0, 2)
            new_strip = new_strip.transpose(1, 0, 2)
        path = minimum_seam(old_strip, new_strip)
        require(len(path) == (b - t if side in ("left", "right") else r - l), "Wrong seam length")
        require(int(path.min()) >= 0 and int(path.max()) < margin, "Seam outside error band")
        paths[side] = path + (x1 if side in ("left", "right") else y1)
        records.append(edge_record(side, path, t if side in ("left", "right") else l, strip, context_box))
    yy, xx = np.mgrid[t:b, l:r]
    chosen = ((xx >= paths["left"][:, None]) & (xx < paths["right"][:, None]) &
              (yy >= paths["top"][None, :]) & (yy < paths["bottom"][None, :]))
    mask = np.zeros((NATIVE, NATIVE), dtype=np.uint8)
    mask[t:b, l:r] = chosen.astype(np.uint8)
    require(np.all(mask[t + margin:b - margin, l + margin:r - margin] == 1), "Interior is not wholly repair")
    outside = np.ones(mask.shape, dtype=bool)
    outside[t:b, l:r] = False
    require(not mask[outside].any(), "Mask escaped bounds")
    return mask, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = read_json(manifest_path)
    require(manifest.get("schemaVersion") == 1, "Unsupported manifest schema")
    prefix = manifest["outputPrefix"]
    require(re.fullmatch(r"repair-[a-z0-9_-]+", prefix) is not None, "Invalid outputPrefix")
    assembly_ref = input_ref(manifest["baseAssembly"], "baseAssembly")
    assembly = read_json(assembly_ref["path"])
    context_ref = input_ref(assembly["context"], "base context")
    candidate_ref = input_ref(assembly["output"], "base candidate")
    require(candidate_ref["sha256"] == manifest["expectedBaseCandidateSha256"], "Wrong stable base candidate")
    require(assembly["output"]["cropFromContext"] == [115, 115, 4211, 4211], "Unexpected base crop")
    base = load_rgb(context_ref["path"], (CONTEXT, CONTEXT))
    base_candidate = load_rgb(candidate_ref["path"], (CORE, CORE))
    require(np.array_equal(base[HALO:HALO + CORE, HALO:HALO + CORE], base_candidate), "Base context/candidate mismatch")
    inputs = [assembly_ref, context_ref, candidate_ref,
              {"path": manifest_path.as_posix(), "sha256": sha(manifest_path)}]
    repairs = manifest["repairs"]
    require(isinstance(repairs, list) and 1 <= len(repairs) <= 254, "Expected 1..254 repairs")
    prepared, ids = [], set()
    for item in repairs:
        rid = item["id"]
        require(re.fullmatch(r"[a-z0-9_-]+", rid) is not None and rid not in ids, "Invalid or duplicate repair id")
        ids.add(rid)
        tile_box = box(item["tileContextBox"], rid + " tileContextBox")
        context_box = [v + HALO for v in tile_box]
        if "contextBox" in item:
            require(item["contextBox"] == context_box, rid + ": contextBox must equal tileContextBox + 115")
        x1, y1, x2, y2 = context_box
        require(x2 - x1 == NATIVE and y2 - y1 == NATIVE and
                0 <= x1 < x2 <= CONTEXT and 0 <= y1 < y2 <= CONTEXT, rid + ": invalid source context box")
        bounds = box(item["repairBounds"], rid + " repairBounds")
        l, t, r, b = bounds
        margin = item["margin"]
        require(0 <= l < r <= NATIVE and 0 <= t < b <= NATIVE, rid + ": bounds outside native image")
        require(type(margin) is int and margin > 0 and 2 * margin < min(r - l, b - t), rid + ": margin leaves no interior")
        source_ref = input_ref(item["source"], rid + " submitted source crop")
        repair_ref = input_ref(item["repair"], rid + " native AI repair")
        source = load_rgb(source_ref["path"], (NATIVE, NATIVE))
        require(np.array_equal(source, base[y1:y2, x1:x2]), rid + ": submitted source differs from stable base crop")
        repair = load_rgb(repair_ref["path"], (NATIVE, NATIVE))
        inputs.extend([source_ref, repair_ref])
        generation = None
        if item.get("generationRecord"):
            generation = input_ref(item["generationRecord"], rid + " generation record")
            generation_data = read_json(generation["path"])
            if "sha256" in generation_data:
                require(generation_data["sha256"] == repair_ref["sha256"], rid + ": generation record refers to a different repair image")
            inputs.append(generation)
        prepared.append({"id": rid, "source": source_ref, "repair": repair_ref, "generationRecord": generation,
                         "tileContextBox": list(tile_box), "contextBox": context_box,
                         "repairBounds": list(bounds), "margin": margin, "pixels": repair})
    # Reserve every intended output before any composition or file write.
    outputs = {"context": output_path(prefix + "-context-native.png"),
               "candidate": output_path(prefix + "-candidate-4096.png"),
               "sourceIds": output_path(prefix + "-context-source-ids.npy"),
               "trace": output_path(prefix + "-trace.json")}
    for item in prepared:
        stem = prefix + "-" + item["id"]
        item["outputs"] = {"maskNpy": output_path(stem + "-source-mask.npy"),
                           "maskPng": output_path(stem + "-source-mask-bw.png"),
                           "trace": output_path(stem + "-trace.json")}
    spec = importlib.util.spec_from_file_location("repair_hard_seam_helper", HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper_ref = {"path": HELPER.as_posix(), "sha256": sha(HELPER)}
    script_ref = {"path": Path(__file__).resolve().as_posix(), "sha256": sha(__file__)}
    inputs.extend([helper_ref, script_ref])
    current = base.copy()
    source_ids = np.zeros((CONTEXT, CONTEXT), dtype=np.uint8)
    traces = []
    for index, item in enumerate(prepared, 1):
        x1, y1, x2, y2 = item["contextBox"]
        before = current[y1:y2, x1:x2].copy()
        repair = item["pixels"]
        mask, paths = closed_mask(before, repair, item["repairBounds"], item["margin"],
                                  item["contextBox"], helper._minimum_vertical_seam)
        selected = mask.astype(bool)
        after = np.where(selected[:, :, None], repair, before)
        require(np.array_equal(after[selected], repair[selected]), "Repair identity validation failed")
        require(np.array_equal(after[~selected], before[~selected]), "Original identity validation failed")
        current[y1:y2, x1:x2] = after
        source_ids[y1:y2, x1:x2][selected] = index
        npy_ref = save_npy(item["outputs"]["maskNpy"], mask)
        png_ref = save_png(item["outputs"]["maskPng"], mask * np.uint8(255))
        trace = {k: v for k, v in item.items() if k not in ("pixels", "outputs")}
        trace.update({"order": index, "sourceId": index,
                      "comparisonBase": "current composite immediately before this repair",
                      "comparisonPixelsSha256": pixel_sha(before), "resultPixelsSha256": pixel_sha(after),
                      "seams": paths, "sourceMask": {"binaryNpy": npy_ref, "blackWhitePng": png_ref,
                          "legend": {"0": "previous composite", "1": "native AI repair"},
                          "pngDisplayLegend": {"0": "black, previous composite", "255": "white, native AI repair"},
                          "role": "provenance data only; not a game image"},
                      "maskFormula": "insideBounds AND x>=L[y] AND x<R[y] AND y>=T[x] AND y<B[x]",
                      "repairPixelCount": int(mask.sum()),
                      "validation": {"allRepairPixelsIdenticalToNativeRepair": True,
                          "allOtherPixelsIdenticalToPreviousComposite": True,
                          "outsideBoundsUnchanged": True, "interiorWhollyRepair": True}})
        trace_ref = save_json(item["outputs"]["trace"], trace)
        traces.append({"id": item["id"], "order": index, "trace": trace_ref,
                       "source": item["source"], "repair": item["repair"],
                       "contextBox": item["contextBox"], "repairBounds": item["repairBounds"],
                       "sourceMask": trace["sourceMask"]})
    # Full-image pixel provenance verification, including overlapping repairs.
    old_chosen = source_ids == 0
    require(np.array_equal(current[old_chosen], base[old_chosen]), "Unselected base pixels changed")
    for index, item in enumerate(prepared, 1):
        x1, y1, x2, y2 = item["contextBox"]
        selected = source_ids[y1:y2, x1:x2] == index
        require(np.array_equal(current[y1:y2, x1:x2][selected], item["pixels"][selected]), "Final source identity failed")
        require(int((source_ids == index).sum()) == int(selected.sum()), "Source ID outside repair context")
    final = current[HALO:HALO + CORE, HALO:HALO + CORE].copy()
    context_out = save_png(outputs["context"], current)
    candidate_out = save_png(outputs["candidate"], final)
    ids_out = save_npy(outputs["sourceIds"], source_ids)
    for ref in inputs:
        require(sha(ref["path"]) == ref["sha256"], "Input changed during composition: " + ref["path"])
    trace = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
             "status": "native_repair_candidate_pending_visual_and_external_joins", "formalAcceptedCount": 0,
             "manifest": inputs[3], "baseAssembly": assembly_ref, "baseContext": context_ref,
             "baseCandidate": candidate_ref, "script": script_ref, "seamHelper": helper_ref,
             "method": "RGB squared-error seam with existing central/edge regularizer; four hard half-plane intersection",
             "marginConvention": "four width-margin strips strictly inside repairBounds",
             "noResize": True, "noFeather": True, "noColourCorrection": True, "noDrawing": True,
             "repairsInOrder": traces, "context": context_out,
             "candidate": {**candidate_out, "cropFromContext": [115, 115, 4211, 4211],
                           "globalCoreBox": assembly["output"]["globalCoreBox"]},
             "completeContextSourceIds": {**ids_out, "legend": {"0": "stable original context",
                 **{str(i): item["id"] for i, item in enumerate(prepared, 1)}}},
             "validation": {"allInputsUnchanged": True, "allSavedPixelsVerified": True,
                 "allFinalPixelsExactlyMatchRecordedSource": True,
                 "baseContextAndCandidateUnmodified": True, "finalIsExact4096IntegerCrop": True},
             "externalJoinsVerified": False}
    trace_ref = save_json(outputs["trace"], trace)
    print(json.dumps({"candidate": candidate_out, "context": context_out, "trace": trace_ref}, ensure_ascii=False))


if __name__ == "__main__":
    main()
