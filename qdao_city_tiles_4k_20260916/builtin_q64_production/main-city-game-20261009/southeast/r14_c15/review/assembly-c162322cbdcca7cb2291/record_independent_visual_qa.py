import json,hashlib,datetime
from pathlib import Path
q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15")
d=q/"review/assembly-c162322cbdcca7cb2291"
i=json.loads((d/"independent-qa-20261012/index.json").read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
failids={"v1024-q1","v1024-q2","h2048-q0","h2048-q1","j1024-2048"}
external={
"ext-north-q0":("failed","N01: the dark vertical floorboard end joint at x~230 terminates exactly at the fixed north-core boundary instead of continuing to the lower diagonal plank edge."),
"ext-north-q1":("pass_observed","Wood post/collar contours and deck lines cross the boundary without an observed hard break."),
"ext-north-q2":("pass_observed","Rail edges and plank grain cross boundary; no clear hard discontinuity observed."),
"ext-north-q3":("pass_observed","Wood rails, upright, and deck retain geometry across boundary."),
"ext-west-q0":("pass_observed","Wood platform corner, leg, stone joint, and shadow cross boundary without a clear hard break."),
"ext-west-q1":("failed","W01: stone grout at y~1090 starts abruptly at x=0; surrounding stone texture changes at the boundary."),
"ext-west-q2":("failed","W02: child-side stone joint at y~2278 turns/starts at the boundary without a matching continuation in the west core."),
"ext-west-q3":("failed","W03: west-side grout reaches x=0 around y~3515 and ends without a matching child continuation. Fine stone texture/tone also changes across sections.")
}
entries=[]
for e in i["evidence"]:
    z=dict(e); z["actuallyViewedAtOriginalPixelSize"]=True
    if e["id"] in external:z["status"],z["observation"]=external[e["id"]]
    elif e["id"] in failids:z.update(status="failed_structure",observation="I01 duplicated lower/front stone post and rail; seam rendering alone is insufficient. See full structure box and source chain.")
    elif e["id"].startswith("edge-"):z.update(status="pass_standalone_edge_only",observation="No intrinsic rendering break observed within this core-edge strip. This does not certify a join to an unviewed neighbor.")
    else:z.update(status="pass_observed",observation="No new hard seam, split outline, or duplicated object observed in this native-size evidence.")
    if e["id"]=="j2048-1024":z["observation"]="Specifically rechecked the small wooden-board concern near x2048/y1024: diagonal rail/board outlines are continuous; no actual hard breakpoint established."
    entries.append(z)
defect=[
dict(id="I01",kind="internal_structure",severity="blocking",boxInChildCore=[445,1930,1330,2780],transitionBox=[420,2620,1420,2880],coordinatePrecision="visual estimated bounding boxes",description="A second lower/front post and rail duplicate the existing upper/pool-side fence. Lower continuation and nearby foliage remain affected below the originally proposed crop bottom y2724.",sources=[{"path":str(q/"native/p03_01_v20261012T122703_8f086cf0.png"),"sha256":"27d18f7e1cbb549152841fb620ac83ce1b299d407ab297c45c2075fa012f9d5c"},{"path":str(q/"native/p03_02_v20261012T125122_6cf424b6.png"),"sha256":"c4ae035a7c2a3aeb4f53185b1932e2f3f156a45cb8aed36d85b85c0441cfd938"}],sourceReason="p03_01 redraws a lower rail beneath the native top anchor; p03_02 inherits that lower rail in its left anchor while its generated area follows the upper rail.",remediation="Keep the upper/pool-side rail; remove duplicate front post/rail and restore gray paving/attached foliage, then inspect all native-size patch boundaries."),
dict(id="N01",kind="north_core_join",severity="blocking",boxInChildRelativeCoordinates=[214,-70,252,90],suggestedChildRepairBox=[200,0,270,120],description="Vertical deck-board end joint at x~230 stops at y=0. Must continue only into the new child side until its true diagonal plank boundary, preserving north core.",neighbor=i["north"],evidence="ext-north-q0"),
dict(id="W01",kind="west_core_join",severity="blocking",boxInChildRelativeCoordinates=[-80,1050,150,1130],description="Child-side diagonal grout begins at x=0 around y1090 but west stone has no matching groove.",neighbor=i["west"],evidence="ext-west-q1"),
dict(id="W02",kind="west_core_join",severity="blocking",boxInChildRelativeCoordinates=[-80,2220,150,2360],description="Stone joint begins/turns at x=0 around y2278; opposing core continues a different slab layout.",neighbor=i["west"],evidence="ext-west-q2"),
dict(id="W03",kind="west_core_join",severity="blocking",boxInChildRelativeCoordinates=[-120,3450,170,3590],description="West-side grout ends at x=0 around y3515; child stone face does not continue it.",neighbor=i["west"],evidence="ext-west-q3"),
dict(id="W04",kind="west_core_material",severity="review_with_geometry_repair",boxInChildRelativeCoordinates=[-90,1024,100,4096],description="Several portions change fine stone texture/tone at the core boundary. Correct alongside actual native geometry; no RGB color correction authorized.",neighbor=i["west"],evidence=["ext-west-q1","ext-west-q2","ext-west-q3"])
]
out={"schemaVersion":1,"reviewer":"assembly_support","reviewedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"candidate":i["candidate"],"assembly":i["assembly"],"status":"failed_internal_structure_and_external_core_joins","formallyAccepted":False,"scope":{"internalFullLengthSeams":6,"internalSeamSegmentsActuallyViewed":24,"junctionsActuallyViewed":9,"standaloneEdgeSegmentsActuallyViewed":16,"externalCoreSegmentsActuallyViewed":8,"totalActuallyViewed":57,"resizedEvidence":False,"neighborHaloUsed":False,"eastSouthNeighborJoins":"not reviewed; no claim"},"evidenceIndex":{"path":str(d/"independent-qa-20261012/index.json"),"sha256":sha(d/"independent-qa-20261012/index.json")},"findings":defect,"evidence":entries,"repairTrials":"Separate evidence/review required; this report does not certify 6289 v2 or 3f0 v3.","candidateAndSelectionUnmodifiedByReviewer":True}
p=d/"visual-qa.json";p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"path":str(p),"sha256":sha(p),"viewed":len(entries)}))
