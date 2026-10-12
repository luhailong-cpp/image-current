"""Save a factual continuation handoff without touching art or Git state."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from checkpoint_resume import atomic_json, read_json
snapshot, snapshot_sha = read_json(BASE / "pipeline-tools/live-counts-20261010.json")
counts = snapshot["recommendedProgressFieldsBeforeRepairIntegration"]
progress, _ = read_json(BASE / "progress.json")
now = datetime.now(timezone.utc).isoformat()
complete = [t["tile"] for t in snapshot["tiles"] if t["complete4kCandidate"]]
all_tiles = [f"r{r:02}_c{c:02}" for r in range(9,17) for c in range(1,9)]
partial = [{ "tile":t["tile"], "savedNativeCount":t["verifiedSelectedSpatialSlots"],
             "selectedIds":t["selectedIds"], "missingIds":t["missingIds"]}
           for t in snapshot["tiles"] if t["verifiedSelectedSpatialSlots"] and not t["complete4kCandidate"]]
handoff = {
    "updatedAtUtc":now, "scope":"southwest rows 9-16, columns 1-8; all 64 owned tiles",
    "finalCityComplete":False, "networkBlocked":False,
    "networkState":"User restored network authorization; five actual root builtin image returns recorded after restoration.",
    "networkRestorationEvidence":str(BASE / "network-restoration-20261011.json"),
    "countsSnapshot":str(BASE / "pipeline-tools/live-counts-20261010.json"),
    "countsSnapshotSha256":snapshot_sha, "countsSnapshotUtc":snapshot["snapshotCompletedAtUtc"],
    "counts":counts, "complete4kCandidateTiles":complete, "partialTiles":partial,
    "remainingTilesWithout4kCandidates":[t for t in all_tiles if t not in complete],
    "candidateCatalog":str(BASE / "current-candidates.json"),
    "latestIntegratedAssembly":str(BASE / "integrated-20261011/v2/assembly.json"),
    "latestIntegratedQa":str(BASE / "integrated-20261011/v2/qa-review.json"),
    "sharedBoundaryReview":{"passed":2,"pending":2,"allCrossEdgesPassed":False},
    "exteriorNeighborFullTilesMissing":["r09_c05","r09_c06","r10_c04","r11_c04","r12_c05","r12_c06","r10_c07","r11_c07"],
    "rootLastSavedNative":{"tile":"r12_c05","patch":"p01_03","receipt":str(BASE / "r12_c05/pipeline/receipts/p01_03.restored20261011-v03.receipt.json"),"formalAccepted":False,"textureReviewPending":True},
    "ongoingAssignments":[
        {"worker":"/root/resume_r11c06","task":"G01 stair-width salvage from saved native 07, bounded proposal; no direct integration"},
        {"worker":"/root/resume_r10c06","task":"North vertical shared-edge lower stair material splice, at most two targeted native edits"},
        {"worker":"/root/resume_crossedge_audit","task":"Local receipt/coverage audit; read only apart from its own report"}
    ],
    "nextSteps":["Review and integrate valid bounded repair proposals with unchanged pixels outside masks.",
                 "Continue r12_c05 remaining 13 spatial patches using exact native neighbor overlaps.",
                 "Review natural stone texture and all internal/external boundaries before formal acceptance.",
                 "Continue remaining southwest coordinates; this 4-tile sample is not the 64-tile delivery."],
    "gitHandoff":{"centralizedMigrationChat":"01a11b5e-158a-77d0-8c02-e8e503b7abe4",
                  "gitMutationsPerformedHere":False,"migrationDirectoryTouched":False,
                  "filesPreserved":True,"readyForCentralizedCollection":True},
    "paidApiUsed":False,"actualModel":None,"actualQuality":None,
    "noGenerationWasCountedFromPreparedRequests":True
}
atomic_json(BASE / "local-continuation-20261011.json", handoff)
progress.update({
    "updatedAtUtc":now,"activeTiles":complete + [p["tile"] for p in partial],
    "primaryNewTile":"r12_c05","primaryNewTileNativeCount":3,
    "nextStep":"Continue r12_c05 native coverage and bounded saved-candidate stair/material repairs; retain formal acceptance at zero pending full visual review.",
    "localContinuationHandoff":str(BASE / "local-continuation-20261011.json"),
    "networkBlocked":False,"allCrossEdgesPassed":False,
    "rootImageGenerationInFlight":False,
    "inFlightStatus":"production_and_bounded_repairs_in_progress"
})
progress["workerStatus"] = {
    "reportedAtUtc":now,"activeWorkers":["/root","/root/resume_r10c06","/root/resume_r11c06","/root/resume_crossedge_audit"],
    "activeGenerationTiles":["r12_c05"],"activeRepairTiles":["r10_c05","r10_c06","r11_c06"],
    "activeReviewWorkers":["/root/resume_crossedge_audit"],
    "supportActivities":"Root saved three r12_c05 spatial slots; two bounded repair assignments and one local audit remain active.",
    "individualWorkerGenerationInFlight":"Pending current worker reports; active assignment does not itself mean an image call is running."
}
atomic_json(BASE / "progress.json", progress)
print(json.dumps({"handoff":str(BASE / "local-continuation-20261011.json"),"fullCandidates":len(complete),"partialTiles":partial,"formalAccepted":0}, ensure_ascii=False, indent=2))
