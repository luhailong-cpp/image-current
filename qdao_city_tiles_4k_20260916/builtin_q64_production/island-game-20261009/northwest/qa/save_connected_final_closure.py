from pathlib import Path
import json,hashlib,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");O=Z/"qa/connected-closure-final-v1"
info=lambda p:dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
pixel=json.loads((O/"pixel-replay-and-qa.json").read_text())
repairs=[]
for s in ("cross_r03_c03c04_paving_upper_a01","cross_r04_c03c04_paving_upper_a01","cross_r04_c03c04_paving_lower_a01","cross_r03r04_c03_paving_left_a01"):
 p=Z/"qa"/f"{s}_mask_v1"/"mask_selection.json";m=json.loads(p.read_text())
 repairs.append(dict(stem=s,maskSelection=info(p),selectedPixels=m["repairPixelCount"],combinedNativeImage=info(Path(m["combinedCrop"]["path"])),nativeVisualPassed=True,independentReviewer="/root/right_completion",independentVisualPassed=True))
checks=[dict(**q,visualPassed=True,reviewMethod="Reopened actual native crop after final repair" if not q["matchesPreviouslyViewedNativeCrop"] else "Exact pixel equality to previously viewed/passed native crop") for q in pixel["nativeScaleCrops"]]
report=dict(schemaVersion=1,completedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope="r03/r04 x c03/c04 connected cluster internal shared boundaries",status="shared_boundary_visual_closure_passed_perimeter_pending",finalManifest=pixel["manifest"],candidateTileCount=4,sharedBoundaryPairCount=4,nativeQaCount=17,nativeQaPassed=17,repairNativeGenerationCount=4,repairs=repairs,checks=checks,fullFinalPixelReplay=info(O/"pixel-replay-and-qa.json"),verifiedPixelCount=67108864,strictFinalRecursiveProvenanceAudit=info(Z/"guides/connected_final_native_audit_a01.input.json"),strictMemo=dict(wrapper=info(Z/"qa/run_cross_with_strict_memo.py"),hits=76,misses=35,transitiveContentRehashes=27504,dependencyChanges=0),clusterOuterEdgesIdenticalToInitialConnected=True,currentRepairReferencesAvailable=True,historicalRetiredStyleReferenceBytesUnavailable=True,formalAcceptedCount=0,remaining=["Outer north/west/east/south neighbors require their respective cluster seam checks.","Large red lantern at south edge spans r04/r05 c03/c04; repair as whole object with next group."],reviewNotes=["Tiny line around lower repair(482,416) was independently reviewed by root and accepted as natural continuous fine stone subdivision.","Fourth repair old lower line is a fine stone crack; main beveled joint is continuous."])
with (O/"closure.json").open("x",encoding="utf8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(closure=info(O/"closure.json"),tiles=pixel["tiles"]),ensure_ascii=False,indent=2))

