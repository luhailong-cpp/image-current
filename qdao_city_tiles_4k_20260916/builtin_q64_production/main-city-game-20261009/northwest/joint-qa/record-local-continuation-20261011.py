from pathlib import Path
import json,datetime,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
z=p.ZONE
g=p.read(z/"progress.json")
first=z/"r06_c06/native/s01_02.png.generation.json"
r=p.read(first)
d=g["currentJointDelivery"]
summary=p.read(d["file"])
tilelist=[]
for t in g["tiles"]:
    if t["selectedUsable"]==16: continue
    missing=[]
    for row in range(1,5):
        for col in range(1,5):
            pid=f"s{row:02d}_{col:02d}"
            s=p.selected_path(z/t["tile"],pid)
            if not s.is_file():missing.append(pid)
    tilelist.append({"tile":t["tile"],"selectedUsable":t["selectedUsable"],"missingLogicalPatches":missing})
out={"updatedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"in_progress_network_restored_with_actual_output","wholeZoneComplete":False,"ownedTiles":60,"latestUserAuthorization":"User explicitly restored network permission via parent delegation; actual success below confirms usable tool route.","firstActualOutputAfterRestoration":{"tile":"r06_c06","id":"s01_02","file":r["file"],"sha256":r["sha256"],"hostOutputPath":r["evidence"]["hostOutputPath"],"generationRecord":{"file":str(first),"sha256":p.sha(first)},"tool":"image_gen.imagegen","route":"builtin","nativePixels":[1254,1254]},"mergedRealOutputs":summary["tiles"],"jointImage":summary["jointImage"],"delivery":d,"currentComplete4kCandidateCount":g["currentComplete4kCandidateCount"],"internalQAPassedCount":g["internalQAPassedCount"],"formalAcceptedCount":g["formalAcceptedCount"],"outerEdgesPending":{"first2x2PendingTileSides":8,"note":"Only the 2x2 internal shared edges were jointly accepted; all broader external closure remains pending."},"selectedUsableNativeCount":g["selectedUsableNativeCount"],"missingNativePatchCount":g["missingNativePatchCount"],"stillNeedsGeneration":tilelist,"blockers":["Remaining native pixels must still be generated","New candidates and neighboring boundaries require visual QA"],"runtimeWorkRequested":False,"nextStep":g.get("nextStep"),"gitAndMigration":{"ownerThread":"01a11b5e-158a-77d0-8c02-e8e503b7abe4","localGitMutations":False,"ownedAutomaticGitScripts":[],"instruction":"All git commits and uploads centralized; preserve all original, preview, receipt and working files. Do not touch .git/migration-sync-20261011."}}
p.write_json(z/"local-continuation-20261011.json",out,replace=True)
print(json.dumps({"file":str(z/"local-continuation-20261011.json"),"firstRecoveredSource":r["file"],"candidateCount":g["currentComplete4kCandidateCount"],"selectedNative":g["selectedUsableNativeCount"]}))

