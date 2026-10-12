from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
from datetime import datetime,timezone
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest"); work=root/"work-r03_c04"; out=work/"paving-fresh"
sys.path.insert(0,str(work))
from apply_r03_c04_repairs import load_base,validate_native,verify_pixels,sha,overlay_mask
recordpath=work/"tiles/r03_c04.assembly.json"
pixels,ids,sources,arrays,base=load_base(recordpath)
nativepath=out/"r03_c04_paving_localshape_v01.png"; genpath=out/(nativepath.name+".generation.json")
info={"sourceId":max(s["sourceId"] for s in sources)+1,"file":str(nativepath),"sha256":sha(nativepath),"generationRecord":str(genpath),"generationRecordSha256":sha(genpath),"nativeBox":[350,420,1604,1674]}
native,info=validate_native(info,base["globalCoreBox"][:2])
before=pixels.copy(); region=pixels[420:1674,350:1604]
mask,paths=overlay_mask(region,native); region[mask]=native[mask];ids[420:1674,350:1604][mask]=info["sourceId"]
sources.append(info);arrays[info["sourceId"]]=native
counts=verify_pixels(pixels,ids,sources,arrays)
candidate=out/"r03_c04.paving-proposal-v1.png"; idfile=out/"r03_c04.paving-proposal-v1.source-id.png"; maskfile=out/"r03_c04.paving-proposal-v1.mask.png"
Image.fromarray(pixels).save(candidate);Image.fromarray(ids.astype(np.uint8)).save(idfile);Image.fromarray(mask.astype(np.uint8)*255).save(maskfile)
changed=np.any(pixels!=before,axis=2); assert not changed[:420].any() and not changed[1674:].any() and not changed[:,:350].any() and not changed[:,1604:].any()
crops=[]
boxes={"north":[318,388,1636,650],"south":[318,1444,1636,1706],"west":[318,388,600,1706],"east":[1374,388,1636,1706],
"defect1":[800,725,1140,1035],"defect2":[925,860,1255,1140],"defect3":[750,915,1130,1225],"defect4":[1050,1135,1400,1465]}
for name,box in boxes.items():
 p=out/f"qa-{name}.100pct.png";Image.fromarray(pixels).crop(box).save(p)
 crops.append({"name":name,"file":str(p),"sha256":sha(p),"tileBox":box,"scale":1})
manifest={"schemaVersion":1,"tile":"r03_c04","createdAt":datetime.now(timezone.utc).isoformat(),"status":"native-paving-repair-proposal-pending-four-edge-QA","formalAccepted":False,"candidate":{"file":str(candidate),"sha256":sha(candidate)},"sourceIdMap":{"file":str(idfile),"sha256":sha(idfile),"mode":"L","coordinateFormula":"sourceX=outputX-nativeBox[0]; sourceY=outputY-nativeBox[1]"},"globalCoreBox":base["globalCoreBox"],"outputSize":[4096,4096],"base":base,"sources":sources,"contributions":counts,"overlays":[{"sourceId":info["sourceId"],"nativeBox":info["nativeBox"],"maskFile":str(maskfile),"maskSha256":sha(maskfile),"selectedPixels":int(mask.sum()),**paths}],"composition":{"feather":False,"resample":False,"scale":False,"colorRewrite":False,"exactNativePixelOwnershipVerified":True,"pixelsVerified":16777216,"outsideActualContributionMaskUnchanged":True},"artifacts":[{"file":str(p),"sha256":sha(p)} for p in [candidate,idfile,maskfile]],"qaCrops":crops,"script":{"file":str(Path(__file__)),"sha256":sha(Path(__file__))},"clientValidated":False,"navigationValidated":False,"capacity5000Validated":False}
(out/"r03_c04.paving-proposal-v1.assembly.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"candidate":str(candidate),"sha256":sha(candidate),"selectedPixels":int(mask.sum()),"changedPixels":int(changed.sum()),"pixelsVerified":16777216,"newSourceId":info["sourceId"]}))

