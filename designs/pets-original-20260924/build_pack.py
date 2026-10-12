"""Deterministic pet extraction/export. Does not generate art or approve its appearance."""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
VERSION = 2
DIRECTIONS = ("E", "W")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(Path(path).resolve())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def reference_details(references):
    index = ROOT / "references/input-index.json"
    archives = {r["source"].replace("\\", "/"): r["archivedAs"] for r in read_json(index).get("references", [])} if index.exists() else {}
    result = []
    for reference in references:
        row = dict(reference) if isinstance(reference, dict) else {"path": reference}
        path = str(row.get("path", "")).replace("\\", "/")
        normalized = path.lower()
        if "pets-20260924/" in normalized or "codex-clipboard" in normalized:
            raise ValueError("Rejected candidate or external game screenshot cannot be a new original-design generation reference")
        if "role" not in row:
            if path.endswith("designs/team-ui-v2/team-ui-v2.png"):
                row["role"] = "approved primary art style, as stated in generation prompt"
            elif "/source/" in path or path.startswith("source/"):
                row["role"] = "same-pet identity and costume reference for the separately generated direction"
            else:
                row["role"] = "unclassified reference; must be reviewed against the original-design reference policy"
        if path in archives:
            row["archive"] = archives[path]
        result.append(row)
    return result


def source_from_hint(hint):
    candidate = (hint or "").partition(" as ")[2].partition(" by default.")[0]
    return candidate if candidate.endswith(".png") else None


def write_if_changed(path, data):
    path = Path(path)
    if isinstance(data, dict) or isinstance(data, list):
        data = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    elif isinstance(data, str):
        data = data.encode("utf-8")
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".build-tmp")
    temp.write_bytes(data)
    temp.replace(path)
    return True


def png_bytes(im):
    output = io.BytesIO()
    im.save(output, format="PNG", compress_level=9)
    return output.getvalue()


def import_provenance_reader():
    path = REPO / "qdao_original_roster_v14_hd/tools/inspect_image_provenance.py"
    spec = importlib.util.spec_from_file_location("pet_source_provenance", path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # Existing inspector directory is read-only.
    spec.loader.exec_module(module)
    return module.inspect_image, path


def components(mask, limit=80):
    """4-connected run-length components; deterministic and linear in occupied rows."""
    height, width = mask.shape
    parents, areas, bounds = [], [], []
    previous = []

    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for y in range(height):
        row = np.pad(mask[y].astype(np.int8), (1, 1))
        edges = np.diff(row)
        starts = np.flatnonzero(edges == 1)
        ends = np.flatnonzero(edges == -1)
        current = []
        scan = 0
        for x0, x1 in zip(starts.tolist(), ends.tolist()):
            idx = len(parents)
            parents.append(idx)
            areas.append(x1 - x0)
            bounds.append([x0, y, x1, y + 1])
            while scan < len(previous) and previous[scan][1] <= x0:
                scan += 1
            for old_x0, old_x1, old_idx in previous[scan:]:
                if old_x0 >= x1:
                    break
                a, b = root(idx), root(old_idx)
                if a != b:
                    parents[max(a, b)] = min(a, b)
            current.append((x0, x1, idx))
        previous = current
    groups = {}
    for i, area in enumerate(areas):
        rid = root(i)
        box = bounds[i]
        if rid not in groups:
            groups[rid] = {"area": 0, "bbox": box.copy(), "seed": [box[0], box[1]]}
        item = groups[rid]
        item["area"] += area
        out = item["bbox"]
        out[0], out[1] = min(out[0], box[0]), min(out[1], box[1])
        out[2], out[3] = max(out[2], box[2]), max(out[3], box[3])
    result = sorted(groups.values(), key=lambda x: (-x["area"], x["bbox"]))
    return result[:limit], len(result), sum(r["area"] for r in result if r["area"] <= 16)


def connected_background(mask):
    """Flood only matching background connected to the canvas boundary."""
    height, width = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    queue = deque()
    for y, x in [(0, x) for x in range(width)] + [(height - 1, x) for x in range(width)] + [(y, 0) for y in range(height)] + [(y, width - 1) for y in range(height)]:
        if mask[y, x] and not seen[y, x]:
            seen[y, x] = True
            queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < height and 0 <= xx < width and mask[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True
                queue.append((yy, xx))
    return seen



def decontaminate_magenta_edge(data, background, options):
    """Unmix matte only in a narrow opt-in edge band of an opaque key source."""
    radius = int(options.get("radius", 2))
    if not 1 <= radius <= 3:
        raise ValueError("Magenta edge radius must be 1, 2 or 3 pixels")
    rgb = data[:, :, :3].astype(np.float64)
    original_alpha = data[:, :, 3].copy()
    matte = np.median(rgb[background], axis=0)
    background_image = Image.fromarray((background * 255).astype(np.uint8))
    near_background = np.asarray(background_image.filter(ImageFilter.MaxFilter(radius * 2 + 1))) > 0
    # The estimate is at least radius+1 pixels inside, away from key-colour mixing.
    outer_core = np.asarray(background_image.filter(ImageFilter.MaxFilter((radius + 1) * 2 + 1))) > 0
    core = (original_alpha > 0) & ~outer_core
    red_dominant = (rgb[:, :, 0] > rgb[:, :, 2] * 1.65) & (rgb[:, :, 0] - rgb[:, :, 1] > 35)
    magenta_excess = np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - rgb[:, :, 1] >= 3
    candidates = near_background & (original_alpha > 0) & magenta_excess & ~red_dominant
    ys, xs = np.where(candidates)
    estimates = np.zeros((len(ys), 3), dtype=np.float64)
    found = np.zeros(len(ys), dtype=bool)
    search_radius = radius + 4
    offsets = sorted(
        ((dy, dx) for dy in range(-search_radius, search_radius + 1)
         for dx in range(-search_radius, search_radius + 1)
         if 0 < dy * dy + dx * dx <= search_radius * search_radius),
        key=lambda offset: (offset[0] ** 2 + offset[1] ** 2, offset),
    )
    height, width = background.shape
    for dy, dx in offsets:
        eligible = np.flatnonzero(~found & (ys + dy >= 0) & (ys + dy < height) & (xs + dx >= 0) & (xs + dx < width))
        if not len(eligible):
            continue
        take = eligible[core[ys[eligible] + dy, xs[eligible] + dx]]
        estimates[take] = rgb[ys[take] + dy, xs[take] + dx]
        found[take] = True
    colour = rgb[ys, xs]
    # Fit foreground intensity as well as matte fraction so a painted dark
    # contour is not mistaken for a bad fit against the brighter inner material.
    ff = np.sum(estimates * estimates, axis=1)
    mm = float(np.sum(matte * matte))
    fm = np.sum(estimates * matte, axis=1)
    cf = np.sum(colour * estimates, axis=1)
    cm = np.sum(colour * matte, axis=1)
    determinant = ff * mm - fm * fm
    stable = determinant > 1e-6
    foreground_coefficient = np.divide(cf * mm - cm * fm, determinant, out=np.zeros(len(ys)), where=stable)
    fraction = np.divide(cm * ff - cf * fm, determinant, out=np.zeros(len(ys)), where=stable)
    brightness = np.divide(foreground_coefficient, 1 - fraction, out=np.zeros(len(ys)), where=np.abs(1 - fraction) > 1e-6)
    residual = colour - (foreground_coefficient[:, None] * estimates + fraction[:, None] * matte)
    rms = np.sqrt(np.mean(residual * residual, axis=1))
    accepted = found & stable & (fraction >= .01) & (fraction <= .95) & (rms <= 24) & (brightness >= .05) & (brightness <= 1.35)
    yy, xx = ys[accepted], xs[accepted]
    keep_alpha = 1 - fraction[accepted]
    unmixed = (colour[accepted] - fraction[accepted, None] * matte) / keep_alpha[:, None]
    data[yy, xx, :3] = np.clip(np.rint(unmixed), 0, 255).astype(np.uint8)
    data[yy, xx, 3] = np.rint(original_alpha[yy, xx] * keep_alpha).astype(np.uint8)
    return {
        "enabled": True, "applied": bool(len(yy)),
        "method": "bounded-edge-matte-unmix-with-nearest-clean-interior-colour",
        "radius": radius, "interiorInset": radius + 1, "searchRadius": search_radius,
        "matteRgb": matte.tolist(), "magentaExcessMinimum": 3,
        "mixtureFractionRange": [.01, .95], "fitRmsMaximum": 24, "foregroundBrightnessRange": [.05, 1.35],
        "candidatePixels": int(len(ys)), "modifiedPixels": int(len(yy)),
        "alphaModifiedPixels": int(np.count_nonzero(data[:, :, 3] != original_alpha)),
        "protectedRedDominantPixels": int(np.count_nonzero(near_background & (original_alpha > 0) & red_dominant)),
        "maxObservedRms": round(float(rms[accepted].max()), 4) if len(yy) else None,
        "nativeRgbaUntouched": True,
        "note": "Only opted-in originally opaque edge-connected-magenta extraction; original source is unchanged. Red-dominant knot colours and all interior pixels are excluded.",
    }


def clear_reviewed_magenta_pockets(data, source_path, options):
    """Clear only reviewed key-colour pixels in source-hash-guarded small boxes."""
    if not options:
        return {"enabled": False, "applied": False, "removedPixels": 0}
    expected_hash = options.get("sourceSha256")
    if not expected_hash or sha(Path(source_path).read_bytes()) != expected_hash:
        raise ValueError("Reviewed magenta-pocket source SHA256 does not match")
    height, width = data.shape[:2]
    regions = []
    for region in options.get("regions", []):
        box = [int(v) for v in region["box"]]
        if len(box) != 4:
            raise ValueError("Magenta-pocket box needs four source coordinates")
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height) or (x1-x0)*(y1-y0) > 4096:
            raise ValueError("Magenta-pocket box must be a bounded reviewed source region <=4096 pixels")
        roi = data[y0:y1, x0:x1]
        rgb = roi[:, :, :3].astype(np.int16)
        # Saturated key colour and its local mixed fringe; preserve red knot paint.
        selected = ((roi[:, :, 3] > 0) & (rgb[:, :, 0] >= 60) & (rgb[:, :, 2] >= 60)
                    & (np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - rgb[:, :, 1] >= 20)
                    & (rgb[:, :, 0] <= rgb[:, :, 2] * 1.65))
        yy, xx = np.where(selected)
        roi[selected, 3] = 0
        regions.append({"reviewedSourceBox": box, "reason": region.get("reason"),
                        "removedPixels": int(len(xx)),
                        "removedSourceBbox": [int(xx.min()+x0), int(yy.min()+y0), int(xx.max()+x0+1), int(yy.max()+y0+1)] if len(xx) else None})
    removed = sum(region["removedPixels"] for region in regions)
    return {"enabled": True, "applied": bool(removed), "method": "reviewed-bounded-key-colour-alpha-only-clear",
            "sourceSha256": expected_hash, "coordinateSpace": "native-source-top-left-pixels-half-open-box",
            "selector": {"minimumRedBlue": 60, "minimumMagentaExcess": 20, "maximumRedBlueRatio": 1.65},
            "regions": regions, "removedPixels": removed, "rgbModifiedPixels": 0,
            "nativeSourceUnchanged": True, "note": "Only explicitly reviewed enclosed background gaps are affected; no global pink removal."}


def extract(path, policy="auto", cleanup_small=False, edge_decontamination=None, pocket_cleanup=None):
    with Image.open(path) as raw:
        mode = raw.mode
        im = raw.convert("RGBA")
    data = np.array(im)
    alpha = data[:, :, 3]
    border_alpha = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
    has_transparency = bool(np.any(alpha < 255))
    rgb = data[:, :, :3].astype(np.int16)
    magenta = (rgb[:, :, 0] >= 180) & (rgb[:, :, 2] >= 180) & (rgb[:, :, 1] <= 80) & (np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - rgb[:, :, 1] >= 110)
    border_key = np.concatenate([magenta[0], magenta[-1], magenta[:, 0], magenta[:, -1]])
    removed = 0
    edge_cleanup = {"enabled": bool(edge_decontamination), "applied": False, "modifiedPixels": 0, "reason": "disabled-or-native-rgba"}
    operation = "preserve-native-rgba"
    if policy == "connected-magenta" or (policy == "auto" and not has_transparency and np.mean(border_key) >= .8):
        connected = connected_background(magenta)
        removed = int(np.count_nonzero(connected & (alpha > 0)))
        data[connected, 3] = 0
        operation = "remove-edge-connected-magenta-only"
        if edge_decontamination and not has_transparency:
            edge_cleanup = decontaminate_magenta_edge(data, connected, edge_decontamination)
        im = Image.fromarray(data)
    elif not has_transparency:
        raise ValueError("Source has neither usable alpha nor a reliably detected magenta boundary; manual review required")
    pocket_result = clear_reviewed_magenta_pockets(data, path, pocket_cleanup)
    if pocket_result["applied"]:
        im = Image.fromarray(data)
    alpha = data[:, :, 3]
    remote_alpha_one = 0
    remote_preserve_box = None
    if cleanup_small:
        stronger = np.argwhere(alpha >= 2)
        if len(stronger):
            by0, bx0 = stronger.min(axis=0).tolist()
            by1, bx1 = (stronger.max(axis=0) + 1).tolist()
            bx0, by0 = max(0, bx0 - 8), max(0, by0 - 8)
            bx1, by1 = min(im.width, bx1 + 8), min(im.height, by1 + 8)
            remote_preserve_box = [bx0, by0, bx1, by1]
            remote = alpha == 1
            remote[by0:by1, bx0:bx1] = False
            remote_alpha_one = int(np.count_nonzero(remote))
            data[remote, 3] = 0
            im = Image.fromarray(data)
            alpha = data[:, :, 3]
    visible = alpha >= 16
    coords = np.argwhere(visible)
    if not len(coords):
        raise ValueError("Source is empty after alpha extraction")
    y0, x0 = coords.min(axis=0).tolist()
    y1, x1 = (coords.max(axis=0) + 1).tolist()
    comps, count, small_pixels = components(visible)
    cleanup = []
    if cleanup_small:
        all_comps, _, _ = components(visible, limit=100000)
        for comp in all_comps[1:]:
            bx0, by0, bx1, by1 = comp["bbox"]
            if comp["area"] > 16 or bx1 - bx0 > 8 or by1 - by0 > 8:
                continue
            x, y = comp["seed"]
            todo, visited = [(y, x)], set()
            while todo:
                yy, xx = todo.pop()
                if (yy, xx) in visited or not (0 <= yy < im.height and 0 <= xx < im.width) or not visible[yy, xx]:
                    continue
                visited.add((yy, xx))
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    todo.append((yy + dy, xx + dx))
            for yy, xx in visited:
                data[yy, xx, 3] = 0
            cleanup.append({"area": len(visited), "bbox": comp["bbox"]})
        im = Image.fromarray(data)
        alpha = data[:, :, 3]
        visible = alpha >= 16
        coords = np.argwhere(visible)
        y0, x0 = coords.min(axis=0).tolist()
        y1, x1 = (coords.max(axis=0) + 1).tolist()
    post_comps, post_count, post_small = components(visible)
    rgb = data[:, :, :3].astype(np.int16)
    magenta = (rgb[:, :, 0] >= 180) & (rgb[:, :, 2] >= 180) & (rgb[:, :, 1] <= 80) & (np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - rgb[:, :, 1] >= 110)
    saturated = (rgb.max(axis=2) - rgb.min(axis=2) > 160) & (rgb.max(axis=2) >= 180) & visible
    diagnostic = {
        "originalMode": mode, "nativeSize": list(im.size), "operation": operation,
        "hadNativeTransparency": has_transparency, "originalTransparentBoundaryRatio": round(float(np.mean(border_alpha <= 8)), 6),
        "magentaEdgeDecontamination": edge_cleanup,
        "reviewedMagentaPocketCleanup": pocket_result,
        "removedMagentaPixels": removed, "alphaBbox": [x0, y0, x1, y1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)), "partialAlphaPixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
        "alphaComponents": comps, "componentCount": count, "smallComponentPixels": small_pixels,
        "visibleMagentaPixels": int(np.count_nonzero(magenta & visible)),
        "highSaturationPixels": int(np.count_nonzero(saturated)),
        "sourceEdgeTouch": bool(x0 == 0 or y0 == 0 or x1 == im.width or y1 == im.height),
        "visualReview": "pending", "componentsWereRemoved": bool(cleanup),
        "removedComponents": cleanup, "removedComponentPixels": sum(c["area"] for c in cleanup),
        "postCleanupComponentCount": post_count, "postCleanupSmallComponentPixels": post_small,
        "mainComponentBbox": post_comps[0]["bbox"],
        "remoteAlphaOneCleanup": {"removedPixels": remote_alpha_one, "alphaValue": 1, "preserveBox": remote_preserve_box, "padding": 8, "method": "clear only 1/255 alpha outside the >=2-alpha envelope plus 8px; preserve near-contour antialias"},
    }
    return im, diagnostic


def find_source(pet, direction):
    normal = ROOT / "source" / f"{pet['slug']}-{direction}.png"
    if normal.exists():
        return normal
    alternate = pet.get("sourceOverrides", {}).get(direction)
    return ROOT / alternate if alternate and (ROOT / alternate).exists() else None


def generation_record(path, pet, direction, snapshot, inspect, inspect_path, write=True):
    digest = sha(path.read_bytes())
    target = Path(str(path) + ".generation.json")
    if target.exists():
        previous = read_json(target)
        if previous.get("sha256") == digest:
            # Decode the inspector's CBOR tag wrapper without inventing a timestamp.
            if isinstance(previous.get("generatedAt"), dict) and "value" in previous["generatedAt"]:
                previous["generatedAt"] = previous["generatedAt"]["value"]
                if write:
                    write_if_changed(target, previous)
            previous["references"] = reference_details(previous.get("references", []))
            if not previous.get("toolSource"):
                previous["toolSource"] = source_from_hint(previous.get("evidence", {}).get("toolOutputHint"))
            if write:
                write_if_changed(target, previous)
            return target, previous
        # Old snapshots are never rewritten to match a replacement image.
        history = ROOT / "records/history" / f"{path.stem}-{previous.get('sha256', 'unknown')[:16]}.generation.json"
        if write:
            write_if_changed(history, previous)
    evidence = inspect(path)
    prov_path = ROOT / "records/provenance" / f"{path.stem}-{digest[:16]}.json"
    created = evidence.get("created_actions", [])
    timestamps = [a.get("when").get("value") if isinstance(a.get("when"), dict) else a.get("when") for a in created if a.get("when")]
    candidates = [ROOT / "prompts" / f"{path.stem}.txt", ROOT / "prompts" / f"{pet['slug']}.txt"]
    prompt = next((p for p in candidates if p.exists()), None)
    receipts = sorted({p for p in (ROOT / "records").glob(f"*{path.stem}*json") if not p.name.endswith("generation.json")})
    receipt_path = ROOT / "records" / f"{path.stem}.receipt.json"
    receipt = read_json(receipt_path) if receipt_path.exists() else {}
    receipt_digest = receipt.get("sha256")
    if receipt_digest and receipt_digest.lower() != digest:
        raise ValueError("Generator receipt SHA256 does not match source")
    references = reference_details(receipt.get("references", pet.get("references", {}).get(direction, [])))
    submitted = receipt.get("submittedParameters", {"model": None, "quality": None, "note": "No model or quality selectors exposed by tool."})
    source_hint = receipt.get("source") or receipt.get("evidence", {}).get("originalPath") or pet.get("toolSources", {}).get(direction) or source_from_hint(receipt.get("output_hint", receipt.get("evidence", {}).get("output_hint")))
    generated_at = timestamps[0] if timestamps else receipt.get("generatedAt")
    archive = ROOT / "source/native-archive" / f"{path.stem}-{digest[:16]}.png"
    record = {
        "schemaVersion": 1, "file": relative(path), "sha256": digest,
        "generatedAt": generated_at,
        "generatedAtBasis": "embedded-c2pa-created-action-unverified-signature" if timestamps else ("generator-receipt-observed-completion-time" if generated_at else "not-disclosed"),
        "width": evidence["native_size"][0], "height": evidence["native_size"][1], "format": "PNG",
        "tool": "image_gen.imagegen", "route": "builtin-host-managed",
        "toolSource": source_hint,
        "configSnapshot": receipt.get("configSnapshot", snapshot), "configSnapshotBasis": "generation-receipt" if "configSnapshot" in receipt else "batch-start-2026-09-24",
        "userPreference": "GPT Image 2.5 when available, otherwise GPT Image 2.0; high-definition character fidelity",
        "submittedParameters": submitted,
        "actualModel": receipt.get("actualModel"), "actualQuality": receipt.get("actualQuality"),
        "evidence": {"provenance": relative(prov_path), "inspector": str(inspect_path), "receipts": [relative(p) for p in receipts], "embeddedCreatedActions": created, "signatureVerified": False, "toolOutputHint": receipt.get("output_hint", receipt.get("evidence", {}).get("output_hint", receipt.get("evidence", {}).get("toolOutputHint")))},
        "unverifiedReason": "宿主管理，工具未披露实际模型分支及质量；嵌入的软件版本只作元数据证据，不当作 API 型号锁定或签名验证。",
        "prompt": receipt.get("prompt") or (relative(prompt) if prompt else None),
        "references": references,
        "referencesReview": "recorded-from-generator-receipt" if references else "pending-generator-receipt",
        "immutableNativeArchive": relative(archive), "facing": direction,
    }
    if write:
        write_if_changed(archive, path.read_bytes())
        write_if_changed(prov_path, evidence)
        write_if_changed(target, record)
    return target, record


def export_image(path, im, source, generation, operation, details):
    raw = png_bytes(im)
    changed = write_if_changed(path, raw)
    record = {
        "schemaVersion": 1, "file": relative(path), "sha256": sha(raw),
        "width": im.width, "height": im.height, "mode": im.mode,
        "derivedFrom": [{"file": relative(source), "sha256": sha(source.read_bytes()), "generationRecord": relative(generation)}],
        "operation": operation, "processor": "build_pack.py", "processorVersion": VERSION, "processorSha256": sha(Path(__file__).read_bytes()),
        **details,
    }
    write_if_changed(Path(str(path) + ".derived.json"), record)
    return {"file": relative(path), "sha256": record["sha256"], "record": relative(Path(str(path) + ".derived.json"))}, changed


def transform(im, factor, source_anchor, output_anchor, size):
    resized = im.convert("RGBa").resize((max(1, round(im.width * factor)), max(1, round(im.height * factor))), Image.Resampling.LANCZOS).convert("RGBA")
    xy = [round(output_anchor[0] - source_anchor[0] * factor), round(output_anchor[1] - source_anchor[1] * factor)]
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(resized, tuple(xy))
    return out, {"resizedSourceSize": list(resized.size), "pasteOffset": xy, "effectiveScale": [resized.width / im.width, resized.height / im.height]}


def visual_review_state(pet):
    """Expose explicit assistant review evidence, never user or engine approval."""
    path = ROOT / "records" / f"{pet['slug']}-visual-review.json"
    review = read_json(path) if path.exists() else {}
    accepted = {"assistant-reviewed", "accepted-agent-visual-review", "passed-agent-visual-review", "passed-for-static-source-export"}
    status = review.get("assistantVisualReview", review.get("status"))
    reviewed = isinstance(status, str) and status in accepted
    findings = review.get("findings") or {}
    originality = review.get("originality", findings.get("originality"))
    originality_ok = reviewed and bool(originality)
    if isinstance(originality, dict) and "status" in originality:
        originality_ok = originality_ok and originality["status"] in accepted | {"passed", "accepted", "reviewed-against-original-design-intent"}
    record = relative(path) if path.exists() else None
    summary = {
        "visualReview": "assistant-reviewed" if reviewed else "pending",
        "assistantVisualReviewStatus": status,
        "visualReviewRecord": record,
        "originalityReview": "assistant-reviewed" if originality_ok else "pending",
        "userApproved": False,
        "clientIntegrated": False,
    }
    directions = {}
    for direction in DIRECTIONS:
        finding = (review.get("directions") or {}).get(direction, findings.get(direction))
        direction_ok = reviewed and bool(finding)
        if isinstance(finding, dict):
            direction_ok = direction_ok and finding.get("status") in accepted | {"passed", "accepted"}
        directions[direction] = {
            "visualReview": "assistant-reviewed" if direction_ok else "pending",
            "visualReviewRecord": record,
            "assistantVisualReviewFinding": finding,
            "userApproved": False,
            "clientIntegrated": False,
        }
    return summary, directions


def aggregate_review(rows, field, expected_count):
    reviewed = sum(row.get(field) == "assistant-reviewed" for row in rows)
    return "assistant-reviewed" if reviewed == expected_count else ("partial" if reviewed else "pending")


def build(pet, config, snapshot, inspect, inspect_path, diagnose_only):
    result = {"slug": pet["slug"], "name": pet["name"], "kind": pet["kind"], "status": "awaiting-sources", "directions": {}, "warnings": [], "outputs": {}, "visualReview": "pending", "clientIntegration": "not-performed"}
    result.update({"slotReferenceName": pet.get("slotReferenceName"), "clientModelId": pet.get("clientModelId"), "identitySummary": pet.get("identitySummary"), "originalityReview": pet.get("originalityReview", "pending"), "originalityAuditRecord": "records/originality-review.json"})
    review, direction_reviews = visual_review_state(pet)
    result.update(review)
    sources = {}
    for direction in DIRECTIONS:
        path = find_source(pet, direction)
        if path is None:
            result["directions"][direction] = {"status": "missing-source", **direction_reviews[direction]}
            continue
        try:
            im, diag = extract(path, pet.get("backgroundPolicy", "auto"), pet.get("cleanupSmallComponents", False), pet.get("magentaEdgeDecontamination", {}).get(direction), pet.get("reviewedMagentaPocketCleanup", {}).get(direction))
            if min(im.size) < config["minimumNativeSize"]:
                raise ValueError(f"Native source {im.size} is below the required minimum; upsampling prohibited")
            generation, evidence = generation_record(path, pet, direction, snapshot, inspect, inspect_path, write=not diagnose_only)
            box = diag["mainComponentBbox"]
            anchor = pet.get("anchors", {}).get(direction, [(box[0] + box[2] - 1) / 2, box[3] - 1])
            diag.update({"source": relative(path), "sha256": evidence["sha256"], "generationRecord": relative(generation), "sourceAnchor": anchor, "anchorBasis": "manually-configured" if direction in pet.get("anchors", {}) else "main-connected-component-bottom-virtual-feet", "status": "diagnosed", "embeddedCreatedActions": evidence.get("evidence", {}).get("embeddedCreatedActions", [])})
            diag.update(direction_reviews[direction])
            sources[direction] = {"path": path, "image": im, "diagnostic": diag, "generation": generation, "anchor": anchor}
            result["directions"][direction] = diag
            if diag["sourceEdgeTouch"]:
                result["warnings"].append(f"{direction}: source touches canvas edge; check clipped body/wing/tail")
            if diag["postCleanupSmallComponentPixels"]:
                result["warnings"].append(f"{direction}: {diag['postCleanupSmallComponentPixels']} pixels in disconnected components <=16 px; retained for review")
            if diag["visibleMagentaPixels"]:
                result["warnings"].append(f"{direction}: visible magenta/pink pixels retained; check whether intended color or fringe")
        except Exception as error:
            result["directions"][direction] = {"status": "processing-error", "source": relative(path), "error": str(error), **direction_reviews[direction]}
    if not diagnose_only:
        for direction, item in sources.items():
            alias_name = pet.get("sourceOverrides", {}).get(direction)
            alias = ROOT / alias_name if alias_name else None
            if alias and alias.exists() and alias != item["path"] and sha(alias.read_bytes()) == sha(item["path"].read_bytes()):
                write_if_changed(Path(str(alias) + ".derived.json"), {"schemaVersion": 1, "file": relative(alias), "sha256": sha(alias.read_bytes()), "operation": "byte-identical-native-source-alias", "derivedFrom": [{"file": relative(item["path"]), "sha256": sha(item["path"].read_bytes()), "generationRecord": relative(item["generation"])}]})
    if not sources:
        return result
    if diagnose_only:
        result["status"] = "diagnostics-only-no-exports"
        return result
    if len(sources) < 2:
        result["status"] = "awaiting-direction-pair-no-runtime-exports"
        return result
    size, margin = config["runtimeSize"], config["safeMargin"]
    output_anchor = [round(size * config["runtimePivot"][0]), round(size * (1 - config["runtimePivot"][1]))]
    factor = 1.0
    for item in sources.values():
        x0, y0, x1, y1 = item["diagnostic"]["alphaBbox"]
        ax, ay = item["anchor"]
        spans = [(ax - x0, output_anchor[0] - margin), (x1 - 1 - ax, size - 1 - margin - output_anchor[0]), (ay - y0, output_anchor[1] - margin), (y1 - 1 - ay, size - 1 - margin - output_anchor[1])]
        for extent, room in spans:
            if extent > 0:
                factor = min(factor, room / extent)
    if "sharedScale" in pet:
        if not 0 < pet["sharedScale"] <= min(1, factor):
            result["status"] = "invalid-shared-scale"
            result["warnings"].append("Configured sharedScale would upscale or clip the silhouette")
            return result
        factor = pet["sharedScale"]
    result["sharedScale"] = factor
    result["runtimePivotBottomOrigin"] = config["runtimePivot"]
    result["runtimeAnchorTopOriginPixels"] = output_anchor
    if factor < .45:
        result["warnings"].append("Wide silhouette requires scale below 0.45; inspect actual body legibility")
    for direction, item in sources.items():
        out, transform_info = transform(item["image"], factor, item["anchor"], output_anchor, size)
        details = {"facing": direction, "sharedScale": factor, "sourceAnchor": item["anchor"], "runtimeAnchorTopOriginPixels": output_anchor, "runtimePivotBottomOrigin": config["runtimePivot"], "sourceNativeSize": list(item["image"].size), "sourceAlphaBbox": item["diagnostic"]["alphaBbox"], "alphaBbox": out.getchannel("A").getbbox(), "resample": "premultiplied-alpha-LANCZOS", "upscaled": False, "mirrored": False, **transform_info}
        details["alphaExtraction"] = item["diagnostic"]["operation"]
        details["magentaEdgeDecontamination"] = item["diagnostic"]["magentaEdgeDecontamination"]
        details["reviewedMagentaPocketCleanup"] = item["diagnostic"]["reviewedMagentaPocketCleanup"]
        details["remoteAlphaOneCleanup"] = item["diagnostic"]["remoteAlphaOneCleanup"]
        details["smallComponentCleanup"] = {"enabled": pet.get("cleanupSmallComponents", False), "alphaThreshold": 16, "maxArea": 16, "maxWidthHeight": 8, "removed": item["diagnostic"].get("removedComponents", []), "removedPixels": item["diagnostic"].get("removedComponentPixels", 0)}
        body = pet.get("bodyBounds", {}).get(direction)
        if body:
            details["bodySizeAfterScale"] = [(body[2] - body[0]) * factor, (body[3] - body[1]) * factor]
            if details["bodySizeAfterScale"][1] < 320:
                result["warnings"].append(f"{direction}: configured anatomical body renders below 320px high; check legibility")
        result["outputs"][f"idle_{direction}"], _ = export_image(ROOT / "runtime" / pet["slug"] / f"idle_{direction}.png", out, item["path"], item["generation"], "extract-alpha-and-shared-scale-align", details)
        if direction == pet.get("uiDirection", "E"):
            result["outputs"]["fullbody_1024"], _ = export_image(ROOT / "ui" / pet["slug"] / "fullbody_1024.png", out, item["path"], item["generation"], "ui-fullbody-from-shared-scale-static-pose", details)
    portrait = pet.get("portrait")
    if not portrait or not portrait.get("reviewed"):
        result["warnings"].append("Portrait pending: configure a visually reviewed face/head crop in asset-config.json")
        result["portraitStatus"] = "pending-manual-face-crop"
    else:
        item = sources[portrait.get("direction", "E")]
        crop = [int(v) for v in portrait["crop"]]
        if len(crop) != 4 or crop[0] < 0 or crop[1] < 0 or crop[2] > item["image"].width or crop[3] > item["image"].height or min(crop[2] - crop[0], crop[3] - crop[1]) <= 0:
            raise ValueError(f"Invalid portrait crop for {pet['slug']}: {crop}")
        head = item["image"].crop(crop)
        portrait_factor = min(1, 512 / head.width, 512 / head.height)
        head = head.convert("RGBa").resize((round(head.width * portrait_factor), round(head.height * portrait_factor)), Image.Resampling.LANCZOS).convert("RGBA")
        canvas = Image.new("RGBA", (512, 512))
        canvas.alpha_composite(head, ((512 - head.width) // 2, (512 - head.height) // 2))
        result["outputs"]["portrait_512"], _ = export_image(ROOT / "ui" / pet["slug"] / "portrait_512.png", canvas, item["path"], item["generation"], "manually-reviewed-face-crop-centered-without-upscale", {"sourceCrop": crop, "cropReviewed": True, "scale": portrait_factor, "upscaled": False, "alphaExtraction": item["diagnostic"]["operation"], "magentaEdgeDecontamination": item["diagnostic"]["magentaEdgeDecontamination"], "reviewedMagentaPocketCleanup": item["diagnostic"]["reviewedMagentaPocketCleanup"], "smallComponentCleanup": {"removed": item["diagnostic"]["removedComponents"], "removedPixels": item["diagnostic"]["removedComponentPixels"], "alphaThreshold": 16, "maxArea": 16, "maxWidthHeight": 8}, "remoteAlphaOneCleanup": item["diagnostic"]["remoteAlphaOneCleanup"]})
        result["portraitStatus"] = "exported-pending-final-visual-review"
    result["status"] = "exported-assistant-reviewed" if result["visualReview"] == "assistant-reviewed" else "exported-pending-visual-review"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", help="Build/diagnose only these slugs")
    parser.add_argument("--diagnose-only", action="store_true", help="Read pixels and print/save diagnostics; no image or provenance-sidecar exports")
    args = parser.parse_args()
    config = read_json(ROOT / "asset-config.json")
    inspect, inspect_path = import_provenance_reader()
    snapshot_path = ROOT / "records/batch-config-snapshot.json"
    snapshot = read_json(snapshot_path) if snapshot_path.exists() else read_json(REPO / "config/image-generation.json")
    if not args.diagnose_only:
        write_if_changed(snapshot_path, snapshot)
    selected = [p for p in config["pets"] if not args.only or p["slug"] in args.only]
    items = [build(p, config, snapshot, inspect, inspect_path, args.diagnose_only) for p in selected]
    report = {"schemaVersion": 1, "processorVersion": VERSION, "mode": "diagnosis" if args.diagnose_only else "export", "items": items, "claims": {"staticDirectionalPoses": True, "animation": False, "clientIntegration": False, "visualApproval": False, "native4k": False}}
    if args.diagnose_only:
        write_if_changed(ROOT / "records/diagnostics.json", report)
    else:
        prior = read_json(ROOT / "manifest.json") if (ROOT / "manifest.json").exists() else {}
        rows = {row["slug"]: row for row in prior.get("pets", [])}
        rows.update({row["slug"]: row for row in items})
        for pet in config["pets"]:
            rows.setdefault(pet["slug"], {"slug": pet["slug"], "name": pet["name"], "kind": pet["kind"], "status": "awaiting-sources", "outputs": {}, "visualReview": "pending"})
        for pet in config["pets"]:
            rows[pet["slug"]].update({"slotReferenceName": pet.get("slotReferenceName"), "clientModelId": pet.get("clientModelId"), "identitySummary": pet.get("identitySummary"), "originalityAuditRecord": "records/originality-review.json"})
            review, direction_reviews = visual_review_state(pet)
            rows[pet["slug"]].update(review)
            for direction, diagnostic in rows[pet["slug"]].get("directions", {}).items():
                diagnostic.update(direction_reviews.get(direction, {}))
        ordered = [rows[pet["slug"]] for pet in config["pets"]]
        expected_count = config.get("expectedPetCount", len(config["pets"]))
        manifest = {"schemaVersion": 1, "title": f"五行奇谈 · {expected_count}只原创宠物静态双朝向素材", "runtimeSize": config["runtimeSize"], "portraitSize": 512, "runtimePivot": config["runtimePivot"], "enemyFacing": "E", "friendlyFacing": "W", "expectedPetCount": expected_count, "originalityReview": aggregate_review(ordered, "originalityReview", expected_count), "visualReview": aggregate_review(ordered, "visualReview", expected_count), "userApproved": False, "clientIntegrated": False, "animation": False, "pets": ordered}
        write_if_changed(ROOT / "manifest.json", manifest)
        report["items"] = ordered
        write_if_changed(ROOT / "processing-report.json", report)
    print(json.dumps({"mode": report["mode"], "pets": [{"slug": i["slug"], "status": i["status"], "warnings": i["warnings"]} for i in items]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
