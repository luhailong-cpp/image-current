from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,datetime
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast');R=Z/'records/west_sol'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role=None):
 d=dict(path=str(p),sha256=sha(p))
 if role:d['role']=role
 return d
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
p='r06_c11_p14';base=Z/f'native/{p}-v2-west_sol.png';src=Z/f'native/{p}-v3-west_sol.png';out=Z/f'native/{p}-v3-floorclosure-west_sol.png';assert not out.exists()
old=Image.open(base).convert('RGB');new=old.copy();im=Image.open(src).convert('RGB');box=[800,400,1254,1254];new.paste(im.crop(box),tuple(box[:2]));new.save(out)
restored=new.copy();restored.paste(old.crop(box),tuple(box[:2]));assert ImageChops.difference(old,restored).getbbox() is None
plan=read(R/f'{p}-v2.plan.json');co=plan['coordinates'];ngb=co['nativeGlobalBox']
record=dict(schemaVersion=1,file=str(out),sha256=sha(out),pixels=list(new.size),coordinates=co,nativeGlobalBox=ngb,
 operation='Exact integer crop and opaque paste of generated native v3 floor transition into generated native v2; no resize, paint, blend or feather',
 derivedFrom=[dict(**ref(base),generationRecord=ref(Path(str(base)+'.generation.json'))),dict(**ref(src),generationRecord=ref(Path(str(src)+'.generation.json')))],
 contributions=[dict(source=str(src),sourceSha256=sha(src),sourceCropBox=box,pasteAt=[800,400],worldBox=[ngb[0]+800,ngb[1]+400,ngb[2],ngb[3]])],
 mechanicalProof=dict(outsideContributionEqualsV2=True,contributionEqualsV3ExactNativeCrop=ImageChops.difference(new.crop(box),im.crop(box)).getbbox() is None),formalAccepted=False,status='candidate_native_floorclosure_pending_QA')
write(Path(str(out)+'.derived.json'),record)
qa=Z/f'qa/west_sol/{p}-v3-floorclosure';qa.mkdir(exist_ok=False);strips=[]
for e in plan['nativeEdgeSources']:
 q=Image.open(e['path']).convert('RGB');s=Image.new('RGB',(256,1254) if e['side']=='right' else (1254,256))
 if e['side']=='right':s.paste(new.crop((1011,0,1139,1254)),(0,0));s.paste(q.crop((115,0,243,1254)),(128,0))
 else:s.paste(q.crop((0,1011,1254,1139)),(0,0));s.paste(new.crop((0,115,1254,243)),(0,128))
 fp=qa/f'{e["side"]}.native-1to1.png';s.save(fp);strips.append(dict(**ref(fp),nativeSize=list(s.size),sources=[ref(out),e],seamLocalCoordinate=128,operation='exact native crop/paste, no resize'))
for label,cb in [('contribution-top',[720,320,1254,480]),('contribution-left',[720,320,880,1254])]:
 fp=qa/f'{label}.native-1to1.png';new.crop(cb).save(fp);strips.append(dict(**ref(fp),nativeSize=[cb[2]-cb[0],cb[3]-cb[1]],targetCropBox=cb,operation='exact native crop, no resize'))
write(qa/'construction.json',dict(native=ref(out),coordinates=co,nativeEdgeSources=plan['nativeEdgeSources'],strips=strips,derivedRecord=ref(Path(str(out)+'.derived.json')),formalAccepted=False,visualReview='pending'))
print(json.dumps(dict(native=str(out),sha256=sha(out),qa=str(qa))))
