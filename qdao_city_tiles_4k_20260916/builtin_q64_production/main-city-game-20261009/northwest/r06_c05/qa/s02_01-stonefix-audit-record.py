from pathlib import Path
import json,hashlib
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05")
pairs=json.loads((b/"qa/s02_01-stonefix-audit-evidence.json").read_text())
for p in pairs:p["actuallyViewed"]=True
r={"source":"native/s02_01_stonefix01.png","sourceSha256":"f426c5effaee03a7df3fab1ebd0e4ea8f28f85b42e46437978ed6bd33f660a7c","scope":"repair upper stone panel topology only; source and full four-boundary local QA","tool":"builtin image_gen","actualModel":None,"actualQuality":None,"nativePixels":[1254,1254],"worldBox":[16269,21389,17523,22643],"actuallyViewedNative":True,"pairs":pairs,"actualViewCount":5,"findings":{"north":"Dangling diagonal eliminated. Hard-cut rectangular ground and x905 vertical joint continuous; new chamfered horizontal course below boundary.","west":"Chamfered entry connects existing diagonal west source. Blue body/pale boundary coordinates preserved. Local pair shows minor material color/texture step; no broken major geometry.","east":"Road top/bottom, blue brick lines and diagonal ground join continuously.","south":"Tree leaves continue; minimum-error improves small hard-cut foliage shading transitions."},"roadBandActualApproxNativeY":[280,348,604,674],"upperCourseApproxNativeY":185,"status":"local_repair_and_pair_geometry_review_pass","notPixelIdenticalClaim":True,"fullTileAcceptance":False,"formalAccepted":False,"progressWritten":False}
(b/"qa/s02_01-stonefix-audit-report.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(b/"qa/s02_01-stonefix-audit-report.json")

