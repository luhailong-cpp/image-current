"""Native partial QA for r09_c05 rows 1-2 and its exported left neighbour.

Produces a 4326x2278 partial context, not a complete or formal 4K tile.
Only original source pixels and integer crops/concatenation are used.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ROOT = QA.parent
PREFIX = "preflight-r09_c05-rows12-v1"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, pixels):
    path = QA / name
    assert path.parent == QA and path.name.startswith(PREFIX) and not path.exists()
    with path.open("xb") as handle:
        Image.fromarray(pixels).save(handle, format="PNG")
    assert np.array_equal(np.asarray(Image.open(path)), pixels)
    return {"path": path.as_posix(), "sha256": sha(path), "size": [pixels.shape[1], pixels.shape[0]]}


def write(name, record):
    path = QA / name
    assert path.parent == QA and path.name.startswith(PREFIX)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def main():
    assemble = load_module(QA / "full-tile-assemble.py", "partial_selector")
    helper = load_module(assemble.HELPER, "partial_seam_helper")
    selected = assemble.select("r09_c05")
    sources, rows, paths = [], [], []
    for row in (1, 2):
        combined = None
        for col in (1, 2, 3, 4):
            version, recpath, rec = selected[row, col]
            path = Path(rec["file"])
            assert sha(path) == rec["sha256"]
            with Image.open(path) as image:
                assert image.size == (1254, 1254) and image.mode in ("RGB", "RGBA")
                if image.mode == "RGBA":
                    assert image.getextrema()[3] == (255, 255)
                pixels = np.asarray(image.convert("RGB")).copy()
            expected = [16269 + (col-1)*1024, 32653 + (row-1)*1024,
                        17523 + (col-1)*1024, 33907 + (row-1)*1024]
            assert rec["coordinates"]["globalContextBox"] == expected
            sources.append({"patch": f"p{row:02d}_{col:02d}", "version": version,
                            "path": path.as_posix(), "sha256": rec["sha256"],
                            "generationRecord": recpath.as_posix(), "recordSha256": sha(recpath),
                            "statusAtSelection": rec.get("status"), "globalContextBox": expected})
            if combined is None:
                combined = pixels
            else:
                seam = helper._minimum_vertical_seam(combined[:, -230:], pixels[:, :230])
                overlap = np.where((np.arange(230)[None, :] >= seam[:, None])[:, :, None],
                                   pixels[:, :230], combined[:, -230:])
                combined = np.concatenate([combined[:, :-230], overlap, pixels[:, 230:]], axis=1)
                paths.append({"id": f"row{row}-c{col-1}-c{col}", "axis": "vertical",
                              "seamXByNativeRowInOverlap": seam.tolist(),
                              "overlapContextBox": [(col-1)*1024, (row-1)*1024,
                                                    (col-1)*1024+230, (row-1)*1024+1254]})
        rows.append(combined)
    seam = helper._minimum_vertical_seam(rows[0][-230:].transpose(1, 0, 2), rows[1][:230].transpose(1, 0, 2))
    overlap = np.where((np.arange(230)[:, None] >= seam[None, :])[:, :, None], rows[1][:230], rows[0][-230:])
    context = np.concatenate([rows[0][:-230], overlap, rows[1][230:]], axis=0)
    paths.append({"id": "row1-row2", "axis": "horizontal", "seamYByColumnInOverlap": seam.tolist(),
                  "overlapContextBox": [0, 1024, 4326, 1254]})
    assert context.shape == (2278, 4326, 3)
    core = context[115:2163, 115:4211].copy()
    context_ref = save(PREFIX + "-partial-context-native.png", context)
    core_ref = save(PREFIX + "-partial-core-4096x2048.png", core)
    qa = []
    boxes = []
    for boundary in (1024, 2048, 3072):
        for part, start in enumerate((0, 700, 1148), 1):
            boxes.append((f"v{boundary}-part{part:02d}", [boundary-345, start, boundary+345, start+900]))
        boxes.append((f"intersection-x{boundary}-y1024", [boundary-450, 574, boundary+450, 1474]))
    for part, start in enumerate((0, 800, 1600, 2400, 3196), 1):
        boxes.append((f"h1024-part{part:02d}", [start, 679, start+900, 1369]))
    for label, box in boxes:
        l, t, r, b = box
        name = PREFIX + "-" + label + "-100pct.png"
        ref = save(name, core[t:b, l:r])
        record = {**ref, "source": core_ref, "sourceBox": box, "operation": "integer crop only",
                  "noResize": True, "noFeather": True, "noDrawing": True}
        write(name + ".derivation.json", record)
        qa.append(record)
    left_path = ROOT / "tiles" / "r09_c04.png"
    left = np.asarray(Image.open(left_path).convert("RGB"))
    assert left.shape == (4096, 4096, 3)
    left_ref = {"path": left_path.as_posix(), "sha256": sha(left_path), "size": [4096, 4096]}
    assert left_ref["sha256"] == "1b34b7380156476a918b2b7ba867b5fcffa1cca0039e4ab10ad4d7ad9883b7ea"
    for part, start in enumerate((0, 700, 1148), 1):
        pixels = np.concatenate([left[start:start+900, -345:], core[start:start+900, :345]], axis=1)
        name = PREFIX + f"-shared-r09c04-right-c05-left-part{part:02d}-100pct.png"
        ref = save(name, pixels)
        record = {**ref, "sources": [{**left_ref, "sourceBox": [3751, start, 4096, start+900], "destinationBox": [0,0,345,900]},
                    {**core_ref, "sourceBox": [0,start,345,start+900], "destinationBox": [345,0,690,900]}],
                  "joinX": 345, "worldBoundaryX": 16384, "globalYRange": [32768+start, 32768+start+900],
                  "operation": "direct juxtaposition of actual core pixels; no cross-tile seam optimization",
                  "noResize": True, "noFeather": True, "noDrawing": True}
        write(name + ".derivation.json", record)
        qa.append(record)
    assert all(sha(s["path"]) == s["sha256"] for s in sources)
    report = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "tile": "r09_c05", "status": "partial_preflight_pending_native_visual_review",
              "notFullTile": True, "formalAcceptedCount": 0,
              "sources": sources, "seams": paths, "context": context_ref, "core": core_ref,
              "leftNeighbour": left_ref, "qa": qa,
              "script": {"path": Path(__file__).as_posix(), "sha256": sha(__file__)},
              "helper": {"path": assemble.HELPER.as_posix(), "sha256": sha(assemble.HELPER)},
              "noResize": True, "noFeather": True, "noColourCorrection": True, "noDrawing": True}
    path = write(PREFIX + "-trace.json", report)
    print(json.dumps({"trace": path.as_posix(), "qaCount": len(qa), "partialDimensions": context_ref["size"]}))


if __name__ == "__main__":
    main()
