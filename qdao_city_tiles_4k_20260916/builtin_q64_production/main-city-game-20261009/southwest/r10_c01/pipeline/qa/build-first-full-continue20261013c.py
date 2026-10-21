import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
b=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest");ap=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r10_c01/pipeline/output/3fa66685eea6dfa7/assembly.json");a=json.loads(ap.read_text(encoding="utf-8-sig"));out=ap.parent/"left-worker-qa-continue20261013c-v01";out.mkdir(exist_ok=False);hs=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();font=ImageFont.load_default(size=16)
corep=Path(a["output"]["file"]);ctxp=Path(a["contextOutput"]["file"]);assert hs(corep)==a["output"]["sha256"];assert hs(ctxp)==a["contextOutput"]["sha256"];core=Image.open(corep).convert("RGB");ctx=Image.open(ctxp).convert("RGB");assert core.size==(4096,4096) and ctx.size==(4326,4326)
items=[]
def save(name,panel,regions,kind):
 p=out/(name+".png");panel.save(p);items.append({"id":name,"kind":kind,"file":str(p),"sha256":hs(p),"pixels":list(panel.size),"nativeRegionResampling":False,"regions":regions});return p
def reg(box,source=corep,sourcehash=None,label=""):
 return {"source":str(source),"sourceSha256":sourcehash or hs(source),"cropBox":list(box),"pixels":[box[2]-box[0],box[3]-box[1]],"label":label,"resampling":False}
for c in range(1,4):
 panel=Image.new("RGB",(988,1090),(30,35,40));dr=ImageDraw.Draw(panel);regions=[]
 for r in range(4):
  box=(c*1024-115,r*1024,c*1024+115,(r+1)*1024);x=16+r*244;dr.text((x,12),f"V{c} row{r+1}",font=font,fill="white");panel.paste(core.crop(box),(x,45));regions.append(reg(box,label=f"V{c}-r{r+1}"))
 save(f"internal-V{c}",panel,regions,"internal-native-seams")
for r in range(1,4):
 panel=Image.new("RGB",(1056,1128),(30,35,40));dr=ImageDraw.Draw(panel);regions=[]
 for c in range(4):
  box=(c*1024,r*1024-115,(c+1)*1024,r*1024+115);y=16+c*276;dr.text((16,y),f"H{r} col{c+1}",font=font,fill="white");panel.paste(core.crop(box),(16,y+28));regions.append(reg(box,label=f"H{r}-c{c+1}"))
 save(f"internal-H{r}",panel,regions,"internal-native-seams")
panel=Image.new("RGB",(778,856),(30,35,40));dr=ImageDraw.Draw(panel);regions=[]
for r in range(1,4):
 for c in range(1,4):
  box=(c*1024-115,r*1024-115,c*1024+115,r*1024+115);x=16+(c-1)*250;y=16+(r-1)*276;dr.text((x,y),f"corner r{r}c{c}",font=font,fill="white");panel.paste(core.crop(box),(x,y+28));regions.append(reg(box,label=f"r{r}c{c}"))
save("internal-nine-corners",panel,regions,"internal-native-intersections")
cat=json.loads((b/"current-candidates.json").read_text(encoding="utf-8-sig"));top=cat["tiles"]["r09_c01"]["context"];tp=Path(top["file"]);assert hs(tp)==top["sha256"];ti=Image.open(tp).convert("RGB");assert ti.size==(4326,4326)
for group in range(2):
 panel=Image.new("RGB",(1056,1104),(30,35,40));dr=ImageDraw.Draw(panel);regions=[]
 for k in range(2):
  c=group*2+k;x0=115+c*1024;upbox=(x0,4096,x0+1024,4326);mybox=(x0,0,x0+1024,230);y=16+k*544;dr.text((16,y),f"TOP col{c+1} r09c01 bottom context / r10c01 top context",font=font,fill="white");panel.paste(ti.crop(upbox),(16,y+28));panel.paste(ctx.crop(mybox),(16,y+286));regions.extend([reg(upbox,tp,top["sha256"],f"TOP-c{c+1}-upper"),reg(mybox,ctxp,a["contextOutput"]["sha256"],f"TOP-c{c+1}-lower")])
 save(f"external-top-cols-{group*2+1}-{group*2+2}",panel,regions,"external-native-top-context-pairs")
rightp=b/"r10_c02/native/p01_01.png";rg=json.loads(rightp.with_name(rightp.name+".generation.json").read_text(encoding="utf-8-sig"));assert hs(rightp)==rg["sha256"];ri=Image.open(rightp).convert("RGB");panel=Image.new("RGB",(506,1090),(30,35,40));dr=ImageDraw.Draw(panel);dr.text((16,12),"RIGHT row1 this / c02",font=font,fill="white");cb=(4096,115,4326,1139);rb=(0,115,230,1139);panel.paste(ctx.crop(cb),(16,45));panel.paste(ri.crop(rb),(260,45));save("external-right-row1-only",panel,[reg(cb,ctxp,a["contextOutput"]["sha256"],"thisright"),reg(rb,rightp,rg["sha256"],"rightneighborleft")],"external-partial-native-right-context-pair")
p=out/"overview-QA-only-1600.png";pv=Image.new("RGB",(1600,1640),(30,35,40));ImageDraw.Draw(pv).text((16,10),"QA PREVIEW ONLY - native core4096, not delivered art",font=font,fill="white");pv.paste(core.resize((1600,1600),Image.Resampling.LANCZOS),(0,40));pv.save(p);overview={"file":str(p),"sha256":hs(p),"qaOnly":True,"finalArt":False,"resamplingOnlyThisPreview":True,"source":str(corep),"sourceSha256":a["output"]["sha256"]}
rec={"schemaVersion":1,"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"tile":"r10_c01","assembly":{"file":str(ap),"sha256":hs(ap)},"core":a["output"],"context":a["contextOutput"],"overview":overview,"panels":items,"internalNativeRegions":33,"externalNativeRegions":10,"externalCompleteness":{"top":"native provisional context available; notaccepted","right":"row1 nativeonly; rows2-4 missing","left":"outside main-city artworld","bottom":"neighbor native unavailable"},"visualInspectionComplete":False,"internalPassed":False,"externalPassed":False,"formalAccepted":False,"gitMutated":False}
mp=out/"manifest.json";mp.write_bytes(json.dumps(rec,ensure_ascii=False,indent=2).encode("utf8"));print(json.dumps({"manifest":str(mp),"overview":str(p),"panels":[{"id":i["id"],"file":i["file"]} for i in items],"regionCount":43}))

