from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import json, hashlib, shutil, datetime

Z = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
name = 'r05_c12_p11-p21-loweredge-v2'
host = Path('C:/Users/luyua/.codex/generated_images/01a13004-3711-7343-a016-7bdb371d0ccc/exec-d6d921a8-3a3d-4930-aa5d-6922b9861ca6.png')
native = Z/f'native/{name}.png'
assert not native.exists(), native
shutil.copyfile(host,native)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 assert not p.exists(), p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(native).convert('RGB')
plan=load(Z/f'records/{name}.plan.json')
receipt=Z/f'records/{name}.receipt.json'
prompt=Z/f'records/{name}.prompt.txt'
gen=dict(schemaVersion=1,patchId='r05_c12_p11-p21-loweredge',version='v2',
 file=str(native),sha256=sha(native),source=dict(path=str(host),sha256=sha(host),role='host output byte-for-byte copy'),
 nativeSize=list(im.size),width=im.width,height=im.height,tool='image_gen.imagegen',route='builtin',
 submittedParameters=dict(transparent_background=False,model=None,quality=None),
 actualModel=None,actualQuality=None,modelSelectorSubmitted=False,qualitySelectorSubmitted=False,
 actualModelReason='Host tool exposes no model or quality selector; result does not identify either.',
 observedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 nativeGlobalBox=plan['nativeGlobalBox'],references=plan['references'],
 prompt=dict(path=str(prompt),sha256=sha(prompt),role='actual submitted prompt'),
 receipt=dict(path=str(receipt),sha256=sha(receipt),role='actual return text and returned-key receipt'),
 pngMetadataKeys=list(Image.open(native).info),nativeResizePerformed=False,
 formalAccepted=False,status='native_candidate_awaiting_four_boundary_QA')
save(Path(str(native)+'.generation.json'),gen)
assert im.size==(1254,1254), 'Unexpected native size: preserved raw output, do not resize'
targetpath=Z/'qa/r05_c12-roofbridge-v1/context.native-1to1.png'
target=Image.open(targetpath).convert('RGB')
box=(30,660,650,820)
context=target.copy();context.paste(im.crop(box),box[:2])
qa=Z/'qa/r05_c12-loweredge-v2';qa.mkdir(exist_ok=False)
contextpath=qa/'context.native-1to1.png';context.save(contextpath)
sources=[dict(path=str(targetpath),sha256=sha(targetpath),role='existing native assembled context'),dict(path=str(native),sha256=sha(native),role='new generated native repair')]
crop_defs=[('top',(0,580,740,740),'horizontal',660),('bottom',(0,740,740,900),'horizontal',820),('left',(0,580,160,900),'vertical',30),('right',(570,580,730,900),'vertical',650),('interior-blue-tiles',(0,620,650,870),'horizontal',740)]
strips=[]
for label,crop,orientation,boundary in crop_defs:
 p=qa/f'{label}.native-1to1.png';context.crop(crop).save(p)
 strips.append(dict(path=str(p),sha256=sha(p),nativeSize=[crop[2]-crop[0],crop[3]-crop[1]],contextCrop=list(crop),orientation=orientation,boundaryInContext=boundary,operation='exact integer crop; no resize',rawRGBPixelSha256=hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest()))
derived=[]
for patch,base,ngb in [('r05_c12_p11','r05_c12_p11-roofbridge-v1.png',[44941,16269,46195,17523]),('r05_c12_p21','r05_c12_p21-roofbridge-v1.png',[44941,17293,46195,18547])]:
 world=[44971,17441,45591,min(17601,ngb[3])]
 src=[world[0]-44941,world[1]-16781,world[2]-44941,world[3]-16781]
 paste=[world[0]-ngb[0],world[1]-ngb[1]]
 bp=Z/'native'/base;out=Z/f'native/{patch}-roofbridge-v2.png'
 assert not out.exists(), out
 bim=Image.open(bp).convert('RGB');bim.paste(im.crop(src),paste);bim.save(out)
 record=dict(schemaVersion=1,file=str(out),sha256=sha(out),pixels=list(bim.size),nativeGlobalBox=ngb,
 operation='Exact integer crop and opaque paste of native generated repair; no resize, paint, blend or feather',
 derivedFrom=[dict(path=str(bp),sha256=sha(bp),derivedRecord=dict(path=str(bp)+'.derived.json',sha256=sha(str(bp)+'.derived.json'))),dict(path=str(native),sha256=sha(native),generationRecord=dict(path=str(native)+'.generation.json',sha256=sha(str(native)+'.generation.json')))],
 contributions=[dict(source=str(native),sourceSha256=sha(native),sourceCropBox=src,pasteAt=paste,worldBox=world)],formalAccepted=False,status='pending_native_QA')
 save(Path(str(out)+'.derived.json'),record);derived.append(dict(path=str(out),sha256=sha(out),contribution=record['contributions'][0]))
save(qa/'construction.json',dict(schemaVersion=1,createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources=sources,context=dict(path=str(contextpath),sha256=sha(contextpath),nativeSize=list(context.size),nativeGlobalBox=[44941,16781,46195,18035]),contributionLocalBox=list(box),contributionWorldBox=[44971,17441,45591,17601],strips=strips,derivedPatches=derived,formalAccepted=False,visualReview='pending',outsideContributionPixelsChanged=False))
print(json.dumps(dict(native=str(native),nativeSize=list(im.size),sha256=sha(native),qa=str(qa),derived=derived),ensure_ascii=False))
