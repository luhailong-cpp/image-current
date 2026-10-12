"""Versioned, read-only artwork inventory; never changes progress or selections.

Reuses exact core-replay evidence only after rehashing the current selected
sources and candidate. New/changed candidates alone undergo pixel replay.
No recursive history scan, overview construction, image edits, or Git calls.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import io
import json

import numpy as np
from PIL import Image

Z = Path(__file__).resolve().parent
ROOT = Z.parents[3]
OWNER = "01a1216d-4a55-7063-ba13-5ddf6d9106f7"
PATCHES = [f"p{r}{c}" for r in range(1, 5) for c in range(1, 5)]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def signature(path):
    s = path.stat()
    return [s.st_size, s.st_mtime_ns]


def resolve(value, tile_dir):
    if isinstance(value, dict):
        value = value.get("file") or value.get("path")
    if not isinstance(value, str) or not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else tile_dir / p


def write_new(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def inspect_sources(tile_dir, selection):
    records, signatures, errors = [], {}, []
    patches = selection.get("patches", {})
    for key in sorted(patches):
        if key not in PATCHES:
            errors.append(f"Unexpected patch id: {key}")
            continue
        p = resolve(patches[key], tile_dir)
        if not p or not p.is_file():
            errors.append(f"Missing selected source: {key}: {p}")
            continue
        before = signature(p)
        data = p.read_bytes()
        after = signature(p)
        with Image.open(io.BytesIO(data)) as im:
            size = list(im.size)
        if before != after:
            errors.append(f"Source changed during hash read: {key}")
        if size != [1254, 1254]:
            errors.append(f"Source dimensions differ from 1254 square: {key}: {size}")
        records.append(dict(patch=key, file=str(p), sha256=digest(data), dimensions=size))
        signatures[str(p)] = after
    return records, signatures, errors


def candidate_check(tile_dir, selection, previous, source_records, previous_index):
    """Reuse by content, or replay changed cores against bounded candidates."""
    source_hashes = {x["patch"]: x["sha256"] for x in source_records}
    old_hashes = {x["patch"]: x["sha256"] for x in previous.get("sources", [])}
    candidates, seen, failures = [], set(), []
    for v in (selection.get("candidate"), previous.get("candidate")):
        p = resolve(v, tile_dir)
        if p:
            candidates.append(p)
    cores = None

    def check(p):
        nonlocal cores
        normalized = str(p).lower()
        if normalized in seen or not p.is_file():
            return None
        seen.add(normalized)
        before = signature(p)
        data = p.read_bytes()
        current_hash = digest(data)
        if signature(p) != before:
            failures.append(dict(candidate=str(p), reason="candidate changed while reading"))
            return None
        if (previous.get("coreReplayVerified") is True
                and source_hashes == old_hashes and len(source_hashes) == 16
                and current_hash == previous.get("candidateSha256")):
            return dict(candidate=str(p), candidateSha256=current_hash,
                        dimensions=[4096, 4096], coreReplayVerified=True,
                        verificationMethod="reused_prior_exact_replay_after_current_source_and_candidate_hash_match",
                        reusedEvidenceIndex=str(previous_index)), {str(p): before}
        with Image.open(io.BytesIO(data)) as im:
            if im.size != (4096, 4096):
                failures.append(dict(candidate=str(p), reason="not 4096 square"))
                return None
            pixels = np.asarray(im.convert("RGB"))
        if cores is None:
            cores = {}
            for item in source_records:
                with Image.open(item["file"]) as im:
                    cores[item["patch"]] = np.asarray(im.convert("RGB"))[115:1139, 115:1139].copy()
        for key, core in cores.items():
            r, c = int(key[1]) - 1, int(key[2]) - 1
            if not np.array_equal(pixels[r*1024:(r+1)*1024, c*1024:(c+1)*1024], core):
                failures.append(dict(candidate=str(p), reason=f"core mismatch: {key}"))
                return None
        return dict(candidate=str(p), candidateSha256=current_hash,
                    dimensions=[4096, 4096], coreReplayVerified=True,
                    verificationMethod="current_16_native_cores_exact_pixel_replay"), {str(p): before}

    for p in candidates:
        result = check(p)
        if result:
            return result[0], result[1], failures
    # Only the three most recently modified immediate QA directories are read.
    # Existing exact evidence above never triggers this bounded fallback.
    qa = tile_dir / "qa"
    qa_dirs = sorted((p for p in qa.iterdir() if p.is_dir()),
                     key=lambda p: p.stat().st_mtime_ns, reverse=True)[:3] if qa.is_dir() else []
    for directory in qa_dirs:
        manifest = directory / "manifest.json"
        options = []
        if manifest.is_file():
            m = read(manifest)
            if isinstance(m, dict):
                p = resolve(m.get("candidate"), tile_dir)
                if p:
                    options.append(p)
        options.append(directory / "candidate-4096.png")
        for p in options:
            result = check(p)
            if result:
                return result[0], result[1], failures
    return {}, {}, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--previous-index", type=Path, default=Z / "delivery-index-20261012.json")
    ap.add_argument("--output-index", type=Path, default=Z / "delivery-index-20261013.json")
    ap.add_argument("--checkpoint", type=Path, default=Z / "production-index-checkpoint-20261013-v1.json")
    args = ap.parse_args()
    if args.output_index.exists() or args.checkpoint.exists():
        raise SystemExit("Preserve prior records: pass new --output-index and --checkpoint paths.")
    started = datetime.now(timezone.utc).isoformat()
    split_path = ROOT / "docs/MAP_PARALLEL_SPLIT_20261013.json"
    split = read(split_path)
    batches = [b for b in split["batches"] if b.get("owner") == OWNER
               and b.get("status") == "allocated_root_reserved"]
    region = [f"r{r:02}_c{c:02}" for r in range(8, 15) for c in range(8, 15)]
    excluded = sorted({t for b in batches for t in b["tiles"] if t in region})
    owned = [t for t in region if t not in excluded]
    previous_document = read(args.previous_index)
    previous = {e["tile"]: e for e in previous_document["entries"]}
    entries, file_signatures, selection_snapshots = [], {}, {}
    for tile in owned:
        tile_dir = Z / tile
        sp = tile_dir / "selected-patches.json"
        entry = dict(tile=tile, selectedPositions=0, declaredSelectedPositions=0,
                     missing=PATCHES.copy(), internalReady=False, formalAccepted=False,
                     status="not_generated", selectionStableDuringObservation=True)
        if not sp.is_file():
            entries.append(entry)
            selection_snapshots[str(sp)] = None
            continue
        data = sp.read_bytes()
        sel_hash = digest(data)
        selection = json.loads(data.decode("utf-8-sig"))
        selection_snapshots[str(sp)] = sel_hash
        records, signatures, errors = inspect_sources(tile_dir, selection)
        file_signatures.update(signatures)
        valid = [x for x in records if x["dimensions"] == [1254, 1254]]
        n = len(valid)
        entry.update(selection=str(sp), selectionSha256=sel_hash,
                     selectedPositions=n, declaredSelectedPositions=len(selection.get("patches", {})),
                     missing=[p for p in PATCHES if p not in {x["patch"] for x in valid}],
                     sources=records, sourceValidationErrors=errors,
                     canonicalStatus=selection.get("status"),
                     canonicalInternalReady=bool(selection.get("internalReady")),
                     canonicalFormalAccepted=bool(selection.get("formalAccepted")),
                     status="partial_native_selection" if n < 16 else "full_native_selection_candidate_pending")
        if n == 16 and not errors:
            candidate, candidate_signatures, failures = candidate_check(
                tile_dir, selection, previous.get(tile, {}), records, args.previous_index)
            entry.update(candidate)
            file_signatures.update(candidate_signatures)
            if failures:
                entry["candidateChecksNotAccepted"] = failures
            if candidate:
                entry["internalReady"] = bool(selection.get("internalReady"))
                entry["formalAccepted"] = bool(selection.get("formalAccepted"))
                entry["status"] = ("formally_accepted" if entry["formalAccepted"] else
                                   "internal_passed_external_pending" if entry["internalReady"] else
                                   "full_candidate_internal_QA_or_repairs_pending")
        for key in ("internalReview", "ownerReview", "availableExternalReview", "externalReview",
                    "materialPending", "externalMaterialPending", "geometryBlockingIssues"):
            if key in selection:
                entry[key] = selection[key]
        # Canonical review flags are owner records, not newly asserted visual QA.
        entry["reviewStatusBasis"] = "current canonical owner selection; no new visual approval by indexer"
        entries.append(entry)
    changed_files = [name for name, sig in file_signatures.items()
                     if not Path(name).is_file() or signature(Path(name)) != sig]
    unstable = []
    for e in entries:
        sp = Z / e["tile"] / "selected-patches.json"
        prior = selection_snapshots[str(sp)]
        after = sha(sp) if sp.is_file() else None
        affected = any(x["file"] in changed_files for x in e.get("sources", []))
        affected = affected or e.get("candidate") in changed_files or prior != after
        if affected:
            unstable.append(e["tile"])
            e.update(selectionStableDuringObservation=False, internalReady=False, formalAccepted=False,
                     status="changed_during_observation_recheck_required")
    stable = [e for e in entries if e["selectionStableDuringObservation"]]
    completed = datetime.now(timezone.utc).isoformat()
    rule = ROOT / "AGENTS.md"
    d = dict(schemaVersion=2, startedAtUtc=started, completedAtUtc=completed,
             ownerThreadId=OWNER, scope="southeast rows 8..14 cols 8..14 excluding current reserved transfers",
             originalRegionTileCount=49, originalRegionNativeCoreTarget=784,
             ownedTargetTileCount=len(owned), ownedNativeCoreTarget=16*len(owned),
             transferredTileCount=len(excluded), transferredTiles=excluded,
             transferredNativeCoreTarget=16*len(excluded), transferredProductionNotCountedHere=True,
             transfers=batches, splitManifest=str(split_path), splitManifestSha256=sha(split_path),
             fullCoverageCandidateCount=sum(bool(e.get("candidate")) for e in stable),
             fullyDrawn16PatchTileCount=sum(e["selectedPositions"] == 16 for e in stable),
             internalPassedCount=sum(e["internalReady"] for e in stable),
             formalAcceptedCount=sum(e["formalAccepted"] for e in stable),
             selectedNativePositions=sum(e["selectedPositions"] for e in stable),
             partialSelections=[dict(tile=e["tile"], selectedPositions=e["selectedPositions"], missing=e["missing"])
                                for e in stable if 0 < e["selectedPositions"] < 16],
             reusedExactReplayCount=sum(e.get("verificationMethod", "").startswith("reused_") for e in stable),
             newlyReplayedCandidateCount=sum(e.get("verificationMethod") == "current_16_native_cores_exact_pixel_replay" for e in stable),
             unstableTiles=unstable, changedFilesDuringObservation=changed_files,
             snapshotAtomic=False, snapshotConsistency="independent tile reads; manifest hashes rechecked and source/candidate file signatures stable at observation end",
             aggregateCountBasis="stable tiles only; lower bound if unstableTiles is nonempty",
             entries=entries, priorIndex=str(args.previous_index), priorIndexSha256=sha(args.previous_index),
             generatedNativeCount=None, generatedCountNote="Not rescanned recursively; counts here describe current selected positions, not historical generations or requests.",
             newArtworkGenerationAllowed=True, preferredImageModel="GPT Image 2.5", fallbackImageModel="GPT Image 2.0",
             actualImageModel=None, actualQuality=None, paidApiAllowed=False,
             modelEvidence="Current project policy allows existing built-in fallback; this local inventory invokes no generation and does not claim a returned model.",
             rootInstructions=str(rule), rootInstructionsSha256=sha(rule),
             writesProgressJson=False, modifiesSelections=False, modifiesImages=False, gitOperations=False)
    d["missingSelectedPositions"] = d["ownedNativeCoreTarget"] - d["selectedNativePositions"]
    d["remainingIncompleteTiles"] = len(owned) - d["fullCoverageCandidateCount"]
    d["fullyDrawnButInternalReviewPendingCount"] = sum(e["selectedPositions"] == 16 and not e["internalReady"] for e in stable)
    d["allOwnedTilesFormallyAccepted"] = d["formalAcceptedCount"] == len(owned) and not unstable
    write_new(args.output_index, d)
    checkpoint = {k: d[k] for k in (
        "startedAtUtc", "completedAtUtc", "originalRegionTileCount", "ownedTargetTileCount",
        "transferredTileCount", "transferredTiles", "fullCoverageCandidateCount", "fullyDrawn16PatchTileCount",
        "internalPassedCount", "formalAcceptedCount", "selectedNativePositions", "missingSelectedPositions",
        "partialSelections", "reusedExactReplayCount", "newlyReplayedCandidateCount", "unstableTiles",
        "snapshotAtomic", "snapshotConsistency", "aggregateCountBasis")}
    checkpoint.update(deliveryIndex=str(args.output_index), deliveryIndexSha256=sha(args.output_index),
                      status="local_index_snapshot_completed_production_continues", progressJsonUpdated=False,
                      sourceSelectionOrImageChanges=False, gitOperations=False)
    write_new(args.checkpoint, checkpoint)
    print(json.dumps(checkpoint, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
