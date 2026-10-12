"""Immutable native-pixel registration, assembly, and guides for city-tower-north.

No image generation, AI editing, Git, shared-progress writes, or native resizing.
Run `python -B native_batch.py --help` or `... selfcheck`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

TOOLS = Path(__file__).resolve().parent
BATCH = TOOLS.parent
WORKSPACE = BATCH.parents[3]
BUILTIN = BATCH.parent.parent
CONTRACT_FILE = BUILTIN / "main-city-game-20261009" / "production-contract.json"
SPLIT_FILE = WORKSPACE / "docs" / "MAP_PARALLEL_SPLIT_20261013.json"
CURRENT_INDEX = BUILTIN / "main-city-game-20261009" / "northeast" / "current-adopted-index-20261012.json"
TILES = ("r03_c13", "r03_c14", "r04_c13", "r04_c14")
CORE, HALO, NATIVE, FINAL, CANVAS = 1024, 115, 1254, 4096, 65536
CORE_CROP = [HALO, HALO, HALO + CORE, HALO + CORE]
PATCHES = tuple(f"p{r}{c}" for r in range(1, 5) for c in range(1, 5))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def unique_version(prefix):
    return f"{prefix}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}"


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pixel_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def resolve_input(value, base):
    require(isinstance(value, str) and bool(value), "Input path must be nonempty text")
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve()


def evidence(path):
    path = Path(path).resolve()
    require(path.is_file(), f"Missing input: {path}")
    return {"file": str(path), "sha256": sha(path)}


def verify_evidence(item):
    require(isinstance(item, dict), "Evidence must be an object")
    path = Path(item["file"]).resolve()
    require(evidence(path)["sha256"] == item["sha256"], f"Input hash changed: {path}")
    return path


def verify_contracts():
    contract, split = read_json(CONTRACT_FILE), read_json(SPLIT_FILE)
    plan = contract["nativePatchPlan"]
    require(contract["artCanvasPixels"] == [CANVAS, CANVAS], "Canvas contract changed")
    require(contract["formalTilePixels"] == [FINAL, FINAL], "Tile contract changed")
    require((plan["corePixels"], plan["haloPixels"], plan["expectedNativePixels"],
             plan["subrows"], plan["subcolumns"]) == (CORE, HALO, NATIVE, 4, 4),
            "Native coordinate contract changed")
    batch = next(item for item in split["batches"] if item["key"] == "city-tower-north")
    require(tuple(batch["tiles"]) == TILES, "Batch tile ownership changed")
    require((WORKSPACE / batch["outputDirectory"]).resolve() == BATCH,
            "Tool is outside its assigned batch directory")
    return contract, batch


def coords(tile, patch=None):
    require(tile in TILES, f"Tile outside this batch: {tile}")
    row, col = int(tile[1:3]), int(tile[5:7])
    ox, oy = (col - 1) * FINAL, (row - 1) * FINAL
    result = {"tile": tile, "canvasPixels": [CANVAS, CANVAS],
              "tileCoreWorldBox": [ox, oy, ox + FINAL, oy + FINAL],
              "tileContextWorldBox": [ox - HALO, oy - HALO, ox + FINAL + HALO, oy + FINAL + HALO]}
    if patch is not None:
        require(patch in PATCHES, "Patch must be p11 through p44")
        r, c = int(patch[1]), int(patch[2])
        x, y = ox + (c - 1) * CORE, oy + (r - 1) * CORE
        result.update({"patch": patch, "coreWorldBox": [x, y, x + CORE, y + CORE],
                       "contextWorldBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
                       "coreCrop": CORE_CROP, "nativePixels": [NATIVE, NATIVE]})
    return result


class Scope:
    """Only versioned batch outputs, or isolated selfcheck outputs, may be written."""
    def __init__(self, selfcheck_root=None):
        self.synthetic = selfcheck_root is not None
        if self.synthetic:
            self.root = Path(selfcheck_root).resolve()
            require(self.root.is_relative_to((TOOLS / "selfcheck").resolve()),
                    "Selfcheck output must stay in tools/selfcheck")
        else:
            self.root = (BATCH / "versions").resolve()
        require(self.root.is_relative_to(BATCH), "Output root escaped batch")

    def path(self, *parts):
        for part in parts:
            require(isinstance(part, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", part),
                    f"Unsafe output component: {part!r}")
            require(part.split(".")[0].upper() not in
                    {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                     *(f"LPT{i}" for i in range(1, 10))}, "Reserved Windows output name")
        result = self.root.joinpath(*parts).resolve()
        require(result.is_relative_to(self.root) and result.is_relative_to(BATCH),
                "Resolved output path escaped write scope")
        return result

    def checked(self, path):
        path = Path(path).resolve()
        require(path.is_relative_to(self.root) and path.is_relative_to(BATCH),
                "Write path outside version scope")
        require(not path.exists(), f"Refusing overwrite: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Resolve again after mkdir so a preexisting junction cannot redirect a write.
        require(path.resolve().is_relative_to(self.root), "Write parent redirected outside scope")
        return path

    def json(self, path, data):
        path = self.checked(path)
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        return evidence(path)

    def copy(self, source, target):
        target = self.checked(target)
        with Path(source).open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
        require(sha(source) == sha(target), "Copied source byte identity failed")
        return evidence(target)

    def png(self, path, image, kind, **metadata):
        path = self.checked(path)
        with path.open("xb") as stream:
            image.save(stream, format="PNG")
        with Image.open(path) as saved:
            saved.load()
            require(saved.size == image.size and saved.mode == image.mode and
                    saved.tobytes() == image.tobytes(), "Saved PNG pixels changed")
        return {**evidence(path), "kind": kind, "pixels": list(image.size),
                "pixelSha256": pixel_sha(image), **metadata}


def load_opaque(path, size=None):
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG", "Native/candidate must be PNG")
        require(image.mode in ("RGB", "RGBA"), "Native/candidate must be RGB/RGBA")
        require(size is None or image.size == size,
                f"Measured dimensions {image.size}; required {size}; resizing is forbidden")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), "Ground source contains transparent pixels")
        return image.convert("RGB")


def register(spec_file, scope, version=None):
    """Register a real tool return by byte-copy; never crop or resize it."""
    spec_file = Path(spec_file).resolve()
    spec = read_json(spec_file)
    tile, patch = spec["tile"], spec["patch"]
    coordinate = coords(tile, patch)
    source = resolve_input(spec["sourceOutputPath"], spec_file.parent)
    pixels = load_opaque(source, (NATIVE, NATIVE))  # Reject before creating any output.
    prompt = resolve_input(spec["prompt"], spec_file.parent)
    require(prompt.read_text(encoding="utf-8-sig").strip(), "Empty actual submitted prompt")
    receipt = resolve_input(spec["receipt"], spec_file.parent)
    require(isinstance(read_json(receipt), (dict, list)), "Receipt must be valid JSON")
    refs = []
    for ref in spec["references"]:
        require(isinstance(ref.get("role"), str) and ref["role"].strip(), "Reference role required")
        ref_path = resolve_input(ref["file"], spec_file.parent)
        refs.append({**evidence(ref_path), "role": ref["role"]})
    require(refs, "Actual attached references must be recorded")
    inputs = {"sourceOutput": evidence(source), "prompt": evidence(prompt),
              "receipt": evidence(receipt), "registrationSpec": evidence(spec_file)}
    if spec.get("request"):
        request = resolve_input(spec["request"], spec_file.parent)
        data = read_json(request)
        require(data["prompt"] == prompt.read_text(encoding="utf-8-sig"),
                "Saved prompt must exactly match submitted request prompt")
        require([resolve_input(p, request.parent) for p in data["referenced_image_paths"]] ==
                [Path(ref["file"]) for ref in refs], "Request/reference list differs")
        inputs["request"] = evidence(request)
    version = version or unique_version("native")
    output = scope.path(version, tile, "native", f"{patch}.png")
    record_path = Path(str(output) + ".generation.json")
    require(not output.exists() and not record_path.exists(), "Native or record already exists")
    saved = scope.copy(source, output)
    require(saved["sha256"] == inputs["sourceOutput"]["sha256"], "Source changed during registration")
    require(pixel_sha(load_opaque(output, (NATIVE, NATIVE))) == pixel_sha(pixels),
            "Copied native differs from inspected source pixels")
    record = {"schemaVersion": 1, "createdAtUtc": now(), "tile": tile, "patch": patch,
              "version": version, "file": str(output), "sha256": saved["sha256"],
              "nativeSize": [NATIVE, NATIVE], "format": "PNG", "opaque": True,
              "pixelSha256RGB": pixel_sha(pixels), "coordinates": coordinate,
              "sourceOutputPath": str(source), "inputs": inputs, "references": refs,
              "prompt": str(prompt), "receipt": str(receipt),
              "tool": "selfcheck-fixture" if scope.synthetic else "image_gen.imagegen",
              "route": "synthetic-selfcheck" if scope.synthetic else "existing-builtin",
              "actualModel": None, "actualQuality": None,
              "unverifiedReason": "Actual model/quality not returned; prompt/configuration is not model evidence.",
              "resized": False, "cropped": False, "sourceByteIdentity": True,
              "status": "synthetic-fixture-not-art" if scope.synthetic else "native-candidate-unreviewed",
              "formalAcceptedCount": 0, "sharedProgressModified": False,
              "registrationTool": evidence(Path(__file__))}
    scope.json(record_path, record)
    return {"file": str(output), "record": str(record_path), "sha256": saved["sha256"],
            "recordSha256": sha(record_path), "tile": tile, "patch": patch, "nativeSize": [NATIVE, NATIVE]}


def load_selection(selection_file, scope):
    selection_file = Path(selection_file).resolve()
    selection = read_json(selection_file)
    require(selection.get("schemaVersion") == 1, "Selection schemaVersion must be 1")
    require(isinstance(selection.get("selectionVersion"), str) and selection["selectionVersion"],
            "Immutable selectionVersion required")
    tile = selection["tile"]
    coords(tile)
    require(isinstance(selection["patches"], dict) and selection["patches"], "Selection is empty")
    sources, records = {}, {}
    for patch, item in sorted(selection["patches"].items()):
        coordinate = coords(tile, patch)
        record_file = resolve_input(item["record"], selection_file.parent)
        require(record_file.is_relative_to(scope.root), "Selected record outside this output scope")
        require(sha(record_file) == item["recordSha256"], "Selected generation record hash changed")
        record = read_json(record_file)
        native = Path(record["file"]).resolve()
        require(native.is_relative_to(scope.root) and native.parent.name == "native",
                "Native outside this batch version/native scope")
        require(native.parent.parent.name == tile, "Native belongs to another tile")
        require(record["coordinates"] == coordinate and record["tile"] == tile and record["patch"] == patch,
                "Native coordinate/identity mismatch")
        require(record["resized"] is False and record["cropped"] is False and
                record["sourceByteIdentity"] is True and record["nativeSize"] == [NATIVE, NATIVE],
                "Selected source is not an unmodified measured 1254 native")
        require(record["route"] == ("synthetic-selfcheck" if scope.synthetic else "existing-builtin"),
                "Synthetic/production provenance mismatch")
        require(sha(native) == record["sha256"] == item["sha256"], "Selected native hash changed")
        pixels = load_opaque(native, (NATIVE, NATIVE))
        require(pixel_sha(pixels) == record["pixelSha256RGB"], "Selected decoded pixels changed")
        for key, value in record["inputs"].items():
            # The preserved native is the exact original byte copy. A host's
            # transient returned-source path may disappear after registration.
            if key == "sourceOutput" and not Path(value["file"]).is_file():
                require(value["sha256"] == record["sha256"], "Retained native/source hash differs")
                continue
            verify_evidence(value)
        for value in record["references"]:
            verify_evidence(value)
        sources[patch], records[patch] = pixels, {
            **record, "generationRecord": evidence(record_file),
            "originalOutputStillPresent": Path(record["sourceOutputPath"]).is_file()}
    return selection, sources, records


def rectangle(patches):
    rows = [int(p[1]) for p in patches]
    cols = [int(p[2]) for p in patches]
    r0, r1, c0, c1 = min(rows), max(rows), min(cols), max(cols)
    required = {f"p{r}{c}" for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}
    require(set(patches) == required, "Partial assembly must be a filled rectangle; no holes or placeholders")
    return r0, r1, c0, c1


def preview(scope, path, image, label):
    small = image.copy()
    small.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    labeled = Image.new("RGB", (small.width, small.height + 40), "#fff2d2")
    labeled.paste(small, (0, 40))
    ImageDraw.Draw(labeled).text((8, 12), label, fill="black")
    return scope.png(path, labeled, "derivative-preview-only", resized=True,
                     label=label, sourcePixels=list(image.size), resampling="LANCZOS",
                     nativeArt=False)


def assemble(selection_file, scope, version=None):
    selection, sources, records = load_selection(selection_file, scope)
    r0, r1, c0, c1 = rectangle(sources)
    tile = selection["tile"]
    width, height = (c1 - c0 + 1) * CORE, (r1 - r0 + 1) * CORE
    complete = len(sources) == 16
    core_world = coords(tile, f"p{r0}{c0}")["coreWorldBox"][:2]
    x0, y0 = core_world
    context = Image.new("RGB", (width + 2 * HALO, height + 2 * HALO))
    # Disjoint integer partitions: core ownership inside; only boundary sources
    # contribute outside halos. No blending or overlapping source overwrite.
    covered = 0
    for patch, image in sorted(sources.items()):
        row, col = int(patch[1]), int(patch[2])
        box = (0 if col == c0 else HALO, 0 if row == r0 else HALO,
               NATIVE if col == c1 else HALO + CORE, NATIVE if row == r1 else HALO + CORE)
        fragment = image.crop(box)
        pos = ((col - c0) * CORE + box[0], (row - r0) * CORE + box[1])
        context.paste(fragment, pos)
        covered += fragment.width * fragment.height
    require(covered == context.width * context.height, "Context partition coverage failed")
    core = context.crop((HALO, HALO, HALO + width, HALO + height))
    for patch, image in sources.items():
        row, col = int(patch[1]), int(patch[2])
        box = ((col - c0) * CORE, (row - r0) * CORE,
               (col - c0 + 1) * CORE, (row - r0 + 1) * CORE)
        require(core.crop(box).tobytes() == image.crop(tuple(CORE_CROP)).tobytes(),
                "Native core pixel identity failed")
    version = version or unique_version("assembly")
    output = scope.path(version, tile, "assembly")
    require(not output.exists(), "Assembly version already exists")
    artifacts = []
    kind = "complete-4096-candidate-unreviewed" if complete else "rectangular-partial-native-cores"
    stem = "candidate" if complete else "partial"
    artifacts.append(scope.png(output / f"{tile}-{stem}.png", core, kind,
                               resized=False, cropped=True, worldBox=[x0, y0, x0 + width, y0 + height]))
    artifacts.append(scope.png(output / f"{tile}-{stem}-context.png", context, "native-context-unreviewed",
                               resized=False, cropped=True,
                               worldBox=[x0 - HALO, y0 - HALO, x0 + width + HALO, y0 + height + HALO]))
    seams = []
    for col in range(c0, c1):
        x = (col - c0 + 1) * CORE
        for row in range(r0, r1 + 1):
            y = (row - r0) * CORE
            pair = [f"p{row}{col}", f"p{row}{col + 1}"]
            box = [x - 192, y, x + 192, y + CORE]
            seams.append(scope.png(output / "seams-100pct" / f"vertical-{'-'.join(pair)}.png",
                                   core.crop(tuple(box)), "internal-seam-native-pixel-crop",
                                   resized=False, scale=1, crop=box, sourceIds=pair))
    for row in range(r0, r1):
        y = (row - r0 + 1) * CORE
        for col in range(c0, c1 + 1):
            x = (col - c0) * CORE
            pair = [f"p{row}{col}", f"p{row + 1}{col}"]
            box = [x, y - 192, x + CORE, y + 192]
            seams.append(scope.png(output / "seams-100pct" / f"horizontal-{'-'.join(pair)}.png",
                                   core.crop(tuple(box)), "internal-seam-native-pixel-crop",
                                   resized=False, scale=1, crop=box, sourceIds=pair))
    artifacts.append(preview(scope, output / f"{tile}-{stem}-DERIVATIVE-preview.png", core,
                             f"DERIVATIVE PREVIEW / {tile} / {len(sources)}/16 cores / UNREVIEWED"))
    scope.copy(selection_file, output / "selection.snapshot.json")
    manifest = {"schemaVersion": 1, "createdAtUtc": now(), "tile": tile, "version": version,
                "selectionVersion": selection["selectionVersion"], "selection": evidence(selection_file),
                "selectedNative": [{"patch": p, "file": records[p]["file"],
                                    "sha256": records[p]["sha256"],
                                    "generationRecord": records[p]["generationRecord"]} for p in sorted(records)],
                "coreWorldBox": [x0, y0, x0 + width, y0 + height],
                "contextWorldBox": [x0 - HALO, y0 - HALO, x0 + width + HALO, y0 + height + HALO],
                "corePixels": [width, height], "contextPixels": list(context.size),
                "selectedNativeCount": len(sources), "complete4kCandidateCount": int(complete),
                "status": kind, "formalAcceptedCount": 0, "sharedProgressModified": False,
                "operation": "integer core crops; disjoint outer-halo partitions; no resampling, blending, or fill",
                "artifacts": artifacts, "internalSeamSegments": seams,
                "visualQa": "all internal and external seams unreviewed",
                "syntheticSelfcheck": scope.synthetic, "assemblyTool": evidence(Path(__file__))}
    path = output / "assembly.json"
    scope.json(path, manifest)
    return {"assembly": str(path), "complete4kCandidateCount": int(complete),
            "corePixels": [width, height], "contextPixels": list(context.size),
            "seamSegments100pct": len(seams), "formalAcceptedCount": 0}


def intersection(first, second):
    box = [max(first[0], second[0]), max(first[1], second[1]),
           min(first[2], second[2]), min(first[3], second[3])]
    return box if box[0] < box[2] and box[1] < box[3] else None


def guide(tile, patch, selection_files, scope, version=None, include_south=False, layout=None):
    target = coords(tile, patch)["contextWorldBox"]
    contract, _ = verify_contracts()
    layout = Path(layout or contract["layoutReference"]).resolve()
    layout_evidence = evidence(layout)
    require(layout_evidence["sha256"] == contract["layoutSha256"],
            "Layout must match the approved contract hash, including relocated copies")
    with Image.open(layout) as macro:
        macro.load()
        macro = macro.convert("RGB")
        source_box = [target[0] * macro.width / CANVAS, target[1] * macro.height / CANVAS,
                      target[2] * macro.width / CANVAS, target[3] * macro.height / CANVAS]
        base = macro.transform((NATIVE, NATIVE), Image.Transform.EXTENT,
                               tuple(source_box), Image.Resampling.BICUBIC)
        macro_size = list(macro.size)
    contributions = []
    selection_evidence = []
    for selection_file in selection_files:
        selection, sources, records = load_selection(selection_file, scope)
        selection_evidence.append(evidence(selection_file))
        for source_patch, image in sources.items():
            if (selection["tile"], source_patch) == (tile, patch):
                continue
            record = records[source_patch]
            # Native cores are authoritative. Discard conflicting outer halos;
            # exact 115-pixel border cores remain at their recorded world position.
            contributions.append({"image": image, "worldBox": record["coordinates"]["coreWorldBox"],
                                  "pixelOrigin": [HALO, HALO], "file": record["file"],
                                  "sha256": record["sha256"], "role": "locked-selected-native-core",
                                  "tile": selection["tile"], "patch": source_patch})
    current_evidence = None
    if include_south:
        current_evidence = evidence(CURRENT_INDEX)
        entries = read_json(CURRENT_INDEX)["candidates"]
        for south in ("r05_c13", "r05_c14"):
            item = next(entry for entry in entries if entry["tile"] == south)
            path = Path(item["file"]).resolve()
            require(sha(path) == item["sha256"], "Current south candidate changed")
            image = load_opaque(path, (FINAL, FINAL))
            col = int(south[5:7])
            x, y = (col - 1) * FINAL, 4 * FINAL
            contributions.append({"image": image, "worldBox": [x, y, x + FINAL, y + FINAL],
                                  "pixelOrigin": [0, 0], **evidence(path), "tile": south,
                                  "role": "locked-current-south-candidate-core"})
    locks, placed = [], []
    for contribution in sorted(contributions, key=lambda item: (item["tile"], item.get("patch", ""))):
        box = intersection(target, contribution["worldBox"])
        if box is None:
            continue
        require(not any(intersection(box, prior) for prior in placed),
                "Guide lock regions overlap; choose only one authoritative source per world core")
        wx, wy = contribution["worldBox"][:2]
        px, py = contribution["pixelOrigin"]
        crop = [box[0] - wx + px, box[1] - wy + py, box[2] - wx + px, box[3] - wy + py]
        paste = [box[0] - target[0], box[1] - target[1]]
        fragment = contribution["image"].crop(tuple(crop))
        base.paste(fragment, tuple(paste))
        locks.append({key: value for key, value in contribution.items() if key not in ("image", "pixelOrigin")})
        locks[-1].update({"lockedWorldBox": box, "sourceCrop": crop, "paste": paste,
                          "pixels": list(fragment.size), "pixelSha256RGB": pixel_sha(fragment), "resized": False})
        placed.append(box)
    for lock in locks:
        x, y = lock["paste"]
        w, h = lock["pixels"]
        require(pixel_sha(base.crop((x, y, x + w, y + h))) == lock["pixelSha256RGB"],
                "Guide modified a locked native core border")
    version = version or unique_version("guide")
    output = scope.path(version, tile, "guides")
    require(not output.exists(), "Guide version already exists")
    artifact = scope.png(output / f"{patch}-GUIDE-only.png", base, "mixed-continuity-guide-not-native-art",
                         nativeArt=False, newGeneration=False, worldBox=target,
                         resampling="BICUBIC for layout only; none for locked sources")
    record = {"schemaVersion": 1, "createdAtUtc": now(), "tile": tile, "patch": patch,
              "assetRole": "GUIDE ONLY; enlarged macro plus exact known native core border pixels; never new art",
              "artifact": artifact, "contextWorldBox": target,
              "macro": {**layout_evidence, "nativePixels": macro_size, "sourceBox": source_box,
                        "resampling": "BICUBIC", "enlargedLayoutOnly": True},
              "selectedInputs": selection_evidence, "currentSouthIndex": current_evidence,
              "lockedSources": locks,
              "nativeLockPolicy": "authoritative core intersections only; outer native halos excluded to avoid conflicts",
              "lockedPixelsIdentityVerified": True, "newImageGeneration": False,
              "actualModel": None, "sharedProgressModified": False}
    path = output / f"{patch}-GUIDE-only.json"
    scope.json(path, record)
    return {"guide": artifact["file"], "metadata": str(path), "lockedSourceCount": len(locks)}


def selfcheck():
    """Deterministic synthetic diagnostics; all writes remain in tools/selfcheck."""
    verify_contracts()
    scope = Scope(TOOLS / "selfcheck" / unique_version("run"))
    fixture = scope.path("fixtures", "source.png")
    # Coordinate-colored fixture makes off-by-one/crop errors detectable.
    image = Image.new("RGB", (NATIVE, NATIVE))
    image.putdata([((x * 13) % 256, (y * 17) % 256, (x + y) % 256)
                   for y in range(NATIVE) for x in range(NATIVE)])
    scope.png(fixture, image, "synthetic-test-fixture-not-art", resized=False)
    prompt = scope.checked(scope.path("fixtures", "prompt.txt"))
    prompt.write_text("SYNTHETIC SELF CHECK; NOT A GENERATION REQUEST", encoding="utf-8")
    receipt = scope.path("fixtures", "receipt.json")
    scope.json(receipt, {"synthetic": True, "actualModel": None})
    items = {}
    for patch in PATCHES:
        spec = scope.path("fixtures", f"{patch}-spec.json")
        scope.json(spec, {"tile": TILES[0], "patch": patch, "sourceOutputPath": str(fixture),
                          "prompt": str(prompt), "receipt": str(receipt),
                          "references": [{"file": str(fixture), "role": "synthetic test reference"}]})
        result = register(spec, scope, "fixture-native-v1")
        items[patch] = {key: result[key] for key in ("record", "sha256", "recordSha256")}
    complete = scope.path("selection-full-v1.json")
    scope.json(complete, {"schemaVersion": 1, "selectionVersion": "synthetic-full-v1",
                          "tile": TILES[0], "patches": items})
    full = assemble(complete, scope, "full-assembly-v1")
    require(full["corePixels"] == [4096, 4096] and full["contextPixels"] == [4326, 4326]
            and full["seamSegments100pct"] == 24, "Full assembly dimensions or seam count wrong")
    partial_file = scope.path("selection-partial-v1.json")
    scope.json(partial_file, {"schemaVersion": 1, "selectionVersion": "synthetic-partial-v1",
                              "tile": TILES[0], "patches": {p: items[p] for p in ("p21", "p22")}})
    partial = assemble(partial_file, scope, "partial-assembly-v1")
    require(partial["corePixels"] == [2048, 1024] and partial["contextPixels"] == [2278, 1254]
            and partial["seamSegments100pct"] == 1, "Partial assembly dimensions wrong")
    guide_result = guide(TILES[0], "p23", [partial_file], scope, "guide-v1")
    guide_record = read_json(guide_result["metadata"])
    require(guide_record["lockedPixelsIdentityVerified"] and guide_result["lockedSourceCount"] == 1,
            "Guide neighbor core lock missing")
    south_guide = guide("r04_c13", "p41", [], scope, "south-guide-v1", include_south=True)
    south_record = read_json(south_guide["metadata"])
    require(south_guide["lockedSourceCount"] == 1 and
            south_record["lockedSources"][0]["pixels"] == [1139, 115] and
            south_record["lockedPixelsIdentityVerified"], "South candidate border lock failed")
    rejections = []
    def rejected(name, call):
        try:
            call()
        except (ValueError, FileExistsError):
            rejections.append(name)
        else:
            raise AssertionError(f"Expected rejection: {name}")
    rejected("overwrite", lambda: assemble(complete, scope, "full-assembly-v1"))
    rejected("path traversal", lambda: scope.path("..", "escape.png"))
    rejected("wrong tile ownership", lambda: coords("r05_c13", "p11"))
    rejected("hole in partial rectangle", lambda: rectangle(["p11", "p22"]))
    bad_image = scope.path("fixtures", "bad-size.png")
    scope.png(bad_image, Image.new("RGB", (1255, 1254)), "bad-size-synthetic-fixture")
    bad_spec = scope.path("fixtures", "bad-size-spec.json")
    spec_data = read_json(scope.path("fixtures", "p11-spec.json"))
    spec_data["sourceOutputPath"] = str(bad_image)
    scope.json(bad_spec, spec_data)
    rejected("non1254 source", lambda: register(bad_spec, scope, "must-not-exist"))
    require(not scope.path("must-not-exist").exists(), "Rejected source created native output")
    report = {"passed": True, "scope": str(scope.root), "syntheticOnly": True,
              "complete": full, "partial": partial, "guide": guide_result, "southGuide": south_guide,
              "guardRejections": rejections, "newImageGeneration": False,
              "sharedProgressModified": False, "actualModel": None}
    scope.json(scope.path("selfcheck-report.json"), report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    coordinate = sub.add_parser("coords", help="Read-only exact world/context boxes")
    coordinate.add_argument("--tile", required=True, choices=TILES)
    coordinate.add_argument("--patch", choices=PATCHES)
    ingest = sub.add_parser("register", help="Copy a returned 1254 PNG into immutable version/native")
    ingest.add_argument("--spec", required=True)
    ingest.add_argument("--version")
    assembly = sub.add_parser("assemble", help="Assemble selected complete or filled rectangular native cores")
    assembly.add_argument("--selection", required=True)
    assembly.add_argument("--version")
    context = sub.add_parser("guide", help="Build GUIDE ONLY with exact known core boundary pixels")
    context.add_argument("--tile", required=True, choices=TILES)
    context.add_argument("--patch", required=True, choices=PATCHES)
    context.add_argument("--selection", action="append", default=[])
    context.add_argument("--include-south-current", action="store_true")
    context.add_argument("--layout")
    context.add_argument("--version")
    sub.add_parser("selfcheck", help="Write isolated synthetic diagnostics under tools/selfcheck only")
    args = parser.parse_args()
    verify_contracts()
    scope = Scope()
    if args.command == "coords":
        result = coords(args.tile, args.patch) if args.patch else {
            **coords(args.tile), "patches": [coords(args.tile, patch) for patch in PATCHES]}
    elif args.command == "register":
        result = register(args.spec, scope, args.version)
    elif args.command == "assemble":
        result = assemble(args.selection, scope, args.version)
    elif args.command == "guide":
        result = guide(args.tile, args.patch, args.selection, scope, args.version,
                       args.include_south_current, args.layout)
    else:
        result = selfcheck()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        print(f"Refused: {error}", file=sys.stderr)
        raise SystemExit(2)
