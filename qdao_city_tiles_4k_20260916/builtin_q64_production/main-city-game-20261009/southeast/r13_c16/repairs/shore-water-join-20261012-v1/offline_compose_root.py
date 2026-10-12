"""Offline preservation, native-only three-edge seam composition, and replay.
Usage: python -B offline_compose.py validate
       python -B offline_compose.py compose ORIGINAL_BUILTIN_PNG
All writes are confined to this repair directory. No network, selection, progress, or Git.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil,importlib.util
import numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
T=D.parent.parent
Z=T.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def info(p):
    p=Path(p); return {"path":str(p),"sha256":sha(p)}
def art(p):
    o=info(p)
    with Image.open(p) as im:o["pixels"]=list(im.size)
    return o
def write(p,value):
    with Path(p).open("x",encoding="utf-8") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")
def png(p,im):
    with Path(p).open("xb") as f:im.save(f,format="PNG")
def validate():
    m=read(D/"preparation.json");r=read(D/"request.json")
    for e in [m["sourceCandidate"],m["sourceContext"],m["sourceAssembly"],m["target"],m["markedTarget"],*m["references"]]:
        assert sha(e["path"])==e["sha256"],e["path"]
    assert r["referenced_image_paths"]==[x["path"] for x in m["references"]]
    assert m["nativeAdoptionCrop"]==[100,0,700,1254]
    assert m["pasteBoxIn4096"]==[760,0,1360,1254]
    base=np.array(Image.open(m["sourceCandidate"]["path"]).convert("RGB"))
    bx=m["cropBoxIn4096"]
    assert np.array_equal(base[bx[1]:bx[3],bx[0]:bx[2]],np.array(Image.open(m["target"]["path"]).convert("RGB")))
    assert np.array_equal(base,np.array(Image.open(m["sourceContext"]["path"]).convert("RGB"))[115:4211,115:4211])
    return m,r,base
def compose(original):
    m,r,base=validate();original=Path(original)
    with Image.open(original) as im:
        im.load();assert im.format=="PNG" and im.size==(1254,1254) and im.mode in ("RGB","RGBA")
        if im.mode=="RGBA":assert im.getextrema()[3]==(255,255)
    native=D/"repair-native-1254.png"
    if not native.exists():shutil.copyfile(original,native)
    assert sha(native)==sha(original)
    receipt=D/"receipt.json"
    if not receipt.exists():
        write(receipt,{"schemaVersion":1,"tool":"image_gen.imagegen","route":"builtin","status":"succeeded_pending_visual_review","dispatchingAgent":"/root","preservingAgent":"/root","sourceEvidence":"Root directly received the successful builtin output path.","savedAtUtc":datetime.now(timezone.utc).isoformat(),"generatedAtUtc":None,"timeMeaning":"savedAtUtc is preservation time only; no actual generation timestamp claimed","actualModel":None,"actualQuality":None,"original":info(original),"savedNative":art(native),"byteCopyVerified":True,"request":info(D/"request.json"),"preparation":info(D/"preparation.json"),"resampling":False})
    record=D/"repair-native-1254.png.generation.json"
    if not record.exists():
        write(record,{"schemaVersion":1,"id":D.name,"tile":T.name,"file":str(native),"sha256":sha(native),"width":1254,"height":1254,"format":"PNG","mode":Image.open(native).mode,"tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"originalOutputPath":str(original),"savedAtUtc":read(receipt)["savedAtUtc"],"generatedAtUtc":None,"receipt":info(receipt),"request":info(D/"request.json"),"preparation":info(D/"preparation.json"),"references":m["references"],"nativeAdoptionCrop":m["nativeAdoptionCrop"],"pasteBoxIn4096":m["pasteBoxIn4096"],"activeLogicalPatch":False,"resampling":False})
    crop=m["nativeAdoptionCrop"];box=m["pasteBoxIn4096"]
    old=base[box[1]:box[3],box[0]:box[2]].copy()
    new=np.array(Image.open(native).convert("RGB").crop(crop))
    h,w=old.shape[:2];assert (h,w)==(1254,600)
    algo_path=Z/"assemble_candidate.py"
    spec=importlib.util.spec_from_file_location("_shore_seam",algo_path)
    alg=importlib.util.module_from_spec(spec);spec.loader.exec_module(alg)
    b=64
    paths={
        "left":alg.minimum_vertical_seam(old[:,:b],new[:,:b]),
        "right":alg.minimum_vertical_seam(old[:,-b:],new[:,-b:]),
        "bottom":alg.minimum_vertical_seam(old[-b:].transpose(1,0,2),new[-b:].transpose(1,0,2))
    }
    a=np.full((h,w),255,np.uint8)
    a[:,:b]=np.where(np.arange(b)[None,:]>=paths["left"][:,None],255,0)
    a[:,-b:]=np.minimum(a[:,-b:],np.where(np.arange(b)[None,:]<paths["right"][:,None],255,0).astype(np.uint8))
    a[-b:]=np.minimum(a[-b:],np.where(np.arange(b)[:,None]<paths["bottom"][None,:],255,0).astype(np.uint8))
    a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(2)))
    a[-1]=0;a[:,[0,-1]]=0
    # No top seam or old top row preservation: the false vertical line reaches y=0.
    assert np.all(a[0,64:-64]==255)
    ap=D/"alpha.png";sp=D/"seam-paths.npz"
    if not ap.exists():png(ap,Image.fromarray(a))
    else:assert np.array_equal(a,np.array(Image.open(ap)))
    if not sp.exists():
        with sp.open("xb") as f:np.savez_compressed(f,**paths)
    mixed=((old.astype(np.uint32)*(255-a[:,:,None])+new.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
    result=base.copy();result[box[1]:box[3],box[0]:box[2]]=mixed
    candidate=D/"candidate-4096.png";context=D/"context-4326.png"
    png(candidate,Image.fromarray(result))
    ctx=np.array(Image.open(m["sourceContext"]["path"]).convert("RGB"));ctx[115:4211,115:4211]=result;png(context,Image.fromarray(ctx))
    local=D/"composed-local-1254.png";png(local,Image.fromarray(result).crop(m["cropBoxIn4096"]))
    rects={
        "top-core-edge-100pct":[760,0,1360,320],
        "bottom-boundary-100pct":[760,998,1360,1510],
        "left-boundary-100pct":[504,0,1016,1254],
        "right-boundary-100pct":[1104,0,1616,1254],
        "former-vertical-discontinuity-100pct":[917,0,1429,1254],
        "junction-x1024-y1024-100pct":[574,574,1474,1474],
        "v1024-q0-100pct":[768,0,1280,1024],
        "v1024-q1-100pct":[768,1024,1280,2048],
        "h1024-q0-100pct":[0,768,1024,1280],
        "h1024-q1-100pct":[1024,768,2048,1280],
    }
    qa=[dict(art(local),cropBoxIn4096=m["cropBoxIn4096"],resized=False)]
    for name,rect in rects.items():
        p=D/(name+".png");png(p,Image.fromarray(result).crop(rect));qa.append(dict(art(p),cropBoxIn4096=rect,resized=False))
    # Independently replay using saved alpha and scalar Python integer arithmetic.
    rep=Image.open(m["sourceCandidate"]["path"]).convert("RGB");px=rep.load()
    nr=Image.open(native).convert("RGB").load();ar=Image.open(ap).convert("L").load()
    for yy in range(h):
        for xx in range(w):
            av=ar[xx,yy]
            if av:
                oo=px[box[0]+xx,box[1]+yy];nn=nr[crop[0]+xx,crop[1]+yy]
                px[box[0]+xx,box[1]+yy]=tuple((oo[c]*(255-av)+nn[c]*av+127)//255 for c in range(3))
    assert np.array_equal(np.array(rep),result)
    assert np.array_equal(np.array(Image.open(context))[115:4211,115:4211],result)
    changed=np.any(result!=base,axis=2);support=np.zeros((4096,4096),bool);support[:1254,760:1360]=a>0
    assert not changed[~support].any()
    assert np.array_equal(result[:,1360:],base[:,1360:])
    # Includes the approved right-hand leaf around x1900, and all other distant material.
    yy,xx=np.where(changed)
    verify={"checkedAtUtc":datetime.now(timezone.utc).isoformat(),"scalarReplayExact":True,"contextCoreExact":True,"outsideSavedAlphaUnchanged":True,"approvedRightLeafAndAllX1360OnwardUnchanged":True,"topCoreRowNativeAdoptedInsideSeams":True,"originalByteCopyVerified":True,"actualChangeBox":[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],"changedPixels":int(changed.sum()),"formalAccepted":False}
    vp=D/"replay-verification.json";write(vp,verify)
    manifest={"schemaVersion":1,"tile":T.name,"version":D.name,"composedAtUtc":datetime.now(timezone.utc).isoformat(),"sourceCandidate":m["sourceCandidate"],"sourceContext":m["sourceContext"],"sourceAssembly":m["sourceAssembly"],"native":art(native),"generationRecord":info(record),"receipt":info(receipt),"request":info(D/"request.json"),"preparation":info(D/"preparation.json"),"nativeCrop":crop,"pasteBoxIn4096":box,"alpha":art(ap),"seamPaths":info(sp),"algorithm":info(algo_path),"compositor":info(__file__),"method":"minimum-error left/right/bottom paths in 64px overlap, Gaussian radius2 on alpha only; no top seam because repair touches core y0","blendArithmetic":"(old*(255-alpha)+new*alpha+127)//255 uint32","resampling":False,"RGBColorCorrection":False,"layoutGuidePixelsComposited":False,"candidate":art(candidate),"context":art(context),"verification":verify,"replay":info(vp),"QAImages":qa,"status":"unpublished_trial_pending_visual_review","formalAccepted":False}
    mp=D/"composition.json";write(mp,manifest)
    print(json.dumps({"candidate":art(candidate),"composition":info(mp),"verification":verify,"QAImageCount":len(qa)}))
if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="validate":
        m,r,b=validate();print(json.dumps({"status":"validated_offline_ready","tile":T.name,"nativeCrop":m["nativeAdoptionCrop"],"pasteBox":m["pasteBoxIn4096"],"compositor":info(__file__)}))
    elif len(sys.argv)==3 and sys.argv[1]=="compose":compose(sys.argv[2])
    else:raise SystemExit("Usage: offline_compose.py validate | compose ORIGINAL_BUILTIN_PNG")
