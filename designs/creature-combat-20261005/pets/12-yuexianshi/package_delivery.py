"""Package final assets and provenance; excludes discarded pixels and cleanup utilities."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "yuexianshi-combat-delivery.zip"
FILES = [
    "README.md", "STATUS.md", "MERGE_HANDOFF.md", "POSES.md", "TASK.md",
    "manifest.json", "SHA256SUMS", "technical-validation.json",
    "delivery-verification.json", "cleanup.json", "preview.html",
    "build_delivery.py", "build_animations.py", "verify_delivery.py",
    "audit_sequence_continuity.py", "VERIFICATION.md",
    "verify_guard_repairs.py",
]

def main():
    verification = json.loads((ROOT / "delivery-verification.json").read_text(encoding="utf-8"))
    assert verification["status"] == "technical-passed-playback-pending"
    sources = [ROOT / name for name in FILES]
    for folder in ("runtime", "preview", "records", "prompts"):
        sources.extend(path for path in (ROOT / folder).rglob("*") if path.is_file())
    sources.extend((ROOT / "repair-inputs").glob("*.input.json"))
    if (ROOT / "cleanup-guardfix.json").exists():
        sources.append(ROOT / "cleanup-guardfix.json")
    sources = sorted(set(sources))
    members = []
    for path in sources:
        assert path.is_file() and path.resolve().is_relative_to(ROOT.resolve())
        members.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for member in members:
            archive.write(ROOT / member["path"], member["path"])
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {member["path"] for member in members}
        for member in members:
            assert hashlib.sha256(archive.read(member["path"])).hexdigest() == member["sha256"]
    result = {"createdAt": datetime.now(timezone.utc).isoformat(), "file": ARCHIVE.name,
              "sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(), "bytes": ARCHIVE.stat().st_size,
              "fileCount": len(members), "archiveAndMemberHashes": "passed", "members": members,
              "acceptanceStatus": verification.get("acceptanceStatus"), "staticReviewStatus": verification.get("staticReviewStatus"),
              "playbackStatus": verification["playbackStatus"], "clientStatus": verification["clientStatus"]}
    (ROOT / "delivery-package.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "members"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
