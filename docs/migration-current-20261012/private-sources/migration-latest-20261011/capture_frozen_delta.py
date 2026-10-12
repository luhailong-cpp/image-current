"""Prepare a frozen content tree in a NEW isolated repository; never publish it.

No command runs by default. --help and Python AST/compile checks create nothing.
Production invocation requires: capture --freeze-evidence PATH --freeze-sha256 SHA
Read freeze-evidence.schema.example.json and CAPTURE_CONTRACT.txt before use.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path("D:/work/image")
WORK = ROOT / ".git/migration-latest-20261011"
OLD = ROOT / ".git/migration-sync-20261011"
FIXED = "26f1df45fff54098dc593ae7a005c3f9a9871ac3"
FIXED_TREE = "92b5b79c2500fa93e579fe349e06ccec52151776"
FIXED_REPORT_SHA = "67f3ea4da24cb6d7e3ee876124a176c0c3890efb46237f999ae35e697c03c9ce"
PRODUCER_COUNT = 15
EXPECTED_ZONES = {
    map_name + "/" + zone for map_name, extra in (
        ("main-city-game-20261009", "accelerated-yamen-north"),
        ("fishing-village-game-20261009", "accelerated-jewelry-approach"),
        ("island-game-20261009", "accelerated-northeast-coast"))
    for zone in ("northwest", "northeast", "southwest", "southeast", extra)
}
AUDIT_PATHS = {
    "main-city-game-20261009": "docs/map-freeze-audit-main-20261011.json",
    "fishing-village-game-20261009": "docs/map-freeze-audit-village-20261011.json",
    "island-game-20261009": "docs/map-freeze-audit-island-20261011.json",
}
PROTECTED_COUNT = 6516
DELETED_COUNT = 186
LIMIT = 100 * 1024 * 1024
BLOCK = 4 * 1024 * 1024
GIT = shutil.which("git") or "git"
ZERO = "0" * 40
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temp.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def safe_path(value):
    require(isinstance(value, str) and value and "\\" not in value
            and not any(ord(c) < 32 for c in value) and not value.startswith("/")
            and not re.match(r"^[A-Za-z]:", value)
            and all(p not in ("", ".", "..") and p.lower() != ".git" for p in value.split("/")),
            "Unsafe repository path: " + repr(value))
    return value


def no_link(path, directory=False):
    path = Path(path)
    require(not path.is_symlink() and not path.is_junction(), "Linked path is forbidden: " + str(path))
    require(path.is_dir() if directory else path.is_file(), "Missing/invalid path: " + str(path))


def source_path(root, relative):
    relative = safe_path(relative)
    path = root / relative
    parent = root
    for part in PurePosixPath(relative).parts[:-1]:
        parent = parent / part
        no_link(parent, directory=True)
    # A leaf symlink is stored as its link text, never followed.
    require(not path.is_junction(), "Junction source is forbidden: " + relative)
    return path


def signature(st):
    # Windows fstat.st_ctime and path.stat.st_ctime can disagree; birthtime does not.
    return (st.st_size, st.st_mtime_ns, getattr(st, "st_birthtime_ns", st.st_ctime_ns),
            stat.S_IFMT(st.st_mode))


def stable_source(root, relative, destination=None):
    """Stream exactly one stable file version. Optional spool is task-owned only."""
    path = source_path(root, relative)
    before = path.lstat()  # Missing is always fatal, never interpreted as a deletion.
    symlink = stat.S_ISLNK(before.st_mode)
    require(symlink or stat.S_ISREG(before.st_mode), "Non-regular source: " + relative)
    sink = None
    try:
        if destination is not None:
            sink = Path(destination).open("xb")
        if symlink:
            data = os.readlink(path).encode("utf-8")
            sha256 = hashlib.sha256(data)
            raw = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data)
            size = len(data)
            if sink:
                sink.write(data)
            require(signature(before) == signature(path.lstat()), "Symlink changed: " + relative)
            source_stat = signature(before)
        else:
            with path.open("rb") as stream:
                first = os.fstat(stream.fileno())
                require(signature(before) == signature(first), "Source replaced before open: " + relative)
                sha256 = hashlib.sha256()
                raw = hashlib.sha1(b"blob " + str(first.st_size).encode() + b"\0")
                size = 0
                while block := stream.read(BLOCK):
                    size += len(block)
                    sha256.update(block)
                    raw.update(block)
                    if sink:
                        sink.write(block)
                last = os.fstat(stream.fileno())
            require(size == first.st_size and signature(first) == signature(last) == signature(path.lstat()),
                    "Unstable or short source read: " + relative)
            source_stat = signature(first)
        if sink:
            sink.flush()
            os.fsync(sink.fileno())
        return {"source_bytes": size, "source_sha256": sha256.hexdigest(), "raw_blob": raw.hexdigest(),
                "source_stat": list(source_stat), "symlink": symlink}
    finally:
        if sink:
            sink.close()


def same_source(a, b):
    return all(a[key] == b[key] for key in
               ("source_bytes", "source_sha256", "raw_blob", "source_stat", "symlink"))


def evidence_file(root, item):
    require(set(item) >= {"path", "sha256"}, "Evidence needs exact path and SHA256")
    path = Path(item["path"])
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    require(path.is_relative_to(root.resolve()) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]),
            "Evidence must be an explicitly named local workspace file")
    no_link(path)
    require(digest(path) == item["sha256"], "Evidence checksum differs: " + str(path))
    return path


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "Evidence timestamps need a timezone")
    return result


def resolve_zone_evidence(zone, audits_by_map):
    """Resolve only the pinned audit for this exact map and zone.

    Current audits store checkpoint identity on the zone row; older audits may
    additionally embed it in row.evidence.checkpoint. Both, when present, agree.
    The gate's compact reference never supplies or substitutes actual evidence.
    """
    require(zone["map"] in audits_by_map, "Zone map has no pinned independent audit")
    item, document = audits_by_map[zone["map"]]
    audit_path = Path(item["path"]).resolve()
    require(Path(zone["independentAudit"]).resolve() == audit_path,
            "Zone independent audit differs from its map's pinned audit")
    gate_evidence = zone["auditEvidence"]
    require(isinstance(gate_evidence, dict), "Malformed gate audit evidence")
    compact = any(key in gate_evidence for key in ("auditPath", "auditSha256", "zoneKey"))
    if compact:
        require(set(gate_evidence) >= {"auditPath", "auditSha256", "zoneKey"}
                and Path(gate_evidence["auditPath"]).resolve() == audit_path
                and gate_evidence["auditSha256"] == item["sha256"]
                and gate_evidence["zoneKey"] == zone["zone"],
                "Compact audit reference has the wrong map, zone, path, or hash")
    rows = document.get("zones")
    require(isinstance(rows, list), "Independent audit must contain explicit zone rows")
    matches = [row for row in rows if row.get("zone") == zone["zone"]]
    require(len(matches) == 1, "Independent audit does not uniquely identify the exact zone")
    row = matches[0]
    require(row.get("map", zone["map"]) == zone["map"]
            and row.get("ready") is True and row.get("blockers") == [],
            "Exact independent audit zone is not ready or has blockers")
    evidence = row.get("evidence")
    require(isinstance(evidence, dict), "Exact independent audit zone lacks source evidence")
    checkpoint = {"path": zone["checkpointPath"], "sha256": zone["checkpointSha256"]}
    expected_path = Path(checkpoint["path"]).resolve()
    identities = []
    if "checkpointPath" in row or "checkpointSha256" in row:
        identities.append({"path": row.get("checkpointPath"), "sha256": row.get("checkpointSha256")})
    if "checkpoint" in evidence:
        identities.append(evidence["checkpoint"])
    require(identities, "Exact independent audit zone does not pin a checkpoint")
    if not compact:
        require("checkpoint" in gate_evidence, "Legacy embedded gate evidence lacks its checkpoint")
        identities.append(gate_evidence["checkpoint"])
    elif "checkpoint" in gate_evidence:
        identities.append(gate_evidence["checkpoint"])
    for identity in identities:
        require(isinstance(identity, dict) and isinstance(identity.get("path"), str)
                and Path(identity["path"]).resolve() == expected_path
                and identity.get("sha256") == checkpoint["sha256"],
                "Exact zone audit checkpoint path/hash does not match the current gate")
    return evidence


def read_freeze(path, expected_sha):
    path = Path(path).resolve()
    require(path.is_relative_to(WORK.resolve()), "Freeze audit must be explicitly saved in the new task directory")
    require(re.fullmatch(r"[0-9a-f]{64}", expected_sha or ""), "Explicit freeze audit SHA256 is required")
    no_link(path)
    require(digest(path) == expected_sha, "Freeze audit checksum differs")
    data = load(path)
    require(data.get("schema_version") == 1 and data.get("purpose") == "capture-frozen-image-delta"
            and data.get("approved") is True and data.get("all_writers_frozen") is True
            and data.get("other_writers_reviewed") is True and bool(data.get("reviewed_by"))
            and Path(data["workspace_root"]).resolve() == ROOT.resolve()
            and data.get("fixed_target") == FIXED, "Explicit completed root freeze review is required")
    requested = timestamp(data["requested_at_utc"])
    reviewed = timestamp(data["reviewed_at_utc"])
    require(requested <= reviewed <= datetime.now(timezone.utc), "Invalid freeze review ordering")
    expected = data["expected_producer_ids"]
    producers = data["producers"]
    require(len(expected) == len(set(expected)) == PRODUCER_COUNT
            and {p["id"] for p in producers} == set(expected) and len(producers) == len(expected),
            "Every expected producer needs exactly one reviewed freeze acknowledgement")
    pinned = {str(path): expected_sha}
    for key in ("freeze_request", "dispatch_evidence", "coordinator_signoff"):
        item = data[key]
        pinned[str(evidence_file(ROOT, item))] = item["sha256"]
    dispatch = load(evidence_file(ROOT, data["dispatch_evidence"]))
    dispatched = dispatch.get("receipts", [])
    require(dispatch.get("freezeSentToAll") is True and len(dispatched) == PRODUCER_COUNT
            and len({r["id"] for r in dispatched}) == PRODUCER_COUNT
            and {r["id"] for r in dispatched} == set(expected)
            and all(r.get("success") is True for r in dispatched),
            "Reviewed producer IDs must exactly match all successful freeze dispatch recipients")
    for producer in producers:
        require(producer.get("state") == "frozen" and producer.get("generationStopped") is True
                and producer.get("unsavedSuccessfulOutputPaths") == [] and producer.get("owned_roots")
                and producer.get("external_outputs_resolved") is True,
                "Producer is not fully frozen/saved: " + producer["id"])
        require(requested <= timestamp(producer["saved_at_utc"]) <= reviewed,
                "Producer receipt predates request or postdates review")
        for owned in producer["owned_roots"]:
            safe_path(owned.rstrip("/"))
        item = producer["receipt"]
        pinned[str(evidence_file(ROOT, item))] = item["sha256"]
    readiness_item = data["readiness_gate"]
    readiness_path = evidence_file(ROOT, readiness_item)
    require(readiness_path == (ROOT / "docs/MAP_MIGRATION_READY_20261011.json").resolve(),
            "The coordinator's exact readiness gate is required")
    pinned[str(readiness_path)] = readiness_item["sha256"]
    gate = load(readiness_path)
    require(gate.get("readyToCaptureFinalIncrement") is True
            and gate.get("expectedZoneCount") == PRODUCER_COUNT
            and gate.get("checkpointCount") == PRODUCER_COUNT
            and gate.get("readyZoneCount") == PRODUCER_COUNT,
            "Coordinator readiness gate is not 15/15; real capture is forbidden")
    zones = gate["zones"]
    zone_keys = [zone["map"] + "/" + zone["zone"] for zone in zones]
    require(len(zones) == len(set(zone_keys)) == PRODUCER_COUNT
            and set(zone_keys) == {p["zone_key"] for p in producers} == EXPECTED_ZONES,
            "Producer/zone mapping differs from the fifteen production zones")
    audits_by_map = {}
    for item in gate["audits"]:
        require(item.get("exists") is True, "A coordinator audit is missing")
        map_name = item.get("map")
        require(map_name in AUDIT_PATHS and map_name not in audits_by_map,
                "Duplicate or unexpected map audit")
        audit_path = evidence_file(ROOT, item)
        require(audit_path == (ROOT / AUDIT_PATHS[map_name]).resolve(),
                "Map audit path differs from its assigned independent audit")
        document = load(audit_path)
        require(digest(audit_path) == item["sha256"], "Independent audit changed while reading")
        expected_rows = {key.split("/", 1)[1] for key in EXPECTED_ZONES if key.startswith(map_name + "/")}
        rows = document.get("zones")
        require(isinstance(rows, list) and len(rows) == len(expected_rows)
                and {row.get("zone") for row in rows} == expected_rows,
                "Independent audit is not the exact five zones for its map")
        pinned[str(audit_path)] = item["sha256"]
        audits_by_map[map_name] = (item, document)
    require(set(audits_by_map) == set(AUDIT_PATHS), "Every map requires its own pinned independent audit")
    def pin_audit_sources(value):
        if isinstance(value, dict):
            for path_key, hash_key in (("path", "sha256"), ("manifestPath", "manifestSha256")):
                if value.get(path_key) and value.get(hash_key):
                    item = {"path": value[path_key], "sha256": value[hash_key]}
                    pinned[str(evidence_file(ROOT, item))] = item["sha256"]
            # Village audits name portable manifests with "manifest". Some
            # rows retain a historical digest beside a current digest; only the
            # explicitly current value is a present-file checksum in that case.
            if value.get("manifest") and (value.get("currentManifestSha256") or value.get("manifestSha256")):
                expected = value.get("currentManifestSha256") or value["manifestSha256"]
                item = {"path": value["manifest"], "sha256": expected}
                pinned[str(evidence_file(ROOT, item))] = expected
            for child in value.values():
                pin_audit_sources(child)
        elif isinstance(value, list):
            for child in value:
                pin_audit_sources(child)
    for zone in zones:
        require(zone.get("ready") is True and zone.get("checkpointExists") is True
                and zone.get("auditReportedReady") is True and zone.get("auditMatchesCurrentCheckpoint") is True
                and not zone.get("blockers") and not zone.get("auditBlockers"), "A zone still has freeze blockers")
        item = {"path": zone["checkpointPath"], "sha256": zone["checkpointSha256"]}
        checkpoint_path = evidence_file(ROOT, item)
        pinned[str(checkpoint_path)] = item["sha256"]
        producer = next(p for p in producers if p["zone_key"] == zone["map"] + "/" + zone["zone"])
        owned_root = "qdao_city_tiles_4k_20260916/builtin_q64_production/" + producer["zone_key"]
        require(owned_root in {root.rstrip("/") for root in producer["owned_roots"]}
                and checkpoint_path.parent == (ROOT / owned_root).resolve(),
                "Producer checkpoint is not in its reviewed production zone")
        require(evidence_file(ROOT, producer["receipt"]) == checkpoint_path
                and producer["receipt"]["sha256"] == item["sha256"], "Producer receipt is not the audited current checkpoint")
        independent_evidence = resolve_zone_evidence(zone, audits_by_map)
        pin_audit_sources(independent_evidence)
        # Preserve extra hashed sources in legacy embedded coordinator records.
        pin_audit_sources(zone["auditEvidence"])
    for item in data.get("source_evidence", []):
        pinned[str(evidence_file(ROOT, item))] = item["sha256"]
    archive_meta = gate["userAttachmentArchive"]
    require(archive_meta.get("all12ArchivedAndHashVerified") is True, "User reference archive is incomplete")
    archive_path = Path(archive_meta["path"]).resolve()
    require(archive_path == (ROOT / "designs/user-references/map-style-20261011/archive-index.json").resolve(),
            "Unexpected user reference archive")
    archive_item = data["user_reference_archive"]
    require(evidence_file(ROOT, archive_item) == archive_path, "User reference archive lacks explicit pinned hash")
    pinned[str(archive_path)] = archive_item["sha256"]
    archive = load(archive_path)
    require(archive.get("archivedCount") == 12 and archive.get("missingOriginalCount") == 0
            and len(archive["files"]) == 12, "Expected twelve archived user reference images")
    for item in archive["files"]:
        require(item.get("status") == "archived_byte_exact" and item.get("hashMatches") is True,
                "A user reference lacks exact-byte archival")
        relative = safe_path(item["workspaceRelativePath"])
        item_path = evidence_file(ROOT, {"path": relative, "sha256": item["sha256"]})
        require(item_path.stat().st_size == item["bytes"], "Archived user reference size differs")
        pinned[str(item_path)] = item["sha256"]
    require(data.get("ignored_review", {}).get("complete") is True,
            "Ignored files need an explicit complete inclusion/exclusion review")
    require(digest(path) == expected_sha, "Freeze audit changed during validation")
    return data, pinned


def protection_contract():
    final = load(OLD / "final-target.json")
    require(digest(OLD / "final-target.json") == FIXED_REPORT_SHA
            and final["commit"] == FIXED and final["tree"] == FIXED_TREE,
            "Fixed target evidence changed")
    pinned = {str(OLD / "final-target.json"): FIXED_REPORT_SHA}
    for name, expected in final["evidence_sha256"].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to((ROOT / ".git").resolve()) and digest(path) == expected,
                "Protected-image evidence changed")
        pinned[str(path)] = expected
    before_name = ".git/asset-recovery-20261011/images-before-cleanup.json"
    deleted_name = ".git/asset-recovery-20261011/approved-screenshots-plan.json"
    receipt_name = ".git/asset-recovery-20261010/restore-receipt.jsonl"
    require(all(str((ROOT / n).resolve()) in pinned for n in (before_name, deleted_name, receipt_name)),
            "Protection source lacks pinned evidence")
    before = load(ROOT / before_name)["entries"]
    removed = load(ROOT / deleted_name)["entries"]
    initial = {x["path"]: x for x in before}
    deleted = {x["path"] for x in removed}
    require(len(initial) == len(before) == PROTECTED_COUNT + DELETED_COUNT
            and len(deleted) == len(removed) == DELETED_COUNT and deleted <= initial.keys(),
            "Protection/deletion inventory differs")
    receipts = {}
    for line in (ROOT / receipt_name).read_text(encoding="utf-8-sig").splitlines():
        if line:
            item = json.loads(line)
            if item["path"] in initial:
                require(item["path"] not in receipts, "Duplicate protected restoration receipt")
                receipts[item["path"]] = item
    protected = {}
    for name, prior in initial.items():
        item = receipts[name]
        require((prior["size"], prior["sha256"]) == (item["size"], item["sha256"]),
                "Restoration/source protection hash mismatch")
        if name not in deleted:
            protected[name] = {"mode": item["mode"], "oid": item["oid"],
                               "size": item["size"], "sha256": item["sha256"]}
    require(len(protected) == PROTECTED_COUNT, "Protected set changed")
    return protected, deleted, pinned


class Capture:
    def __init__(self, root, run, baseline, audit, pinned, protected, deleted):
        self.root, self.run = Path(root).resolve(), Path(run).resolve()
        self.live = self.root / ".git"
        self.bare = self.run / "capture.git"
        self.index = self.bare / "capture.index"
        self.spools = self.run / "spools"
        self.baseline, self.audit, self.pinned = baseline, audit, pinned
        self.protected, self.deleted = protected, deleted
        self.env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        self.env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never",
                        GIT_NO_REPLACE_OBJECTS="1", GIT_ATTR_NOSYSTEM="1")
        self.configs = ["gc.auto=0", "maintenance.auto=false", "core.compression=0",
                        "core.hooksPath=" + str(self.run / "no-hooks"),
                        "core.attributesFile=" + os.devnull, "core.fsmonitor=false"]
        self.source_config = {}

    def git(self, *args, live=False, data=None, stdin=None, allowed=(0,)):
        if live:
            require(args[0] in ("rev-parse", "ls-files", "config", "cat-file", "merge-base"),
                    "Live Git command is not read-only")
        env = dict(self.env)
        repo = self.live if live else self.bare
        if not live:
            require(self.index.is_absolute() and self.index.parent == self.bare, "Private index escaped capture")
            env["GIT_INDEX_FILE"] = str(self.index)
        command = [GIT, "--no-optional-locks", "--git-dir=" + str(repo), "--work-tree=" + str(self.root)]
        if args and args[0] == "hash-object":
            # Read clean attributes from the verified baseline object, never a
            # concurrently rewritten working-tree attributes file.
            command.append("--attr-source=" + self.baseline)
        for config in self.configs:
            command += ["-c", config]
        result = subprocess.run(command + list(args), cwd=self.root, env=env, input=data,
                                stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        require(result.returncode in allowed, "Git failed: " + " ".join(args[:3]) + "\n"
                + result.stderr.decode("utf-8", "replace")[-2000:])
        return result.stdout

    def tree(self, value):
        result = {}
        for row in self.git("ls-tree", "-r", "-z", value).split(b"\0"):
            if row:
                meta, path = row.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                name = safe_path(path.decode("utf-8"))
                require(kind == "blob" and mode in ("100644", "100755", "120000"),
                        "Submodule or unsupported tree entry needs explicit review: " + name)
                result[name] = {"mode": mode, "oid": oid}
        return result

    def live_index(self):
        entries = {}
        for row in self.git("ls-files", "--stage", "-z", live=True).split(b"\0"):
            if row:
                info, path = row.split(b"\t", 1)
                mode, oid, stage = info.decode().split()
                name = safe_path(path.decode("utf-8"))
                require(stage == "0" and mode in ("100644", "100755", "120000") and oid != ZERO,
                        "Unmerged or unsupported live index entry: " + name)
                entries[name] = {"mode": mode, "oid": oid}
        return entries

    def inventory(self):
        index = self.live_index()
        nonignored = {safe_path(p.decode("utf-8")) for p in self.git(
            "ls-files", "--others", "--exclude-standard", "-z", live=True).split(b"\0") if p}
        ignored = {safe_path(p.decode("utf-8")) for p in self.git(
            "ls-files", "--others", "--ignored", "--exclude-standard", "-z", live=True).split(b"\0") if p}
        review = self.audit["ignored_review"]
        require(fingerprint(sorted(ignored)) == review["ignored_paths_sha256"],
                "Ignored inventory differs from the explicitly reviewed list")
        includes = {safe_path(r["path"]): r for r in review["include"]}
        excludes = {safe_path(r["path"]): r for r in review["exclude"]}
        require(len(includes) == len(review["include"]) and len(excludes) == len(review["exclude"])
                and not includes.keys() & excludes.keys() and includes.keys() | excludes.keys() == ignored,
                "Every ignored file needs exactly one explicit inclusion or exclusion")
        require(all(bool(r.get("reason")) for r in [*includes.values(), *excludes.values()]),
                "Ignored-file decisions need review reasons")
        selected = set(self.baseline_entries) | set(index) | nonignored | set(includes)
        require(not self.deleted & selected, "An approved deleted screenshot reappeared in capture inputs")
        for path in self.deleted:
            require(not os.path.lexists(self.root / path), "Approved screenshot exists on disk: " + path)
        for path in selected:
            require(os.path.lexists(source_path(self.root, path)), "Deletion is not permitted: " + path)
        return {"live_index": index, "nonignored_untracked": sorted(nonignored),
                "ignored": sorted(ignored), "selected": sorted(selected)}, includes

    def check_attributes(self, selected):
        expected = {p: entry for p, entry in self.baseline_entries.items()
                    if PurePosixPath(p).name == ".gitattributes"}
        candidates = set(expected)
        for path in selected:
            parent = PurePosixPath(path).parent
            while True:
                candidates.add(str(parent / ".gitattributes"))
                if str(parent) == ".":
                    break
                parent = parent.parent
        for name in sorted(candidates):
            path = self.root / name
            if name not in expected:
                require(not os.path.lexists(path), "Unknown .gitattributes file: " + name)
            else:
                source = stable_source(self.root, name)
                require(not source["symlink"] and source["raw_blob"] == expected[name]["oid"],
                        "Unknown .gitattributes edit: " + name)
        for path in (self.live / "info/attributes",):
            require(not path.exists() or path.stat().st_size == 0, "Unreviewed live info/attributes rules")
        return expected

    def attributes(self, paths):
        names = sorted(paths)
        if not names:
            return {}
        data = b"".join(name.encode() + b"\0" for name in names)
        raw = self.git("check-attr", "--cached", "-z", "--stdin",
                       "filter", "working-tree-encoding", "text", data=data).split(b"\0")
        require(raw[-1] == b"" and (len(raw) - 1) % 3 == 0, "Malformed attribute results")
        result = {name: {} for name in names}
        for offset in range(0, len(raw) - 1, 3):
            path, key, value = [x.decode("utf-8") for x in raw[offset:offset + 3]]
            require(path in result and key not in result[path], "Unexpected attribute path/key")
            result[path][key] = value
        require(all(len(v) == 3 for v in result.values()), "Incomplete attribute results")
        return result

    def initialize(self):
        for path in (self.root, self.live, self.live / "objects", self.run.parent):
            no_link(path, directory=True)
        require(not self.run.exists(), "Each capture needs a fresh isolated run directory")
        require(not (self.live / "objects/info/alternates").exists(), "Live repository has unexpected alternates")
        self.run.mkdir()
        self.spools.mkdir()
        subprocess.run([GIT, "-c", "core.hooksPath=" + str(self.run / "no-hooks"), "init", "--bare", str(self.bare)],
                       cwd=self.run, env=self.env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with (self.bare / "objects/info/alternates").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write((self.live / "objects").as_posix() + "\n")
        # --work-tree is supplied for read-only source attribute discovery, so
        # rev-parse --is-bare-repository reports false for that command context.
        # Verify the persisted repository setting and actual common directory.
        require(self.git("config", "--bool", "core.bare").strip() == b"true", "Capture repository is not bare")
        require(Path(self.git("rev-parse", "--git-common-dir").decode().strip()).resolve() == self.bare,
                "Capture common directory escaped its isolated repository")
        require(self.git("cat-file", "-t", self.baseline).strip() == b"commit", "Baseline must identify a commit")
        self.git("merge-base", "--is-ancestor", FIXED, self.baseline)
        self.baseline_tree = self.git("rev-parse", self.baseline + "^{tree}").decode().strip()
        require(self.baseline_tree == FIXED_TREE, "Baseline tree must equal the fixed uploaded snapshot")
        self.baseline_entries = self.tree(self.baseline)
        self.git("read-tree", self.baseline)  # Private index only; no checkout.
        self.head_before = self.git("rev-parse", "HEAD", live=True).decode().strip()
        for key in ("core.autocrlf", "core.eol", "core.safecrlf"):
            value = self.git("config", "--get", key, live=True, allowed=(0, 1)).decode().strip()
            self.source_config[key] = value
            if value:
                self.configs.append(key + "=" + value)
        for name, expected in self.protected.items():
            require(self.baseline_entries.get(name) == {"mode": expected["mode"], "oid": expected["oid"]},
                    "Protected image differs in baseline: " + name)
        require(not self.deleted & self.baseline_entries.keys(), "Deleted screenshots exist in baseline")

    def write_blob(self, data=None, spool=None, path=None):
        args = ["hash-object", "-w", "--stdin"]
        args += ["--path=" + path] if path else ["--no-filters"]
        if spool:
            with Path(spool).open("rb") as stream:
                oid = self.git(*args, stdin=stream).decode().strip()
        else:
            oid = self.git(*args, data=data).decode().strip()
        require(re.fullmatch(r"[0-9a-f]{40}", oid), "Invalid generated blob")
        return oid

    def lfs_object(self, name, source, spool):
        obj = source["source_sha256"]
        destination = self.bare / "lfs/objects" / obj[:2] / obj[2:4] / obj
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(spool, destination)  # Unique object name, no replacement.
        except FileExistsError:
            require(destination.stat().st_size == source["source_bytes"] and digest(destination) == obj,
                    "Conflicting independent LFS object")
        require(destination.stat().st_size == source["source_bytes"] and digest(destination) == obj,
                "Independent LFS bytes differ from captured source")
        pointer = LFS_HEADER + ("oid sha256:" + obj + "\nsize " + str(source["source_bytes"]) + "\n").encode()
        pointer_blob = self.write_blob(data=pointer)
        return {"path": name, "sha256": obj, "size": source["source_bytes"], "pointer_blob": pointer_blob,
                "storage_path": str(destination), "new": True, "source_verified": True}

    def run_capture(self):
        self.initialize()
        before, ignored_includes = self.inventory()
        for path in self.pinned:
            relative = Path(path).resolve().relative_to(self.root).as_posix()
            if PurePosixPath(relative).parts[0] != ".git":
                require(relative in before["selected"], "Portable source/audit evidence was excluded from migration: " + relative)
        attributes_entries = self.check_attributes(before["selected"])
        attrs = self.attributes(before["selected"])
        source_records, expected_tree, lfs_records, new_lfs_paths = {}, dict(self.baseline_entries), [], []
        changed = []
        started = now()
        atomic_json(self.run / "inventory-before.json", before)
        last_progress = time.monotonic()
        for number, name in enumerate(before["selected"], 1):
            source = stable_source(self.root, name)
            baseline = self.baseline_entries.get(name)
            index_entry = before["live_index"].get(name)
            mode = "120000" if source["symlink"] else (index_entry or baseline or {"mode": "100644"})["mode"]
            require(mode in ("100644", "100755", "120000")
                    and (mode == "120000") == source["symlink"], "Unexpected source mode: " + name)
            if name in ignored_includes:
                approved = ignored_includes[name]
                require((source["source_bytes"], source["source_sha256"]) == (approved["size"], approved["sha256"]),
                        "Approved ignored source changed: " + name)
            if name in self.protected:
                protected = self.protected[name]
                require((mode, source["raw_blob"], source["source_bytes"], source["source_sha256"])
                        == (protected["mode"], protected["oid"], protected["size"], protected["sha256"]),
                        "Protected original changed on disk: " + name)
            filters = attrs[name]
            require(filters["filter"] in ("unspecified", "unset", "lfs"), "Unreviewed custom clean filter: " + name)
            use_lfs = filters["filter"] == "lfs" or source["source_bytes"] > LIMIT
            if use_lfs:
                require(not source["symlink"] and filters["working-tree-encoding"] in ("unspecified", "unset"),
                        "LFS source has unsupported mode/encoding: " + name)
            existing_pointer = None
            if baseline and filters["filter"] == "lfs":
                pointer = self.git("cat-file", "blob", baseline["oid"])
                match = re.fullmatch(rb"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n", pointer)
                require(match is not None, "Existing LFS tree entry is not a canonical pointer: " + name)
                require(source["raw_blob"] != baseline["oid"], "LFS working file is an unsmudged placeholder: " + name)
                if source["source_sha256"] == match[1].decode() and source["source_bytes"] == int(match[2]):
                    cache = self.live / "lfs/objects" / source["source_sha256"][:2] / source["source_sha256"][2:4] / source["source_sha256"]
                    no_link(cache)
                    require(cache.stat().st_size == source["source_bytes"] and digest(cache) == source["source_sha256"],
                            "Existing verified LFS cache is missing/corrupt: " + name)
                    destination = self.bare / "lfs/objects" / source["source_sha256"][:2] / source["source_sha256"][2:4] / source["source_sha256"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        os.link(cache, destination)
                    except FileExistsError:
                        pass
                    require(destination.stat().st_size == source["source_bytes"] and digest(destination) == source["source_sha256"],
                            "Independent existing LFS cache failed verification")
                    existing_pointer = {"path": name, "sha256": source["source_sha256"], "size": source["source_bytes"],
                                        "pointer_blob": baseline["oid"], "storage_path": str(destination),
                                        "new": False, "source_verified": True}
            if existing_pointer:
                oid = baseline["oid"]
                lfs_records.append(existing_pointer)
            elif baseline and source["raw_blob"] == baseline["oid"] and not use_lfs:
                oid = baseline["oid"]  # No subprocess or spool for an unchanged ordinary file.
            else:
                spool = self.spools / (uuid.uuid4().hex + ".source")
                copied = stable_source(self.root, name, spool)
                require(same_source(source, copied), "Source changed before capture spool: " + name)
                if use_lfs:
                    if source["source_bytes"] <= 256:
                        require(re.fullmatch(rb"version https://git-lfs.github.com/spec/v1\noid sha256:[0-9a-f]{64}\nsize [0-9]+\n",
                                             spool.read_bytes()) is None,
                                "LFS source is pointer text, not hydrated artwork: " + name)
                    item = self.lfs_object(name, source, spool)
                    oid = item["pointer_blob"]
                    lfs_records.append(item)
                    if filters["filter"] != "lfs":
                        new_lfs_paths.append(name)
                else:
                    # Standard clean text/eol/ident handling cannot expand source bytes;
                    # arbitrary filters and working-tree encodings require separate review.
                    require(filters["working-tree-encoding"] in ("unspecified", "unset"),
                            "Changed working-tree-encoding source requires explicit review: " + name)
                    require(source["source_bytes"] <= LIMIT, "Oversized source must go directly to LFS")
                    oid = self.write_blob(spool=spool, path=None if source["symlink"] else name)
                spool.unlink()  # Only our exclusive, task-owned spool; LFS hardlink survives.
            expected_tree[name] = {"mode": mode, "oid": oid}
            if baseline != expected_tree[name]:
                changed.append(name)
            source_records[name] = {"path": name, **source, "mode": mode, "oid": oid,
                                    "kind": "lfs_pointer" if use_lfs else "git_blob"}
            if time.monotonic() - last_progress >= 20:
                print(json.dumps({"phase": "stable_capture", "processed": number, "total": len(before["selected"])}), flush=True)
                last_progress = time.monotonic()
        attrs_source = self.git("cat-file", "blob", self.baseline_entries[".gitattributes"]["oid"]) if ".gitattributes" in self.baseline_entries else b""
        generated_attrs = attrs_source
        if new_lfs_paths:
            if generated_attrs and not generated_attrs.endswith(b"\n"):
                generated_attrs += b"\n"
            for name in sorted(new_lfs_paths):
                require(not any(c in name for c in "*?[]!\\"), "LFS exact pattern needs an explicit escaping review: " + name)
                # Root-leading slash anchors the pattern; JSON quoting is Git-compatible
                # for spaces and non-ASCII UTF-8 (controls/backslashes already forbidden).
                pattern = json.dumps("/" + name, ensure_ascii=False)
                generated_attrs += (pattern + " filter=lfs diff=lfs merge=lfs -text\n").encode("utf-8")
            attrs_oid = self.write_blob(data=generated_attrs)
            expected_tree[".gitattributes"] = {
                "mode": self.baseline_entries.get(".gitattributes", {}).get("mode", "100644"), "oid": attrs_oid}
            if ".gitattributes" not in changed:
                changed.append(".gitattributes")
        payload = b"".join((item["mode"] + " " + item["oid"] + "\t" + name).encode("utf-8") + b"\0"
                           for name, item in sorted(expected_tree.items()) if self.baseline_entries.get(name) != item)
        if payload:
            self.git("update-index", "--add", "-z", "--index-info", data=payload)
        target_tree = self.git("write-tree").decode().strip()
        require(self.tree(target_tree) == expected_tree, "Full content tree differs from captured inputs")
        require(self.baseline_entries.keys() <= expected_tree.keys(), "Capture would delete baseline files")
        for name, expected in self.protected.items():
            require(expected_tree[name] == {"mode": expected["mode"], "oid": expected["oid"]}, "Protected tree OID/mode changed")
        require(not self.deleted & expected_tree.keys(), "Approved screenshots reintroduced")
        effective = self.attributes([item["path"] for item in lfs_records])
        for item in lfs_records:
            values = effective[item["path"]]
            require(values["filter"] == "lfs" and values["text"] == "unset"
                    and values["working-tree-encoding"] in ("unspecified", "unset"),
                    "Nested attributes override exact LFS rules: " + item["path"])
        # Check every final object size without reading whole blob bodies again.
        unique_oids = sorted({entry["oid"] for entry in expected_tree.values()})
        sizes = {}
        rows = self.git("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)",
                        data=("\n".join(unique_oids) + "\n").encode()).splitlines()
        require(len(rows) == len(unique_oids), "Incomplete final object size scan")
        for oid, row in zip(unique_oids, rows):
            parts = row.decode().split()
            require(len(parts) == 3 and parts[:2] == [oid, "blob"] and int(parts[2]) <= LIMIT,
                    "Missing or oversized final Git blob: " + oid)
            sizes[oid] = int(parts[2])
        atomic_json(self.run / "inventory-after.json", self.inventory()[0])
        require(self.inventory()[0] == before, "Capture membership/live index changed; freeze again")
        catchup = []
        last_progress = time.monotonic()
        for number, name in enumerate(before["selected"], 1):
            try:
                verified = stable_source(self.root, name)
                if not same_source(source_records[name], verified):
                    catchup.append(name)
            except (OSError, RuntimeError):
                catchup.append(name)
            if time.monotonic() - last_progress >= 20:
                print(json.dumps({"phase": "full_content_recheck", "processed": number, "total": len(before["selected"])}), flush=True)
                last_progress = time.monotonic()
        atomic_json(self.run / "catchup.json", {"count": len(catchup), "paths": catchup})
        require(not catchup, "Frozen sources changed; catchup must be zero")
        require(self.inventory()[0] == before, "Final membership/live index changed; freeze again")
        self.check_attributes(before["selected"])
        require(self.git("rev-parse", "HEAD", live=True).decode().strip() == self.head_before, "Live HEAD changed during capture")
        for path, expected in self.pinned.items():
            require(digest(path) == expected, "Pinned freeze/protection evidence changed: " + path)
        for key, expected in self.source_config.items():
            # Explicitly reset our per-command override for the readback.
            configs = self.configs
            self.configs = [v for v in configs if not v.startswith(key + "=")]
            try:
                actual = self.git("config", "--get", key, live=True, allowed=(0, 1)).decode().strip()
            finally:
                self.configs = configs
            require(actual == expected, "Source Git text configuration changed")
        if new_lfs_paths:
            overlay = source_records.setdefault(".gitattributes", {"path": ".gitattributes", "source_absent": True})
            if overlay.get("source_absent"):
                overlay.update(source_sha256=hashlib.sha256(generated_attrs).hexdigest(),
                               source_bytes=len(generated_attrs), source_kind="generated_in_memory")
            overlay.update(kind="generated_attributes_overlay", mode=expected_tree[".gitattributes"]["mode"],
                oid=expected_tree[".gitattributes"]["oid"], content_sha256=hashlib.sha256(generated_attrs).hexdigest(),
                source_unchanged_on_disk=True, exact_new_lfs_paths=sorted(new_lfs_paths))
        manifest = self.run / "captured-files.jsonl"
        with manifest.open("x", encoding="utf-8", newline="\n") as stream:
            for name, item in sorted(source_records.items()):
                item["git_bytes"] = sizes[item["oid"]]
                stream.write(json.dumps(item, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.git("update-ref", "refs/codex/frozen-content-tree", target_tree, ZERO)
        report = {"schema_version": 1, "passed": True, "repository": str(self.root), "isolated_git_dir": str(self.bare),
            "baseline_commit": self.baseline, "baseline_tree": self.baseline_tree,
            "target_commit": None, "target_tree": target_tree, "content_ref": "refs/codex/frozen-content-tree",
            "freeze_audit_file": self.audit["_audit_path"], "freeze_audit_sha256": self.audit["_audit_sha256"],
            "manifest_file": str(manifest), "manifest_sha256": digest(manifest), "manifest_count": len(source_records),
            "target_path_count": len(expected_tree), "changed_paths": sorted(changed), "new_lfs_paths": sorted(new_lfs_paths),
            "lfs_objects": lfs_records, "protected_evidence_sha256": self.pinned,
            "all_lfs_pointer_entries_verified": True, "all_lfs_storage_within_capture_repo": True,
            "protected_image_count": len(self.protected), "authorized_screenshots_absent": len(self.deleted),
            "catchup_path_count": 0, "deleted_paths": [], "inventory_before_sha256": digest(self.run / "inventory-before.json"),
            "inventory_after_sha256": digest(self.run / "inventory-after.json"), "started_utc": started, "completed_utc": now(),
            "live_head_observed": self.head_before, "live_git_written": False, "working_files_written": False,
            "pushed": False, "publication_complete": False, "git_text_config": self.source_config,
            "publication_contract": "Content candidate only. A later publisher must verify completed remote P and construct new commits based on P. Do not attach unfinished raw history or overwrite remote history.",
            "freeze_limitation": "All named producers and other writers must remain frozen through capture. Two full content reads and final membership checks verify the observed interval; this is not an atomic filesystem snapshot."}
        atomic_json(self.run / "capture-report.json", report)
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("capture",))
    parser.add_argument("--freeze-evidence", type=Path)
    parser.add_argument("--freeze-sha256")
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    require(args.freeze_evidence is not None, "Explicit freeze evidence is required")
    require(Path(__file__).resolve().parent == WORK.resolve(), "Production script must stay in the audited new directory")
    audit, frozen_evidence = read_freeze(args.freeze_evidence, args.freeze_sha256)
    protected, deleted, pinned = protection_contract()
    pinned.update(frozen_evidence)
    baseline = audit["baseline_commit"]
    require(re.fullmatch(r"[0-9a-f]{40}", baseline), "Baseline must be a full commit SHA")
    if baseline != FIXED:
        item = audit["baseline_publication_evidence"]
        path = evidence_file(ROOT, item)
        receipt = load(path)
        require(receipt.get("server_confirmed") is True and receipt.get("exact_target_tree") is True
                and receipt.get("commit") == baseline and receipt.get("tree") == FIXED_TREE
                and receipt.get("target_report_sha256") == FIXED_REPORT_SHA
                and FIXED in receipt.get("parents", []), "Baseline is not the verified same-tree publication P")
        pinned[str(path)] = item["sha256"]
    audit.update(_audit_path=str(args.freeze_evidence.resolve()), _audit_sha256=args.freeze_sha256)
    runs = WORK / "runs"
    runs.mkdir(exist_ok=True)
    no_link(runs, directory=True)
    run = runs / uuid.uuid4().hex
    capture = Capture(ROOT, run, baseline, audit, pinned, protected, deleted)
    try:
        report = capture.run_capture()
        print(json.dumps({"passed": True, "report": str(run / "capture-report.json"),
                          "tree": report["target_tree"], "new_lfs_objects": len(report["new_lfs_paths"]),
                          "publication_complete": False}), flush=True)
    except BaseException as error:
        if run.is_dir():
            atomic_json(run / "capture-failed.json", {"passed": False, "error": str(error), "failed_utc": now(),
                "freeze_audit_sha256": args.freeze_sha256, "live_git_written": False,
                "working_files_written": False, "pushed": False})
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Frozen capture refused or stopped: " + str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
