#!/usr/bin/env python3
"""Copy one returned PNG and record its origin; never select it or pass QA.

--dry-run reads the request, plan and real source only. It creates no files.
Production uses copy2, refuses existing targets, and retains the original PNG.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def inside(value):
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    require(p.is_relative_to(ROOT), f"Path escapes this batch: {p}")
    return p


def read(path):
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), hashlib.sha256(raw).hexdigest()


def inspect_source(path):
    with Image.open(path) as im:
        im.load()
        require(im.format == "PNG", f"Source is not PNG: {path}")
        require(im.mode in ("RGB", "RGBA"), f"Unsupported map PNG mode: {im.mode}")
        opaque = im.mode == "RGB" or im.getextrema()[3] == (255, 255)
        return {"width": im.width, "height": im.height, "mode": im.mode,
                "format": im.format, "opaque": opaque}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="Existing saved request JSON inside this batch")
    parser.add_argument("--source", required=True, help="Absolute path of the returned built-in PNG")
    parser.add_argument("--plan", default="production-plan-v1.json")
    parser.add_argument("--dry-run", action="store_true", help="Read-only validation; no copy or sidecar write")
    args = parser.parse_args(argv)
    rp, pp = inside(args.request), inside(args.plan)
    request, request_hash = read(rp)
    plan, plan_hash = read(pp)
    require(plan.get("batch") == "village-west-courtyard", "Wrong production batch")
    require(plan.get("allocation", {}).get("status") == "allocated_root_reserved", "Wrong allocation status")
    require(request.get("tool") in ("image_gen.imagegen", "image_gen__imagegen"), "Request is not for the built-in image tool")
    patch, version = request.get("patch", ""), request.get("version", "")
    require(isinstance(patch, str) and re.fullmatch(r"r\d{2}_c\d{2}_p\d{2}_\d{2}", patch), "Invalid request.patch")
    require(isinstance(version, str) and re.fullmatch(r"v\d+", version), "Invalid request.version")
    matches = [p for p in plan.get("nativePatches", []) if f"{p['tile']}_{p['patch']}" == patch]
    require(len(matches) == 1, "Request patch must match exactly one planned slot")
    planned = matches[0]
    for field in ("globalCoreBox", "globalNativeBox"):
        require(isinstance(planned.get(field), list) and len(planned[field]) == 4, f"Invalid planned {field}")
        if request.get(field) is not None:
            require(request[field] == planned[field], f"Request disagrees with plan: {field}")
        if request.get("coordinates", {}).get(field) is not None:
            require(request["coordinates"][field] == planned[field], f"Request coordinates disagree with plan: {field}")
    source = Path(args.source)
    require(source.is_absolute(), "--source must be an absolute returned-PNG path")
    source = source.resolve(strict=True)
    info = inspect_source(source)
    expected = planned.get("expectedNativeDimensions", plan.get("expectedNativeDimensions"))
    require([info["width"], info["height"]] == expected == [1254, 1254],
            f"Measured size differs from native plan: {[info['width'], info['height']]}; expected {expected}")
    require(info["opaque"], "Map source contains transparent pixels")
    for field in ("requestedNativeDimensions", "expectedNativeDimensions"):
        if request.get(field) is not None:
            require(request[field] == [info["width"], info["height"]], f"Request {field} differs from measured PNG")
    source_hash = digest(source)
    output = ROOT / "native" / f"{patch}_{version}.png"
    sidecar = Path(str(output) + ".generation.json")
    require(source != output, "Source must be the original returned PNG, not the destination")
    arguments = request.get("submittedArguments", {})
    record = {"schemaVersion": 1, "file": str(output), "sha256": source_hash,
              "recordedAtUtc": datetime.now(timezone.utc).isoformat(), "generatedAt": None,
              "tile": planned["tile"], "patch": planned["patch"], "requestPatch": patch, "version": version,
              **info, "globalCoreBox": planned["globalCoreBox"], "globalNativeBox": planned["globalNativeBox"],
              "nativeCoreCropBox": planned.get("coreInNative", [115, 115, 1139, 1139]),
              "tool": "image_gen.imagegen", "route": "builtin", "actualModel": None, "actualQuality": None,
              "unverifiedReason": "Actual model/quality metadata was not supplied to this recorder; not inferred from settings.",
              "nativeScaleResampled": False, "operation": "shutil.copy2; unchanged PNG bytes; original retained",
              "toolOriginal": {"file": str(source), "sha256": source_hash},
              "request": {"file": str(rp), "sha256": request_hash},
              "plan": {"file": str(pp), "sha256": plan_hash},
              "evidence": {"request": str(rp), "requestSha256": request_hash,
                           "returnedSourcePath": str(source), "returnedSourceSha256": source_hash,
                           "receipt": None, "receiptStatus": "not supplied; recorder does not fabricate tool receipt"},
              "submittedParameters": request.get("submittedParameters", {"model": arguments.get("model"),
                                      "quality": arguments.get("quality"),
                                      "transparent_background": arguments.get("transparent_background")}),
              "promptText": arguments.get("prompt"), "references": request.get("references", []),
              "status": "candidate-pending-QA", "selected": False, "internalAccepted": False, "formalAccepted": False,
              "qa": {k: "pending" for k in ("layout", "adjacentEdges", "internalSeams", "externalSeams", "formalAcceptance")}}
    summary = {"valid": True, "dryRun": args.dry_run, "source": str(source), "sourceSha256": source_hash,
               "destination": str(output), "generationRecord": str(sidecar), "measured": info,
               "globalCoreBox": planned["globalCoreBox"], "globalNativeBox": planned["globalNativeBox"],
               "wouldRefuseOverwrite": output.exists() or sidecar.exists(), "selected": False, "qa": record["qa"]}
    if args.dry_run:
        summary.update(writes=0, copied=False)
        print(json.dumps(summary))
        return 0
    require(not output.exists() and not sidecar.exists(), "Destination or generation sidecar already exists; refusing overwrite")
    require(digest(rp) == request_hash and digest(pp) == plan_hash, "Request or plan changed during validation")
    output.parent.mkdir(parents=True, exist_ok=True)
    require(not output.exists() and not sidecar.exists(), "Destination appeared; refusing overwrite")
    shutil.copy2(source, output)
    require(digest(output) == digest(source) == source_hash, "Original/copy SHA256 differs; retained for investigation, sidecar not written")
    require(inspect_source(output) == info, "Copy PNG dimensions/mode differ; retained for investigation")
    with sidecar.open("x", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
        f.write("\n")
    summary.update(writes=2, copied=True, copySha256=digest(output), generationRecordSha256=digest(sidecar))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "status": "recording-refused"}), file=sys.stderr)
        raise SystemExit(2)
