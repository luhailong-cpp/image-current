"""Coordinate guides and native-image provenance only; never assembles final art.

Run with the bundled Python. See --help and each subcommand's --help.
prepare may resample the layout-only overview, but only crops/pastes native
neighbor pixels at 1:1. ingest copies original bytes; it never resizes images.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ZONE = Path(__file__).resolve().parent
ROOT = next(p for p in ZONE.parents if (p / "config/image-generation.json").is_file())
PATCH_RE = re.compile(r"^(r\d{2}_c\d{2}_p[1-4][1-4])(?:-|$)")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path = Path(path).resolve()
    if not path.is_relative_to(ZONE):
        raise ValueError("Output must stay inside this zone")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_ref(path, role):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path), "role": role}


def coordinates(patch_id, zone=ZONE):
    if not re.fullmatch(r"r\d{2}_c\d{2}_p[1-4][1-4]", patch_id):
        raise ValueError("PATCHID must have the form r06_c12_p12")
    tile = patch_id.split("_p")[0]
    candidates = [zone / "records" / (tile + ".coordinates.json"), zone / (tile + ".coordinates.json")]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        raise ValueError(f"Missing coordinates for {patch_id}: {candidates[0]}")
    document = read_json(path)
    patch = next((p for p in document["patches"] if p["id"] == patch_id), None)
    if patch is None:
        raise ValueError(f"Patch absent from coordinates: {patch_id}")
    if patch["expectedSize"] != [1254, 1254]:
        raise ValueError("This plan requires measured 1254-square native images")
    core = patch["coreGlobalBox"]
    native = patch["nativeGlobalBox"]
    if [core[2] - core[0], core[3] - core[1]] != [1024, 1024]:
        raise ValueError("Core must be 1024 square")
    if native != [core[0] - 115, core[1] - 115, core[2] + 115, core[3] + 115]:
        raise ValueError("Native box must have exactly 115 context on every side")
    if patch["nativeCoreBox"] != [115, 115, 1139, 1139]:
        raise ValueError("Unexpected local core box")
    return path, document, patch


def checked_references(document):
    refs = []
    for reference in document["references"]:
        current = file_ref(reference["path"], reference["role"])
        if current["sha256"].lower() != reference["sha256"].lower():
            raise ValueError(f"Reference hash changed: {current['path']}")
        refs.append(current)
    return refs


def intersection(a, b):
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return box if box[2] > box[0] and box[3] > box[1] else None


def local_box(box, origin):
    return [box[0] - origin[0], box[1] - origin[1], box[2] - origin[0], box[3] - origin[1]]


def neighbor_provenance(path, seen=None):
    """Read a neighbor's generation OR mechanical derivation chain, without writes."""
    path = Path(path).resolve()
    seen = set() if seen is None else set(seen)
    if path in seen:
        raise ValueError(f"Cyclic image provenance: {path}")
    seen.add(path)
    for suffix, kind in ((".derived.json", "mechanical_derived"), (".generation.json", "image_gen_native")):
        metadata_path = path.with_name(path.name + suffix)
        if not metadata_path.is_file():
            continue
        metadata = read_json(metadata_path)
        if path.is_file() and metadata.get("sha256") != sha(path):
            raise ValueError(f"Neighbor provenance hash mismatch: {path}")
        result = {"sourceType": kind, "sourceImageAvailable": path.is_file(),
                  "generationRecord": None, "derivedRecord": None}
        key = "derivedRecord" if kind == "mechanical_derived" else "generationRecord"
        result[key] = file_ref(metadata_path, "neighbor " + kind + " provenance")
        if kind == "mechanical_derived":
            result["derivedOperation"] = metadata.get("operation")
            parents = metadata.get("derivedFrom", [])
            if isinstance(parents, dict):
                parents = [parents]
            result["derivedFrom"] = []
            for parent in parents:
                item = dict(parent)
                parent_path = Path(item["path"])
                if not parent_path.is_absolute():
                    parent_path = metadata_path.parent / parent_path
                parent_path = parent_path.resolve()
                if parent_path.is_file() and sha(parent_path) != item.get("sha256"):
                    raise ValueError(f"Derived source hash mismatch: {parent_path}")
                item["provenance"] = neighbor_provenance(parent_path, seen)
                result["derivedFrom"].append(item)
        return result
    return {"sourceType": "unrecorded", "generationRecord": None, "derivedRecord": None,
            "sourceImageAvailable": path.is_file()}


def prepare(args):
    coordinate_path, document, patch = coordinates(args.patch_id)
    contract_path = ZONE.parent / "production-contract.json"
    contract = read_json(contract_path)
    references = checked_references(document)
    if Path(references[0]["path"]).resolve() != Path(contract["layoutReference"]).resolve():
        raise ValueError("First coordinate reference must be the contracted layout")
    if references[0]["sha256"] != contract["layoutSha256"]:
        raise ValueError("Layout hash differs from contract")
    canvas = contract["artCanvasPixels"]
    with Image.open(references[0]["path"]) as layout:
        layout.load()
        if layout.size != (1254, 1254):
            raise ValueError(f"Layout dimensions changed: {layout.size}")
        expected = [v * 1254 / canvas[i % 2] for i, v in enumerate(patch["nativeGlobalBox"])]
        if any(abs(a - b) > 1e-7 for a, b in zip(expected, patch["overviewBox"])):
            raise ValueError("Overview box disagrees with exact global coordinate mapping")
        guide = layout.convert("RGB").transform((1254, 1254), Image.Transform.EXTENT,
                    patch["overviewBox"], Image.Resampling.BICUBIC)
    overlays = []
    warnings = []
    native_box = patch["nativeGlobalBox"]
    deltas = {"left": (-1024, 0), "right": (1024, 0), "top": (0, -1024), "bottom": (0, 1024)}
    # Deterministic corner ownership: later sides replace earlier sides.
    for side in ("left", "right", "top", "bottom"):
        value = getattr(args, side)
        if not value:
            continue
        path = Path(value).resolve()
        match = PATCH_RE.match(path.stem)
        if not match:
            raise ValueError(f"Neighbor filename has no patch identity: {path.name}")
        neighbor_zone = path.parent.parent if path.parent.name == "native" else ZONE
        cp, _, neighbor = coordinates(match.group(1), neighbor_zone)
        other_box = neighbor["nativeGlobalBox"]
        actual_delta = (other_box[0] - native_box[0], other_box[1] - native_box[1])
        if actual_delta != deltas[side]:
            raise ValueError(f"{side} neighbor is at {actual_delta}, expected {deltas[side]}")
        global_overlap = intersection(native_box, other_box)
        source_crop = local_box(global_overlap, other_box)
        target_box = local_box(global_overlap, native_box)
        with Image.open(path) as source:
            source.load()
            if source.size != (1254, 1254):
                raise ValueError(f"Neighbor native size {source.size} is not 1254 square: {path}")
            if source.mode not in ("RGB", "RGBA"):
                raise ValueError(f"Neighbor requires RGB/RGBA, got {source.mode}: {path}")
            if source.mode == "RGBA" and source.getchannel("A").getextrema() != (255, 255):
                raise ValueError("Transparent neighbors require a separately verified coverage plan")
            strip = source.convert("RGB").crop(source_crop)
        conflicts = []
        for earlier in overlays:
            common = intersection(target_box, earlier["targetLocalBox"])
            if common is not None:
                before = guide.crop(common)
                after = strip.crop(local_box(common, target_box))
                difference = ImageChops.difference(before, after)
                if difference.getbbox() is not None:
                    conflicts.append({"withSide": earlier["side"], "localBox": common,
                                      "meanAbsoluteChannelDifference": ImageStat.Stat(difference).mean})
        if conflicts:
            warnings.append({"type": "neighbor_corner_pixels_differ", "laterSide": side,
                             "conflicts": conflicts, "requiresGeometryReview": True,
                             "action": "No blend; later side owns corner. Inspect both full neighbors and repair with image_gen if geometry differs."})
        guide.paste(strip, (target_box[0], target_box[1]))
        item = file_ref(path, f"{side} adjacent native image; preserve exact global overlap geometry")
        item.update({"patchId": neighbor["id"], "side": side,
                     "nativeSize": [1254, 1254], "sourceNativeGlobalBox": other_box,
                     "globalOverlapBox": global_overlap, "sourceLocalBox": source_crop,
                     "targetLocalBox": target_box, "coordinateRecord": file_ref(cp, "neighbor coordinates"),
                     "operation": "1:1 crop and opaque paste; no resize, blend, feather or painting"})
        item.update(neighbor_provenance(path))
        if item["sourceType"] == "mechanical_derived":
            item["role"] = f"{side} adjacent candidate mechanically derived from native images; preserve exact global overlap geometry"
        elif item["sourceType"] == "unrecorded":
            warnings.append({"type": "neighbor_provenance_record_missing", "path": str(path)})
        overlays.append(item)
    identity = {"guideProvenanceVersion": 2, "patch": patch, "layoutSha256": references[0]["sha256"],
                "neighbors": [{"side": x["side"], "sha256": x["sha256"],
                               "provenance": x.get("derivedRecord") or x.get("generationRecord")} for x in overlays]}
    token = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]
    guide_path = ZONE / "guides" / f"{args.patch_id}.prepared-layout-only-{token}.png"
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    if guide_path.exists():
        with Image.open(guide_path) as existing:
            if existing.size != guide.size or existing.convert("RGB").tobytes() != guide.tobytes():
                raise ValueError(f"Immutable guide already exists with different pixels: {guide_path}")
    else:
        guide.save(guide_path)
    guide_ref = file_ref(guide_path, "exact crop/edit target; blurred layout-only center plus 1:1 native neighbor context; NOT final game art")
    config_path = ROOT / "config/image-generation.json"
    result = {"schemaVersion": 1, "preparedAtUtc": now(), "patchId": args.patch_id,
              "purpose": "layout-only generation guide; never final game pixels",
              "coordinateRecord": file_ref(coordinate_path, "authoritative patch coordinates"),
              "contract": file_ref(contract_path, "production contract"), "coordinates": patch,
              "guide": guide_ref, "guideNativeSize": [1254, 1254],
              "sourceChain": [references[0]] + overlays,
              "operations": ["Pillow EXTENT bicubic of overviewBox to 1254 square, layout-only",
                             "Native neighbor intersections cropped/pasted 1:1; no feathering"],
              "pasteOrder": [x["side"] for x in overlays], "warnings": warnings,
              "references": [guide_ref] + references + [file_ref(x["path"], x["role"]) for x in overlays],
              "referenceSubmissionStatus": "planned; pass every listed reference to image_gen and preserve actual call arguments in receipt",
              "configSnapshot": read_json(config_path), "configSource": file_ref(config_path, "target settings only"),
              "finalResizeAllowed": False, "formalAccepted": False}
    immutable = guide_path.with_name(guide_path.name + ".references.json")
    if not immutable.exists():
        write_json(immutable, result)
    else:
        result = read_json(immutable)
    result["preparedManifest"] = file_ref(immutable, "immutable guide provenance")
    write_json(ZONE / "records" / f"{args.patch_id}.prepared-references.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def copy_unchanged(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if not target.is_relative_to(ZONE):
        raise ValueError("Output must stay inside this zone")
    if target.exists():
        if sha(source) != sha(target):
            raise ValueError(f"Existing output differs; use a new --version: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if sha(source) != sha(target):
        raise OSError(f"Copy hash verification failed: {target}")


def receipt_text(path):
    value = Path(path).read_text(encoding="utf-8-sig")
    if re.search(r"data:[^\s;]+;base64,|[A-Za-z0-9+/]{4096,}={0,2}", value):
        raise ValueError("Receipt contains encoded binary data; retain metadata only, never base64")
    try:
        return value, json.loads(value)
    except json.JSONDecodeError:
        return value, None


def reference_evidence(patch_id, document, receipt):
    plan_path = ZONE / "records" / f"{patch_id}.prepared-references.json"
    plan = read_json(plan_path) if plan_path.is_file() else None
    roles = {str(Path(r["path"]).resolve()): r for r in document["references"]}
    if plan:
        roles.update({str(Path(r["path"]).resolve()): r for r in plan["references"]})
    submitted = None
    if isinstance(receipt, dict):
        for key in ("request", "submittedArguments", "arguments"):
            request = receipt.get(key)
            if isinstance(request, dict) and isinstance(request.get("referenced_image_paths"), list):
                submitted = request["referenced_image_paths"]
                break
    if submitted is None:
        if plan is None:
            raise ValueError("Need receipt request.referenced_image_paths or a prepared references manifest")
        submitted = [r["path"] for r in plan["references"]]
        verified = False
    else:
        verified = True
    if not submitted:
        raise ValueError("Reference list is empty; required actual reference evidence is missing")
    refs = []
    for value in submitted:
        path = Path(value)
        if not path.is_absolute():
            path = ZONE / path
        path = path.resolve()
        known = roles.get(str(path))
        role = known["role"] if known else "submitted reference; role not recorded in preparation manifest"
        if ".layout-only" in path.name or ".prepared-layout-only" in path.name:
            role = "exact coordinate crop/edit target; layout-only guide, NOT game art"
        ref = file_ref(path, role)
        if known and ref["sha256"] != known["sha256"]:
            raise ValueError(f"Reference changed since coordinate/preparation record: {path}")
        for suffix in (".derived.json", ".references.json", ".generation.json"):
            metadata = path.with_name(path.name + suffix)
            if metadata.is_file():
                ref.setdefault("provenanceRecords", []).append(file_ref(metadata, "reference source-chain evidence"))
        refs.append(ref)
    required = {str(Path(r["path"]).resolve()) for r in document["references"]}
    missing = required - {r["path"] for r in refs}
    if missing:
        raise ValueError("Receipt/reference plan omits mandatory references: " + ", ".join(sorted(missing)))
    matched_plan = plan if plan and plan["guide"]["path"] in {r["path"] for r in refs} else None
    return refs, verified, matched_plan


def generation_census():
    """Count independent image_gen results from retained records, never PNG files."""
    results = {}
    excluded_derived = [str(p) for p in sorted((ZONE / "native").glob("*.derived.json"))]
    for record_path in sorted((ZONE / "native").glob("*.generation.json")):
        record = read_json(record_path)
        image_path = Path(record["file"])
        if not image_path.is_absolute():
            image_path = ZONE / image_path
        image_path = image_path.resolve()
        if image_path.with_name(image_path.name + ".derived.json").is_file():
            continue
        if record.get("tool") not in ("image_gen.imagegen", "image_gen__imagegen") or record.get("route") != "builtin":
            continue
        image_hash = record.get("sha256")
        if not isinstance(image_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", image_hash):
            raise ValueError(f"Generation record lacks image hash: {record_path}")
        if image_path.is_file() and sha(image_path) != image_hash:
            raise ValueError(f"Native bytes changed under a generation record: {image_path}")
        receipt_ref = record.get("receipt") or record.get("evidence", {}).get("receipt")
        receipt_value = receipt_ref.get("path") if isinstance(receipt_ref, dict) else receipt_ref
        if not receipt_value:
            raise ValueError(f"Generation record lacks tool receipt: {record_path}")
        receipt_path = Path(receipt_value)
        if not receipt_path.is_absolute():
            receipt_path = ZONE / receipt_path
        receipt_path = receipt_path.resolve()
        receipt_hash = sha(receipt_path)
        if isinstance(receipt_ref, dict) and receipt_ref.get("sha256") and receipt_ref["sha256"] != receipt_hash:
            raise ValueError(f"Tool receipt hash changed: {receipt_path}")
        _, receipt = receipt_text(receipt_path)
        if not isinstance(receipt, dict) or receipt.get("tool") not in ("image_gen.imagegen", "image_gen__imagegen"):
            raise ValueError(f"Not an image_gen receipt: {receipt_path}")
        # Some built-in receipts store the observed return fields at the top
        # level. Normalize in memory; never rewrite the original tool receipt.
        response = receipt.get("response") or {
            "keys": receipt.get("returnedKeys", []),
            "output_hint": receipt.get("output_hint", ""),
        }
        if receipt.get("error") or receipt.get("isError") or not isinstance(response, dict) or response.get("error"):
            continue
        if "image_url" not in response.get("keys", []) and not response.get("output_hint") and not response.get("image_url"):
            raise ValueError(f"Receipt does not establish a returned image: {receipt_path}")
        # A copied record/receipt for the same returned image counts once. Separate
        # successful calls stay distinct, including retries with identical pixels.
        output_ids = sorted(set(re.findall(r"exec-[0-9a-fA-F-]{36}", response.get("output_hint", ""))))
        call_identity = "|".join(output_ids) or str(response.get("id") or receipt.get("toolCallId") or receipt_hash)
        identity = hashlib.sha256((call_identity + ":" + image_hash.lower()).encode()).hexdigest()
        entry = results.setdefault(identity, {"imageSha256": image_hash, "image": str(image_path),
                    "receipt": file_ref(receipt_path, "successful image_gen native output receipt"),
                    "generationRecords": []})
        entry["generationRecords"].append(str(record_path))
    return {"schemaVersion": 2, "generatedCount": len(results), "successfulGenerations": results,
            "excludedDerivedRecords": excluded_derived,
            "meaning": "Independent successful image_gen results proven by generation records and receipts; mechanical derived images excluded; retained records keep counts valid after source cleanup"}


def update_ingest_progress(patch_id, record_path, dimension_error):
    progress_path = ZONE / "progress.json"
    progress = read_json(progress_path) if progress_path.is_file() else {"zone": ZONE.name}
    counter = generation_census()
    total = counter["generatedCount"]
    # Recompute from evidence, so an earlier PNG-based overcount is corrected.
    progress["mechanicalIngestCounter"] = counter
    progress["generatedNativeCount"] = total
    for key in ("usableNativeCount", "complete4kCount", "formalAcceptedCount"):
        progress.setdefault(key, 0)
    progress.update({"updatedAtUtc": now(), "currentTile": patch_id.split("_p")[0],
                     "currentPatch": patch_id.split("_")[-1],
                     "status": "native_size_mismatch" if dimension_error else "native_saved_pending_visual_review",
                     "nextStep": "Recompute coverage or request a correctly sized native image; no automatic resize." if dimension_error else "Inspect native geometry and all overlaps at 100%; usable/accepted counters require separate review.",
                     "lastIngestRecord": str(record_path)})
    if dimension_error:
        errors = progress.setdefault("errors", [])
        error = {"type": "native_size_mismatch", "patchId": patch_id,
                 "record": str(record_path), "message": dimension_error}
        if error not in errors:
            errors.append(error)
    write_json(progress_path, progress)
    return total


def ingest(args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.version):
        raise ValueError("--version must be a safe filename component such as v1")
    coordinate_path, document, patch = coordinates(args.patch_id)
    checked_references(document)
    source = Path(args.source_path).resolve()
    prompt_source = Path(args.prompt_path).resolve()
    receipt_source = Path(args.receipt_path).resolve()
    prompt_source.read_text(encoding="utf-8-sig")
    _, receipt = receipt_text(receipt_source)
    with Image.open(source) as native:
        native.load()
        width, height = native.size
        image_format = native.format
        metadata_keys = sorted(native.info)
    extension = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}.get(image_format)
    if extension is None:
        raise ValueError(f"Unsupported native format {image_format}; no conversion will be performed")
    identity = f"{args.patch_id}-{args.version}"
    destination = ZONE / "native" / (identity + extension)
    record_path = destination.with_name(destination.name + ".generation.json")
    prompt_path = ZONE / "records" / (identity + ".prompt.txt")
    receipt_path = ZONE / "records" / (identity + (".receipt.json" if isinstance(receipt, dict) else ".receipt.txt"))
    dimensions_ok = [width, height] == patch["expectedSize"]
    dimension_error = None if dimensions_ok else f"Measured native {width}x{height}; expected 1254x1254. Original bytes retained; no scaling or core crop is valid under the current plan."
    if record_path.is_file():
        record = read_json(record_path)
        if record["sha256"] != sha(source) or record["prompt"]["sha256"] != sha(prompt_source) or record["receipt"]["sha256"] != sha(receipt_source):
            raise ValueError("Existing generation record differs; use a new --version")
        if sha(destination) != record["sha256"]:
            raise ValueError("Recorded native image bytes changed")
    else:
        refs, verified, plan = reference_evidence(args.patch_id, document, receipt)
        config_path = ROOT / "config/image-generation.json"
        config = plan["configSnapshot"] if plan else read_json(config_path)
        capture = "prepare_before_generation" if plan else "ingest_only; prior configuration was not independently captured"
        receipt_time = receipt.get("observedAtUtc") if isinstance(receipt, dict) else None
        record = {"schemaVersion": 1, "file": str(destination), "sha256": sha(source),
                  "patchId": args.patch_id, "version": args.version,
                  "generatedAt": None, "observedAtUtc": receipt_time, "ingestedAtUtc": now(),
                  "timeEvidence": "Exact generation time not disclosed; observedAtUtc copied only from receipt when present",
                  "width": width, "height": height, "nativeSize": [width, height], "format": image_format,
                  "metadataKeys": metadata_keys, "coordinates": patch,
                  "coordinateRecord": file_ref(coordinate_path, "exact patch placement plan"),
                  "tool": "image_gen.imagegen", "route": "builtin", "configSnapshot": config,
                  "configSnapshotCaptureStage": capture,
                  "submittedParameters": {"model": None, "quality": None},
                  "submittedModel": None, "submittedQuality": None,
                  "actualModel": None, "actualQuality": None,
                  "unverifiedReason": "宿主管理，工具未开放 model/quality 选择器；未披露可核实的实际型号与质量",
                  "prompt": {"path": str(prompt_path), "sha256": sha(prompt_source)},
                  "receipt": {"path": str(receipt_path), "sha256": sha(receipt_source)},
                  "references": refs, "referenceSubmissionVerifiedFromReceipt": verified,
                  "evidence": {"receipt": str(receipt_path), "nativeMetadataKeys": metadata_keys,
                               "selectorsExposed": False, "configTargetsAreNotActualSelectors": True},
                  "source": {"path": str(source), "sha256": sha(source), "operation": "byte-for-byte copy only; no transformation"},
                  "dimensionValidation": {"expected": patch["expectedSize"], "actual": [width, height], "passed": dimensions_ok, "error": dimension_error},
                  "visualReview": "pending", "usable": False, "formalAccepted": False,
                  "status": "candidate_pending_review" if dimensions_ok else "native_size_mismatch",
                  "nativeResizePerformed": False}
        if plan:
            record["preparedGuideEvidence"] = plan
        # Validate destination collisions before writing any output.
        for src, dst in ((source, destination), (prompt_source, prompt_path), (receipt_source, receipt_path)):
            if dst.exists() and sha(src) != sha(dst):
                raise ValueError(f"Existing output differs; use a new --version: {dst}")
        copy_unchanged(source, destination)
        copy_unchanged(prompt_source, prompt_path)
        copy_unchanged(receipt_source, receipt_path)
        write_json(record_path, record)
    count = update_ingest_progress(args.patch_id, record_path, dimension_error)
    print(json.dumps({"native": str(destination), "record": str(record_path), "sha256": record["sha256"],
                      "nativeSize": [width, height], "dimensionsValid": dimensions_ok,
                      "generatedNativeCount": count, "usableDefault": False,
                      "error": dimension_error}, ensure_ascii=False, indent=2))
    if dimension_error:
        raise SystemExit(2)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="Create a coordinate guide; never final art")
    prep.add_argument("patch_id", metavar="PATCHID")
    for side in ("left", "right", "top", "bottom"):
        prep.add_argument("--" + side, metavar="NEIGHBOR.png")
    prep.set_defaults(func=prepare)
    incoming = commands.add_parser("ingest", help="Copy native bytes and record provenance; never approve or resize")
    incoming.add_argument("patch_id", metavar="PATCHID")
    incoming.add_argument("source_path", metavar="SOURCEPATH")
    incoming.add_argument("prompt_path", metavar="PROMPTPATH")
    incoming.add_argument("receipt_path", metavar="RECEIPTPATH")
    incoming.add_argument("--version", default="v1")
    incoming.set_defaults(func=ingest)
    return parser


if __name__ == "__main__":
    try:
        arguments = build_parser().parse_args()
        arguments.func(arguments)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
