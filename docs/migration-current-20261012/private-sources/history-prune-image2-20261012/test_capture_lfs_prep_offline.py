"""Small local Git fixtures only. Never inspect or capture the live artwork tree."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import types
import uuid

WORK = Path(__file__).resolve().parent
SCRIPT = WORK / "capture_frozen_delta_lfs_prep.py"
SCRIPT_SHA = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
module = types.ModuleType("offline_capture")
module.__file__ = str(SCRIPT)
exec(compile(SCRIPT.read_bytes(), str(SCRIPT), "exec"), module.__dict__)
FIXTURES = WORK / ("cp-" + uuid.uuid4().hex[:8])  # Keep fixture paths below Windows MAX_PATH.
FIXTURES.mkdir()
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
GIT = module.GIT
results = []


def git(root, *args, data=None, allowed=(0,)):
    result = subprocess.run([GIT, "-c", "user.name=Offline Test", "-c", "user.email=offline@example.invalid",
        "-c", "core.hooksPath=" + str(FIXTURES / "no-hooks"), "-C", str(root), *args],
        env=ENV, input=data, capture_output=True)
    assert result.returncode in allowed, result.stderr.decode(errors="replace")
    return result.stdout


def fixture(label, nested=False):
    root = FIXTURES / label
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "core.autocrlf", "false")
    old_data = b"old LFS image contents\x00" * 10
    old_sha = hashlib.sha256(old_data).hexdigest()
    pointer = module.LFS_HEADER + ("oid sha256:" + old_sha + "\nsize " + str(len(old_data)) + "\n").encode()
    files = {"keep.txt": b"unchanged\n", "edit.txt": b"before\n", "protected.png": b"protected bytes\x00\xff",
             ".gitattributes": b"old.bin filter=lfs diff=lfs merge=lfs -text\n",
             ".gitignore": b"ignored.dat\ncache.tmp\n", "old.bin": pointer}
    if nested:
        files["sub/.gitattributes"] = b"*.bin -filter\n"
    payload = []
    for path, data in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        oid = git(root, "hash-object", "-w", "--stdin", "--no-filters", data=data).decode().strip()
        payload.append(("100644 " + oid + "\t" + path).encode() + b"\0")
    git(root, "update-index", "--add", "-z", "--index-info", data=b"".join(payload))
    tree = git(root, "write-tree").decode().strip()
    commit = git(root, "commit-tree", tree, "-m", "Offline baseline").decode().strip()
    git(root, "update-ref", "refs/heads/main", commit)
    (root / "old.bin").write_bytes(old_data)
    cache = root / ".git/lfs/objects" / old_sha[:2] / old_sha[2:4] / old_sha
    cache.parent.mkdir(parents=True)
    cache.write_bytes(old_data)
    (root / "edit.txt").write_bytes(b"after\n")
    large = "sub/new art.bin" if nested else "new art.bin"
    (root / large).parent.mkdir(exist_ok=True)
    (root / large).write_bytes(b"large-new-image\x00" * 300)
    (root / "ignored.dat").write_bytes(b"required ignored artwork")
    (root / "cache.tmp").write_bytes(b"explicitly excluded cache")
    include = {"path": "ignored.dat", "reason": "fixture required image",
               "size": (root / "ignored.dat").stat().st_size, "sha256": module.digest(root / "ignored.dat")}
    audit = {"_audit_path": "offline-no-production-audit", "_audit_sha256": "0" * 64,
             "ignored_review": {"complete": True, "ignored_paths_sha256": module.fingerprint(["cache.tmp", "ignored.dat"]),
                 "include": [include], "exclude": [{"path": "cache.tmp", "reason": "fixture cache"}]}}
    protected_bytes = files["protected.png"]
    protected = {"protected.png": {"mode": "100644", "oid": module.stable_source(root, "protected.png")["raw_blob"],
                    "size": len(protected_bytes), "sha256": hashlib.sha256(protected_bytes).hexdigest()}}
    module.FIXED, module.FIXED_TREE, module.LIMIT = commit, tree, 1024
    capture = module.Capture(root, root / ".git/capture-output", commit, audit, {}, protected, {"deleted-shot.png"})
    before = {"head": git(root, "rev-parse", "HEAD"), "index": module.digest(root / ".git/index"),
              "attrs": (root / ".gitattributes").read_bytes()}
    return capture, root, before, large, pointer


def unchanged(root, before):
    assert git(root, "rev-parse", "HEAD") == before["head"]
    assert module.digest(root / ".git/index") == before["index"]
    assert (root / ".gitattributes").read_bytes() == before["attrs"]


capture, root, before, large, pointer = fixture("positive")
report = capture.run_capture()
assert report["passed"] and report["catchup_path_count"] == 0 and report["target_commit"] is None
assert not report["publication_complete"] and not report["pushed"]
manifest = [json.loads(x) for x in Path(report["manifest_file"]).read_text().splitlines()]
assert len(manifest) == len({x["path"] for x in manifest}) == report["target_path_count"]
assert {x["path"] for x in manifest} == set(capture.tree(report["target_tree"]))
assert "ignored.dat" in {x["path"] for x in manifest} and "cache.tmp" not in {x["path"] for x in manifest}
assert len(report["lfs_objects"]) == 2 and len(report["new_lfs_paths"]) == 1
assert all(Path(x["storage_path"]).is_relative_to(capture.bare) and module.digest(x["storage_path"]) == x["sha256"] for x in report["lfs_objects"])
raw_large = module.stable_source(root, large)["raw_blob"]
absent = subprocess.run([GIT, "--git-dir=" + str(capture.bare), "cat-file", "-e", raw_large], env=ENV, capture_output=True)
assert absent.returncode != 0, "Raw oversized blob was written to Git"
unchanged(root, before)
results.append({"test": "full_fixture_success_exact_tree_ignored_lfs_attrs_and_live_preservation", "passed": True})


def rejected(label, mutate, expected, nested=False):
    capture, root, before, large, pointer = fixture(label, nested)
    mutate(capture, root, pointer)
    if label == "unknown-attrs":
        before["attrs"] = (root / ".gitattributes").read_bytes()
    try:
        capture.run_capture()
    except (RuntimeError, OSError) as error:
        assert expected in str(error), (label, str(error))
    else:
        raise AssertionError("Unsafe fixture did not fail: " + label)
    unchanged(root, before)
    assert not (capture.run / "capture-report.json").exists()
    results.append({"test": label, "passed": True, "expected_rejection": expected})


rejected("missing-baseline", lambda c, r, p: (r / "keep.txt").unlink(), "Deletion is not permitted")
rejected("protected-change", lambda c, r, p: (r / "protected.png").write_bytes(b"changed"), "Protected original changed")
rejected("unknown-attrs", lambda c, r, p: (r / ".gitattributes").write_bytes(b"*.txt filter=unreviewed\n"), "Unknown .gitattributes edit")
rejected("lfs-placeholder", lambda c, r, p: (r / "old.bin").write_bytes(p), "unsmudged placeholder")
rejected("different-lfs-placeholder", lambda c, r, p: (r / "old.bin").write_bytes(p.replace(b"size ", b"size 1", 1)), "pointer text")
rejected("nested-attribute-override", lambda c, r, p: None, "Nested attributes override", nested=True)
rejected("deleted-screenshot-returned", lambda c, r, p: (r / "deleted-shot.png").write_bytes(b"shot"), "approved deleted screenshot")
rejected("ignored-inclusion-byte-change", lambda c, r, p: (r / "ignored.dat").write_bytes(b"new ignored bytes"), "Approved ignored source changed")


def changed_mid_capture(capture, root, _):
    original = capture.inventory
    count = 0
    def inventory():
        nonlocal count
        count += 1
        if count == 2:
            (root / "keep.txt").write_bytes(b"changed after first capture pass\n")
        return original()
    capture.inventory = inventory


rejected("nonzero-catchup", changed_mid_capture, "catchup must be zero")
for path in ("../escape", "/absolute", "a/.git/index", "D:/absolute", "a\\b"):
    try:
        module.safe_path(path)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Unsafe path accepted")
results.append({"test": "path_boundary_rejections", "passed": True})

# Validate the real freeze-schema parser against a separate, invented fixture.
# Every ID/path below belongs only to this fixture, never to production evidence.
root = FIXTURES / "freeze-schema"
root.mkdir()
module.ROOT = root
module.WORK = root / ".git/migration-latest-20261011"
module.WORK.mkdir(parents=True)
def document(relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content), encoding="utf-8")
    return {"path": str(path), "sha256": module.digest(path)}
when = module.now()
ids = ["fixture-producer-" + str(i) for i in range(15)]
request = document("docs/fixture-request.json", {"requested": True})
dispatch = document("docs/fixture-dispatch.json", {"freezeSentToAll": True,
    "receipts": [{"id": item, "success": True} for item in ids]})
signoff = document("docs/fixture-signoff.json", {"reviewed": True})
audits = [dict(document("docs/fixture-audit-" + str(i) + ".json", {"passed": True}), exists=True) for i in range(3)]
zones, producers = [], []
for i, key in enumerate(sorted(module.EXPECTED_ZONES)):
    map_name, zone_name = key.split("/")
    owned = "qdao_city_tiles_4k_20260916/builtin_q64_production/" + key
    checkpoint = document(owned + "/migration-freeze-20261011.json", {"generationStopped": True, "inFlightCount": 0})
    zones.append({"map": map_name, "zone": zone_name, "ready": True, "checkpointExists": True,
        "auditReportedReady": True, "auditMatchesCurrentCheckpoint": True, "blockers": [], "auditBlockers": [],
        "checkpointPath": checkpoint["path"], "checkpointSha256": checkpoint["sha256"],
        "independentAudit": audits[i // 5]["path"], "auditEvidence": {"checkpoint": checkpoint}})
    producers.append({"id": ids[i], "zone_key": key, "owned_roots": [owned], "state": "frozen",
        "generationStopped": True, "unsavedSuccessfulOutputPaths": [], "external_outputs_resolved": True,
        "saved_at_utc": when, "receipt": checkpoint})
# Real compact coordinator schema: each map audit owns five rows and checkpoint
# identity is on the row itself, without requiring evidence.checkpoint to exist.
audits = []
for map_name, relative in module.AUDIT_PATHS.items():
    rows = [{"zone": z["zone"], "checkpointPath": z["checkpointPath"],
             "checkpointSha256": z["checkpointSha256"], "ready": True, "blockers": [],
             "evidence": {"generationStopped": True, "unsavedSuccessfulOutputPaths": []}}
            for z in zones if z["map"] == map_name]
    source_manifest = document("docs/fixture-source-" + map_name + ".json", {"entries": []})
    rows[0]["evidence"]["sourceManifest"] = {
        "manifest": source_manifest["path"], "manifestSha256": "0" * 64,
        "currentManifestSha256": source_manifest["sha256"]}
    item = dict(document(relative, {"allReady": True, "zones": rows}), exists=True, map=map_name)
    audits.append(item)
    for z in zones:
        if z["map"] == map_name:
            z["independentAudit"] = item["path"]
            z["auditEvidence"] = {"auditPath": item["path"], "auditSha256": item["sha256"],
                                   "zoneKey": z["zone"], "detailLocation": "zones entry evidence"}
archive_files = []
for i in range(12):
    relative = "designs/user-references/map-style-20261011/fixture-" + str(i) + ".jpg"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fixture photo " + str(i).encode())
    archive_files.append({"workspaceRelativePath": relative, "status": "archived_byte_exact", "hashMatches": True,
                          "sha256": module.digest(path), "bytes": path.stat().st_size})
archive = document("designs/user-references/map-style-20261011/archive-index.json",
                   {"archivedCount": 12, "missingOriginalCount": 0, "files": archive_files})
gate = {"readyToCaptureFinalIncrement": True, "expectedZoneCount": 15, "checkpointCount": 15,
        "readyZoneCount": 15, "zones": zones, "audits": audits,
        "userAttachmentArchive": {"path": archive["path"], "all12ArchivedAndHashVerified": True}}
gate_file = document("docs/MAP_MIGRATION_READY_20261011.json", gate)
audit = {"schema_version": 1, "purpose": "capture-frozen-image-delta", "approved": True,
    "all_writers_frozen": True, "other_writers_reviewed": True, "reviewed_by": "offline fixture only",
    "requested_at_utc": when, "reviewed_at_utc": when, "workspace_root": str(root), "fixed_target": module.FIXED,
    "expected_producer_ids": ids, "producers": producers, "freeze_request": request, "dispatch_evidence": dispatch,
    "coordinator_signoff": signoff, "readiness_gate": gate_file, "user_reference_archive": archive,
    "ignored_review": {"complete": True}}
audit_file = document(".git/migration-latest-20261011/fixture-freeze.json", audit)
checked, pins = module.read_freeze(audit_file["path"], audit_file["sha256"])
assert len(checked["producers"]) == 15 and all(str(root / r["workspaceRelativePath"]) in pins for r in archive_files)
results.append({"test": "compact_freeze_schema_exact_fifteen_dispatch_checkpoints_and_twelve_archives", "passed": True})

def freeze_rejected(label, mutate_gate, expected_error):
    changed_gate = json.loads(json.dumps(gate))
    changed_audit = json.loads(json.dumps(audit))
    mutate_gate(changed_gate)
    changed_audit["readiness_gate"] = document("docs/MAP_MIGRATION_READY_20261011.json", changed_gate)
    reviewed = document(".git/migration-latest-20261011/fixture-" + label + ".json", changed_audit)
    try:
        module.read_freeze(reviewed["path"], reviewed["sha256"])
    except RuntimeError as error:
        assert expected_error in str(error), (label, str(error))
    else:
        raise AssertionError("Unsafe freeze reference accepted: " + label)
    results.append({"test": label, "passed": True})

freeze_rejected("compact_wrong_zone_rejected",
    lambda g: g["zones"][0]["auditEvidence"].update(zoneKey="not-this-zone"), "Compact audit reference")
freeze_rejected("compact_wrong_hash_rejected",
    lambda g: g["zones"][0]["auditEvidence"].update(auditSha256="0" * 64), "Compact audit reference")
freeze_rejected("map_audit_actual_hash_mismatch_rejected",
    lambda g: g["audits"][0].update(sha256="0" * 64), "Evidence checksum differs")
freeze_rejected("wrong_map_audit_reference_rejected",
    lambda g: g["zones"][0].update(independentAudit=g["audits"][-1]["path"]), "map's pinned audit")
# Legacy embedded gates remain accepted only by resolving the same independently
# pinned row first; neither legacy nor compact records can stand in for that row.
legacy_gate = json.loads(json.dumps(gate))
for z in legacy_gate["zones"]:
    z["auditEvidence"] = {"checkpoint": {"path": z["checkpointPath"], "sha256": z["checkpointSha256"]}}
legacy_audit = json.loads(json.dumps(audit))
legacy_audit["readiness_gate"] = document("docs/MAP_MIGRATION_READY_20261011.json", legacy_gate)
legacy_file = document(".git/migration-latest-20261011/fixture-legacy.json", legacy_audit)
module.read_freeze(legacy_file["path"], legacy_file["sha256"])
results.append({"test": "legacy_embedded_gate_still_checks_pinned_independent_zone", "passed": True})
# Real main-city audit rows embed metadata-only checkpoint snapshots beside a
# mandatory hashed row identity. Metadata validates location/existence/size and
# cannot silently substitute for any hashed checkpoint identity.
metadata_zone = json.loads(json.dumps(gate["zones"][0]))
metadata_item = next(a for a in gate["audits"] if a["map"] == metadata_zone["map"])
metadata_document = json.loads(Path(metadata_item["path"]).read_text())
metadata_row = next(r for r in metadata_document["zones"] if r["zone"] == metadata_zone["zone"])
metadata_row["evidence"]["checkpoint"] = {
    "path": metadata_zone["checkpointPath"], "exists": True,
    "bytes": Path(metadata_zone["checkpointPath"]).stat().st_size, "lastWriteUtc": when}
metadata_map = {metadata_zone["map"]: (metadata_item, metadata_document)}
assert module.resolve_zone_evidence(metadata_zone, metadata_map) is metadata_row["evidence"]
results.append({"test": "metadata_only_checkpoint_supported_with_actual_hashed_top_row", "passed": True})

def metadata_rejected(label, mutate, expected):
    bad_doc = json.loads(json.dumps(metadata_document))
    bad_row = next(r for r in bad_doc["zones"] if r["zone"] == metadata_zone["zone"])
    mutate(bad_row)
    try:
        module.resolve_zone_evidence(metadata_zone, {metadata_zone["map"]: (metadata_item, bad_doc)})
    except RuntimeError as error:
        assert expected in str(error), (label, str(error))
    else:
        raise AssertionError("Unsafe checkpoint identity accepted: " + label)
    results.append({"test": label, "passed": True})

metadata_rejected("metadata_only_checkpoint_wrong_path_rejected",
                  lambda row: row["evidence"]["checkpoint"].update(path=str(root / "docs/fixture-request.json")),
                  "checkpoint path/hash")
def remove_hashed_row(row):
    row.pop("checkpointPath"); row.pop("checkpointSha256")
metadata_rejected("metadata_only_checkpoint_without_any_hashed_identity_rejected",
                  remove_hashed_row, "does not pin a checkpoint")
metadata_rejected("malformed_embedded_checkpoint_digest_rejected",
                  lambda row: row["evidence"]["checkpoint"].update(sha256="not-a-sha256"),
                  "SHA256 is malformed")

# Added portable aliases/nested-manifest checks, using fake nonexistent originals.
# Only tiny fixture copies are opened; no production paths or network are used.
alias_rows = []
for i in range(160):
    relative = "portable/copy-" + str(i) + ".png"
    copy = root / relative
    copy.parent.mkdir(exist_ok=True)
    copy.write_bytes(("small-fixture-art-" + str(i)).encode())
    alias_rows.append({"original_path": str(FIXTURES / "outside-not-created" / ("source-" + str(i) + ".png")),
                       "workspace_copy": relative, "sha256": module.digest(copy), "size": copy.stat().st_size})
assert all(not Path(r["original_path"]).exists() for r in alias_rows)

portable_gate = json.loads(json.dumps(gate))
first_map = portable_gate["zones"][0]["map"]
first_audit = next(a for a in portable_gate["audits"] if a["map"] == first_map)
audit_doc = json.loads(Path(first_audit["path"]).read_text())
source_manifest = document("docs/nested-source.json", {"saved": True})
audit_doc["zones"][0]["evidence"]["portableSources"] = [
    {"path": r["original_path"], "sha256": r["sha256"]} for r in alias_rows]
audit_doc["zones"][0]["evidence"]["nestedSourceManifest"] = {
    "manifest": {"path": source_manifest["path"], "sha256": source_manifest["sha256"]},
    "manifestSha256": source_manifest["sha256"]}
new_item = document(module.AUDIT_PATHS[first_map], audit_doc)
first_audit["sha256"] = new_item["sha256"]
for z in portable_gate["zones"]:
    if z["map"] == first_map:
        z["auditEvidence"]["auditSha256"] = new_item["sha256"]
portable_audit = json.loads(json.dumps(audit))
portable_audit["readiness_gate"] = document("docs/MAP_MIGRATION_READY_20261011.json", portable_gate)
portable_audit["portable_source_aliases"] = alias_rows
portable_audit["portable_source_aliases_manifest"] = document("docs/portable-source-aliases.json", {"aliases": alias_rows})
portable_file = document(".git/migration-latest-20261011/portable-freeze.json", portable_audit)
portable_checked, portable_pins = module.read_freeze(portable_file["path"], portable_file["sha256"])
assert all(str((root / r["workspace_copy"]).resolve()) in portable_pins for r in alias_rows)
assert str((root / "docs/portable-source-aliases.json").resolve()) in portable_pins
assert str((root / "docs/nested-source.json").resolve()) in portable_pins
assert all(not Path(r["original_path"]).exists() for r in alias_rows)
results.append({"test": "160_explicit_outside_aliases_and_nested_manifest_are_pinned_without_original_access", "passed": True})

def alias_reject(label, operation, needle):
    try:
        operation()
    except (RuntimeError, OSError) as error:
        assert needle in str(error), (label, str(error))
    else:
        raise AssertionError("Unsafe alias input accepted: " + label)
    results.append({"test": label, "passed": True})

aliases = module.checked_portable_aliases(root, alias_rows)
alias_reject("outside_source_without_alias_rejected",
             lambda: module.evidence_file(root, {"path": alias_rows[0]["original_path"], "sha256": alias_rows[0]["sha256"]}),
             "no explicit portable alias")
alias_reject("outside_reference_digest_not_alias_digest_rejected",
             lambda: module.evidence_file(root, {"path": alias_rows[0]["original_path"], "sha256": "0" * 64}, aliases),
             "source SHA differs")
alias_reject("duplicate_original_alias_rejected",
             lambda: module.checked_portable_aliases(root, alias_rows + [alias_rows[0]]), "Duplicate or ambiguous")
wrong_copy = dict(alias_rows[1], original_path=alias_rows[0]["original_path"])
alias_reject("ambiguous_original_to_two_copies_rejected",
             lambda: module.checked_portable_aliases(root, [alias_rows[0], wrong_copy]), "Duplicate or ambiguous")
alias_reject("wrong_alias_size_rejected",
             lambda: module.checked_portable_aliases(root, [dict(alias_rows[0], size=0)]), "size differs")
alias_reject("wrong_alias_copy_digest_rejected",
             lambda: module.checked_portable_aliases(root, [dict(alias_rows[0], sha256="0" * 64)]), "checksum differs")
alias_reject("alias_copy_traversal_rejected",
             lambda: module.checked_portable_aliases(root, [dict(alias_rows[0], workspace_copy="../escape.png")]), "path")
alias_reject("alias_for_workspace_original_rejected",
             lambda: module.checked_portable_aliases(root, [dict(alias_rows[0], original_path=str(root / "keep.png"))]),
             "outside workspace")
(root / alias_rows[0]["workspace_copy"]).write_bytes(b"tampered copy")
alias_reject("alias_copy_tamper_after_alias_review_rejected",
             lambda: module.evidence_file(root, {"path": alias_rows[0]["original_path"], "sha256": alias_rows[0]["sha256"]}, aliases),
             "checksum differs")
(root / alias_rows[0]["workspace_copy"]).write_bytes(b"small-fixture-art-0")

missing = json.loads(json.dumps(portable_audit))
missing["portable_source_aliases"] = alias_rows[:-1]
missing["portable_source_aliases_manifest"] = document("docs/missing-aliases.json", {"aliases": alias_rows[:-1]})
missing_file = document(".git/migration-latest-20261011/missing-alias-freeze.json", missing)
alias_reject("full_freeze_missing_one_of_160_aliases_rejected",
             lambda: module.read_freeze(missing_file["path"], missing_file["sha256"]), "no explicit portable alias")
missing_manifest = json.loads(json.dumps(portable_audit))
missing_manifest.pop("portable_source_aliases_manifest")
f = document(".git/migration-latest-20261011/missing-mapping-freeze.json", missing_manifest)
alias_reject("full_freeze_requires_committed_portable_manifest",
             lambda: module.read_freeze(f["path"], f["sha256"]), "committed mapping manifest")
wrong_manifest = json.loads(json.dumps(portable_audit))
wrong_manifest["portable_source_aliases_manifest"] = document("docs/wrong-aliases.json", {"aliases": []})
f = document(".git/migration-latest-20261011/wrong-mapping-freeze.json", wrong_manifest)
alias_reject("portable_manifest_exact_row_equality_required",
             lambda: module.read_freeze(f["path"], f["sha256"]), "differs from reviewed rows")
private_manifest = json.loads(json.dumps(portable_audit))
private_manifest["portable_source_aliases_manifest"] = document(".git/migration-latest-20261011/private-aliases.json", {"aliases": alias_rows})
f = document(".git/migration-latest-20261011/private-mapping-freeze.json", private_manifest)
alias_reject("mapping_manifest_cannot_remain_only_in_dotgit",
             lambda: module.read_freeze(f["path"], f["sha256"]), "included in committed workspace")

# Nested manifest dictionaries verify both the outer current digest and any
# separately embedded path+SHA record; neither may bypass stale-source checks.
bad_nested_gate = json.loads(json.dumps(portable_gate))
bad_nested_audit_doc = json.loads(json.dumps(audit_doc))
bad_nested_audit_doc["zones"][0]["evidence"]["nestedSourceManifest"]["manifest"]["sha256"] = "0" * 64
bad_item = document(module.AUDIT_PATHS[first_map], bad_nested_audit_doc)
for a in bad_nested_gate["audits"]:
    if a["map"] == first_map:
        a["sha256"] = bad_item["sha256"]
for z in bad_nested_gate["zones"]:
    if z["map"] == first_map:
        z["auditEvidence"]["auditSha256"] = bad_item["sha256"]
bad_nested = json.loads(json.dumps(portable_audit))
bad_nested["readiness_gate"] = document("docs/MAP_MIGRATION_READY_20261011.json", bad_nested_gate)
f = document(".git/migration-latest-20261011/stale-inner-manifest-freeze.json", bad_nested)
alias_reject("nested_manifest_embedded_path_digest_is_checked",
             lambda: module.read_freeze(f["path"], f["sha256"]), "checksum differs")
alias_reject("relative_source_evidence_escape_cannot_use_alias",
             lambda: module.evidence_file(root, {"path": "../outside-not-created/source-0.png", "sha256": alias_rows[0]["sha256"]}, aliases),
             "traversal is forbidden")

# A real fixture content capture proves copy and full mapping enter final tree.
schema_fixed, schema_tree, schema_limit = module.FIXED, module.FIXED_TREE, module.LIMIT
cap, alias_root, before_alias, large_alias, pointer_alias = fixture("aliases-captured")
copy = alias_root / "portable/copy.png";copy.parent.mkdir();copy.write_bytes(b"small portable artwork")
row = {"original_path": str(FIXTURES / "external-not-created.png"), "workspace_copy": "portable/copy.png",
       "sha256": module.digest(copy), "size": copy.stat().st_size}
manifest_path = alias_root / "portable/aliases.json";manifest_path.write_text(json.dumps({"aliases": [row]}))
cap.audit["portable_source_aliases"] = [row]
cap.audit["portable_source_aliases_manifest"] = {"path": str(manifest_path), "sha256": module.digest(manifest_path)}
cap.pinned.update({str(copy): row["sha256"], str(manifest_path): module.digest(manifest_path)})
cap_report = cap.run_capture();cap_tree = cap.tree(cap_report["target_tree"])
assert {"portable/copy.png", "portable/aliases.json"} <= cap_tree.keys()
assert cap_report["portable_source_aliases"] == [row]
assert cap_report["portable_source_aliases_manifest"]["sha256"] == module.digest(manifest_path)
unchanged(alias_root, before_alias)
results.append({"test": "portable_copy_and_full_alias_manifest_captured_into_content_tree", "passed": True})

cap, excluded_root, excluded_before, large_excluded, pointer_excluded = fixture("excluded-alias-copy")
cap.pinned[str(excluded_root / "cache.tmp")] = module.digest(excluded_root / "cache.tmp")
alias_reject("required_portable_copy_cannot_be_excluded_from_content_tree",
             cap.run_capture, "was excluded from migration")
unchanged(excluded_root, excluded_before)
module.FIXED, module.FIXED_TREE, module.LIMIT = schema_fixed, schema_tree, schema_limit

gate["readyToCaptureFinalIncrement"] = False
audit["readiness_gate"] = document("docs/MAP_MIGRATION_READY_20261011.json", gate)
audit_file = document(".git/migration-latest-20261011/fixture-freeze-false.json", audit)
try:
    module.read_freeze(audit_file["path"], audit_file["sha256"])
except RuntimeError as error:
    assert "15/15" in str(error)
else:
    raise AssertionError("Unready coordinator gate was accepted")
results.append({"test": "not_ready_coordinator_refuses_capture", "passed": True})
assert module.digest(SCRIPT) == SCRIPT_SHA, "Capture script changed during offline validation"
receipt = {"passed": True, "tests": results, "count": len(results), "fixtures": str(FIXTURES),
           "capture_script_sha256": module.digest(SCRIPT), "production_capture_run": False,
           "script_unchanged_during_tests": True,
           "network_accessed": False, "production_live_git_written": False,
           "note": "Threshold lowered only in the imported test module to 1024 bytes; production remains 100 MiB."}
(WORK / "capture-lfs-prep-offline-verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k:v for k,v in receipt.items() if k != "tests"}, indent=2))
