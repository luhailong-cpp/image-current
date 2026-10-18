"""Root-run adoption only. This file has been prepared, not executed by its author.

Copies both verified native candidates into a new processed directory, preserves
the exact previous selection, and replaces the two source references together
in one atomic JSON replacement. All other patch references are preserved.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import shutil
import uuid

from verify_bracket_joint_replay_20261013 import Q, T, read, sha, verify_current


def new_json(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    destination = T / "processed/bracket-joint-20261013-v2"
    assert not destination.exists(), "Preserve existing versions; destination already exists"
    canonical = T / "selected-patches.json"
    # Repeats the independent raw/mask pixel replay against current canonical inputs.
    replay, before, selection = verify_current()
    before_sha = hashlib.sha256(before).hexdigest()
    reviewed = read(Q / "bracket-joint-v2.adoption-instructions.json")
    assert reviewed["adoptRecommended"] is True and reviewed["localGeometryPassed"] is True
    assert reviewed["canonicalModified"] is False
    recipe = read(Q / "bracket-joint-v2-proof.json")
    now = datetime.now(timezone.utc).isoformat()
    assert canonical.read_bytes() == before, "Selection changed; restart from fresh inputs"
    destination.mkdir(parents=True, exist_ok=False)
    backup = destination / "selection-before-bracket-joint-20261013-v2.json"
    with backup.open("xb") as f:
        f.write(before)
    assert sha(backup) == before_sha
    replay_path = destination / "adoption-time-independent-replay.json"
    new_json(replay_path, replay)
    adopted = []
    after = copy.deepcopy(selection)
    for item in recipe["candidates"]:
        source = Path(item["file"])
        output = destination / source.name
        assert not output.exists()
        shutil.copyfile(source, output)
        assert sha(output) == item["sha256"]
        after["patches"][item["patch"]] = output.relative_to(T).as_posix()
        adopted.append(dict(patch=item["patch"], file=str(output), sha256=sha(output),
                            original=item["original"], originalSha256=item["originalSha256"]))
    assert {a["patch"] for a in adopted} == {"p43", "p44"}
    for pid, old_entry in selection["patches"].items():
        if pid not in {"p43", "p44"}:
            assert after["patches"][pid] == old_entry
    pending = after.setdefault("pendingIssues", [])
    assert isinstance(pending, list), "Existing pendingIssues is not a list; review rather than replace it"
    added_pending = [
        dict(id="r09_c08-p44-window-duplicate-flower", status="pending",
             description="Window flower duplicates across r09_c08/r10_c08; two north-only attempts retained and rejected.",
             evidence=str(T / "qa/window-repair-20261013/final-review-20261013-v1.json")),
        dict(id="r09_c08-p43-p44-roof-fascia-color-seam", status="pending",
             description="Existing blue-roof and fascia tone seam remains outside the adopted bracket repair; whole-tile color and external checks pending.")]
    current_ids = {p.get("id") for p in pending if isinstance(p, dict)}
    for issue in added_pending:
        if issue["id"] not in current_ids:
            pending.append(issue)
    after.update(updatedAt=now, status="native_production_bracket_joint_adopted_other_QA_pending",
                 internalReady=False, formalAccepted=False, materialPending=True,
                 bracketJointAdoption=dict(localGeometryPassed=True, tilePassed=False,
                     adoptedAtUtc=now, directory=str(destination),
                     review=str(Q / "bracket-joint-v2.adoption-instructions.json"),
                     sourceProof=str(Q / "bracket-joint-v2-proof.json"),
                     adoptionReplay=str(replay_path), previousSelection=str(backup),
                     previousSelectionSha256=before_sha, actualModel=None, actualQuality=None))
    # Preserve but explicitly invalidate any stale assembled candidate field.
    if after.get("candidate"):
        after.setdefault("historicalCandidates", []).append(dict(candidate=after.pop("candidate"),
             candidateSha256=after.pop("candidateSha256", None), invalidatedAtUtc=now,
             reason="Selected p43/p44 changed; must reassemble from current cores"))
    pending_record = dict(preparedAtUtc=now, status="prepared_before_atomic_selection_update",
                          originalSelection=str(backup), originalSelectionSha256=before_sha,
                          adoptionTimeReplay=str(replay_path), adopted=adopted,
                          internalReady=False, formalAccepted=False, pendingIssues=pending,
                          otherTileImagesModified=False, originalImagesModified=False, gitOperations=False)
    new_json(destination / "adoption-prepared.json", pending_record)
    temp = T / ("selected-patches.bracket-joint-" + uuid.uuid4().hex + ".tmp.json")
    new_json(temp, after)
    # Abort without touching canonical if another producer changed the selection.
    assert canonical.read_bytes() == before, "Concurrent selection update detected; preserved staged files, canonical unchanged"
    os.replace(temp, canonical)
    installed = canonical.read_bytes()
    assert json.loads(installed.decode("utf-8-sig"))["patches"] == after["patches"]
    completed = dict(pending_record, status="both_sources_adopted_together",
                     completedAtUtc=datetime.now(timezone.utc).isoformat(),
                     newSelection=str(canonical), newSelectionSha256=hashlib.sha256(installed).hexdigest())
    new_json(destination / "adoption-completed.json", completed)
    print(json.dumps({"status": completed["status"], "destination": str(destination),
                      "selectionSha256": completed["newSelectionSha256"],
                      "adopted": adopted, "internalReady": False, "formalAccepted": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
