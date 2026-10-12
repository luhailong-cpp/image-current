from pathlib import Path
import json,hashlib,sys,shutil
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mode=sys.argv[1]
if mode=="prepare":
    specs=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    template=json.loads((D/"p01_03-macro-rebuild-v01/request.json").read_text())
    result=[]
    for spec in specs:
        folder=D/spec["attempt"];folder.mkdir(exist_ok=False)
        target=Path(spec["target"])
        prompt=spec["prompt"]
        pf=folder/"prompt.txt";pf.write_text(prompt,encoding="utf-8")
        refs=[dict(x) for x in template["references"]];refs[0]={"file":str(target),"sha256":sha(target),"role":spec["targetRole"]}
        if spec.get("materialReference"):
            material=Path(spec["materialReference"]);refs[-1]={"file":str(material),"sha256":sha(material),"role":"previously visually approved quiet native stone pilot; material only"}
        guide=json.loads((B/"guides"/(spec["id"]+".layout-only.png.derivation.json")).read_text())
        coords={k:guide[k] for k in ["id","row","column","coreWorldBox","contextWorldBox","nativeCoreBox"]}
        req=dict(template);req.update(id=spec["id"],attempt=spec["attempt"],prompt=prompt,promptFile=str(pf),promptSha256=sha(pf),referenced_image_paths=[x["file"] for x in refs],references=refs,coordinates=coords,preparedAtUtc=datetime.now(timezone.utc).isoformat(),visualDisposition="prepared; no generation yet")
        (folder/"request.json").write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding="utf-8")
        result.append(req)
    print(json.dumps(result,ensure_ascii=False))
elif mode=="save":
    folder=D/sys.argv[2];src=Path(sys.argv[3]);assert src.is_file()
    req=json.loads((folder/"request.json").read_text())
    dst=folder/"native.png";assert not dst.exists()
    shutil.copy2(src,dst)
    im=Image.open(dst);assert im.size==(1254,1254)
    rec={"status":"returned_image","tool":"image_gen.imagegen","route":"builtin","sourceOutputPath":str(src),"sourceOutputSha256":sha(src),"savedNativePath":str(dst),"savedNativeSha256":sha(dst),"width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"actualModel":None,"actualQuality":None,"nativePixelsPreserved":True,"resizedAfterGeneration":False,"apiUsed":False,"savedAtUtc":datetime.now(timezone.utc).isoformat(),"request":str(folder/"request.json"),"requestSha256":sha(folder/"request.json"),"promptSha256":req["promptSha256"],"references":req["references"],"visualDisposition":"pending actual native visual QA"}
    (folder/"receipt.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(rec))

