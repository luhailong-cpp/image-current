from pathlib import Path
from PIL import Image
import json,hashlib,shutil,datetime
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
name='r05_c12_p11-p21-loweredge-v3'
host=Path('C:/Users/luyua/.codex/generated_images/01a13004-3711-7343-a016-7bdb371d0ccc/exec-a1593daa-f180-4710-aab4-7bca893229f1.png')
native=Z/f'native/{name}.png';assert not native.exists();shutil.copyfile(host,native)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
plan=json.loads((Z/f'records/{name}.plan.json').read_text(encoding='utf-8'))
im=Image.open(native).convert('RGB');pp=Z/f'records/{name}.prompt.txt';rp=Z/f'records/{name}.receipt.json'
save(Path(str(native)+'.generation.json'),dict(schemaVersion=1,file=str(native),sha256=sha(native),nativeSize=list(im.size),width=im.width,height=im.height,nativeGlobalBox=plan['nativeGlobalBox'],
 tool='image_gen.imagegen',route='builtin',source=dict(path=str(host),sha256=sha(host),role='byte-for-byte host output copy'),references=plan['references'],
 prompt=dict(path=str(pp),sha256=sha(pp),role='actual submitted prompt'),receipt=dict(path=str(rp),sha256=sha(rp),role='actual tool return receipt'),
 submittedParameters=dict(transparent_background=False,model=None,quality=None),actualModel=None,actualQuality=None,
 actualModelReason='Host exposes no selector and return does not identify actual model or quality',nativeResizePerformed=False,formalAccepted=False,status='native_candidate_awaiting_QA',observedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
assert im.size==(1254,1254)
tp=Z/'qa/r05_c12-roofbridge-v1/context.native-1to1.png';context=Image.open(tp).convert('RGB')
boxes=plan['holeLocalBoxes']
for b in boxes:context.paste(im.crop(b),tuple(b[:2]))
qa=Z/'qa/r05_c12-loweredge-v3';qa.mkdir(exist_ok=False)
cp=qa/'context.native-1to1.png';context.save(cp)
strips=[]
for i,(x0,y0,x1,y1) in enumerate(boxes,1):
 for edge,crop,axis,boundary in [('top',(max(0,x0-40),y0-40,x1+40,y0+40),'y',y0),('bottom',(max(0,x0-40),y1-40,x1+40,y1+40),'y',y1),('left',(x0-40,y0-40,x0+40,y1+40),'x',x0),('right',(x1-40,y0-40,x1+40,y1+40),'x',x1)]:
  p=qa/f'window{i}-{edge}.native-1to1.png';context.crop(crop).save(p)
  strips.append(dict(path=str(p),sha256=sha(p),nativeSize=[crop[2]-crop[0],crop[3]-crop[1]],contextCrop=list(crop),axis=axis,boundary=boundary,operation='exact integer crop, no resize'))
dp=qa/'interior-blue-tiles.native-1to1.png';context.crop((0,620,650,870)).save(dp)
save(qa/'construction.json',dict(schemaVersion=1,sources=[dict(path=str(tp),sha256=sha(tp)),dict(path=str(native),sha256=sha(native))],context=dict(path=str(cp),sha256=sha(cp),nativeSize=list(context.size),nativeGlobalBox=plan['nativeGlobalBox']),
 contributionLocalBoxes=boxes,contributionWorldBoxes=[[b[0]+44941,b[1]+16781,b[2]+44941,b[3]+16781] for b in boxes],strips=strips,formalAccepted=False,visualReview='pending',outsideContributionsPixelsChanged=False))
print(json.dumps(dict(native=str(native),nativeSize=list(im.size),sha256=sha(native),qa=str(qa))))
