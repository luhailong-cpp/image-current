from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p): return {"path":p.as_posix(),"sha256":sha(p),"bytes":p.stat().st_size}
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
selected=["r06_c04_s01_01_a01","r06_c04_s01_02_a03","r06_c04_s01_03_a02","r06_c04_s01_04_a01","r06_c04_s02_01_a01"]
rejected=["r06_c04_s01_02_a01","r06_c04_s01_02_a02"]
natives=[]
for stem in selected+rejected:
    p=Z/"native"/(stem+".png"); gp=p.with_suffix(".png.generation.json")
    gen=read(gp); rp=Z/"receipts"/(stem+".receipt.json"); receipt=read(rp)
    source=Path(gen["sourceOutputPath"])
    assert source.is_file() and sha(source)==sha(p)==gen["sha256"]==gen["sourceOutputSha256"]
    assert gen["actualModel"] is None and gen["actualQuality"] is None
    assert gen["route"]=="builtin" and gen["resizedAfterGeneration"] is False
    assert [gen["nativeWidth"],gen["nativeHeight"]]==[1254,1254]
    assert Path(receipt["generatedFile"]).resolve()==source.resolve()
    paths=[p,gp,rp,Z/"prompts"/(stem+".prompt.txt"),Z/"guides"/(stem+".input.json"),Z/"guides"/(stem+".references.json")]
    assert all(x.is_file() for x in paths)
    natives.append({"stem":stem,"selection":"provisional_selected_pending_QA" if stem in selected else "rejected_geometry_retained","files":[rec(x) for x in paths],"rawGeneratedOriginal":rec(source),"sourceAndArchivedNativeBytesIdentical":True})
inventory=[]
for directory in ("native","guides","prompts","receipts"):
    inventory.extend(rec(p) for p in sorted((Z/directory).glob("r06_c04*")) if p.is_file())
helper=Z/"prepare_r06_c04_v4_top.py"
anchor=Z/"guides/r06_c04_r05c04_v4_top_anchors.json"
assert sha(anchor)=="ebad91b6e8ea11564cf911ecad249ac3155a2f88f758be73b8ed120d178e65a0"
left=[]
for stem in ["r06_c03_s01_04_a01","r06_c03_s02_04_a02"]:
    left.append({"stem":stem,"native":rec(Z/"native"/(stem+".png")),"generation":rec(Z/"native"/(stem+".png.generation.json")),"input":rec(Z/"guides"/(stem+".input.json"))})
missing=[f"s{r:02d}_{c:02d}" for r in range(1,5) for c in range(1,5) if (r,c) not in [(1,1),(1,2),(1,3),(1,4),(2,1)]]
obj={
"schemaVersion":1,"frozenAtUtc":datetime.now(timezone.utc).isoformat(),"agent":"/root/right_completion","reason":"User migration freeze relayed by parent /root: no new generation, repair, expansion, art composition, Git or progress writes; only save returned output and handoff.",
"status":"frozen_incomplete_do_not_resume_without_new_authorization",
"inflightCount":0,"unarchivedUniqueOutputCount":0,"requestReconciliation":{"basis":"All seven locally issued r06_c04 image_gen requests have completed tool returns; each output raw hash equals archived native and complete receipt/generation/prompt/input records. No request was started for prepared s02c2.","completedRequestCount":7,"successfullyArchivedRequestCount":7,"pendingExecCellIds":[],"allOriginalGeneratedOutputsPreserved":True},
"activeTile":"r06_c04","provisionalSelected":selected,"rejectedRetained":rejected,"missingNativeSlots":missing,"selectedCount":5,"requiredCount":16,
"nativeOutputs":natives,
"breakpoint":{"latestCompleted":"r06_c04_s02_01_a01 receipt and native ingested","nextPreparedOnly":"r06_c04_s02_02_a01","nextHasGuideAndReferences":True,"nextHasPrompt":(Z/"prompts/r06_c04_s02_02_a01.prompt.txt").exists(),"nextHasGeneratedNative":(Z/"native/r06_c04_s02_02_a01.png").exists(),"unusedPreparedGuideVersions":["r06_c04_s01_03_a01 (left a02 subsequently rejected)"],"assemblyCreated":False,"internal33QA":"not begun; no complete 4096 tile","freezeDoesNotMeanCompleted":True},
"knownDefectsAndPendingWork":[
"s1c1 uses too shallow a stone rail slope relative to the north fixed rail; s1c2 a03 restored upper-right match to r05c04 north anchor but west span still needs final geometric review.",
"s1c2 a01 and a02 rejected because rail right end too low; retained as provenance only.",
"s1c2 a03 has unintended blind-ending lower rail near local x390,y1050 and red paper additions; requires actual local repair after future authorization.",
"s1c3 a02 top rail matches fixed north source; lower wall foot at left shifted roughly 140px vs s1c2 a03, must repair joint.",
"s2c1 a01 currently has obvious stepped/rectangular rail transitions near local x230, y350 and y620. Candidate is not accepted; requires rail geometry repair. Do not propagate stepped geometry as final.",
"First two rows stone spans need consistent straight rails or valid column nodes; no unposted bends, duplicate rails, or hiding conflict by blur.",
"Finish 11 missing native slots, exact 4x4 assembly, all33 native internal QA, targeted native repairs and complete boundary provenance only after explicit resumption authorization."
],
"northAnchor":{"proof":rec(anchor),"helper":rec(helper),"kind":"verifiedTileCoreWithOriginalNativeHalo","notRawGeneration":True,"latestCoreSource":rec(Z/"tiles/r05_c04_candidate-v4_4096.png"),"latestCoreRecord":rec(Z/"tiles/r05_c04_candidate-v4_4096.native-repair.json"),"method":"Strict reconstruct_padded replay; current 4096 core plus original 4326 padded halo. Four exact1254 crops at padded[(c-1)*1024,3072,(c-1)*1024+1254,4326]; guide top uses each source crop[0,1024,1254,1254].","southChangedPixels":529,"southChangedXHalfOpen":[954,1483],"boundaryPriority":"current fixed r05_c04 v4 north edge, not old raw core"},
"leftAnchors":left,
"externalDependencies":[
"Parent /root owns r06_c03, supplied s01c4a01 and s02c4a02; r3/r4 left anchors must be explicitly confirmed on resumption.",
"Parent agreed prioritize fixed north boundary and may adjust own r06c03 rail endpoint when actual target coordinates are delivered; exact final coordinates not yet established.",
"/root/connected_closure owns r04/r05 connected group and final cross-tile seam repairs. My 8 horizontal native crops reviewed: first7 pass, x7168-8192 thickblindjoint defects delegated to it.",
"Independent audit of this derived north anchor proof was requested of connected_closure; result pending at freeze."
],
"previousCompletedTile":{"tile":"r05_c04","image":rec(Z/"tiles/r05_c04_candidate-v4_4096.png"),"provenance":rec(Z/"tiles/r05_c04_candidate-v4_4096.native-repair.json"),"QA":rec(Z/"qa/r05_c04_v4_internal_closure/visual_review.json"),"status":"internal33QA passed previously; external connected closure separately owned"},
"allR06FilesInventory":inventory,
"previewsPreserved":[rec(p) for p in sorted((Z/"guides").glob("r06_c04*NOT_FOR_ART.png"))],
"operations":{"newImagesAfterFreeze":0,"newArtCompositionAfterFreeze":0,"gitUsed":False,"progressModified":False,"actualModel":None,"actualQuality":None}
}
out=Z/"qa/right-migration-freeze-20261011.json"
assert not out.exists(),"Freeze record exists; inspect rather than overwrite."
out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"path":out.as_posix(),"sha256":sha(out),"inflightCount":0,"unarchivedUniqueOutputCount":0,"nativeOutputCount":len(natives),"selectedCount":len(selected),"missingCount":len(missing),"inventoryFiles":len(inventory)},ensure_ascii=False))

