"""Preserve native art; replay saved source alpha and apply two bounded repair masks."""
from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
R=T/'repairs-20261012'
Q=T/'review/native-orphan-repair-v2'
Q.mkdir(exist_ok=True)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evidence(p):
 p=Path(p); d={'path':str(p),'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p) as im: d['size']=list(im.size)
 return d
def writej(p,d):
 p=Path(p); s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if p.exists(): assert p.read_text(encoding='utf-8')==s, str(p)
 else: p.write_text(s,encoding='utf-8')
def png(p,a):
 p=Path(p)
 if p.exists(): assert np.array_equal(np.asarray(Image.open(p)),a)
 else: Image.fromarray(a).save(p)
 return evidence(p)
basepath=T/'candidate/r16_c13-assembly-1b42f26f841bf002cac7.json'
b=read(basepath)
native=[]
for s in b['nativeSources']:
 assert sha(s['native'])==s['nativeSha256']
 native.append(np.asarray(Image.open(s['native']).convert('RGB')))
assert sha(b['seamPathsAndAlpha']['path'])==b['seamPathsAndAlpha']['sha256']
with np.load(b['seamPathsAndAlpha']['path'],allow_pickle=False) as masks:
 def join(a,c,label):
  w=masks[label+'_alpha'].astype(np.uint32)[...,None]
  v=((a[:,-230:].astype(np.uint32)*(255-w)+c[:,:230].astype(np.uint32)*w+127)//255).astype(np.uint8)
  return np.concatenate([a[:,:-230],v,c[:,230:]],axis=1)
 strips=[]
 for row in range(4):
  strip=native[row*4]
  for col in range(1,4): strip=join(strip,native[row*4+col],f'row{row+1:02d}_c{col:02d}_c{col+1:02d}')
  strips.append(strip)
 context=strips[0].transpose(1,0,2)
 for row in range(1,4): context=join(context,strips[row].transpose(1,0,2),f'rows_r{row:02d}_r{row+1:02d}')
 context=context.transpose(1,0,2).copy()
assert np.array_equal(context,np.asarray(Image.open(b['context']['path'])))
base=context[115:4211,115:4211].copy()
assert np.array_equal(base,np.asarray(Image.open(b['candidate']['path'])))
receiptpath=R/'two-orphan-joints-v1.tool-receipt.json'
receipt=read(receiptpath)
original=Path(receipt['originalOutputPath'])
destination=R/'two-orphan-joints-v1-native.png'
if not destination.exists(): shutil.copyfile(original,destination)
assert sha(original)==sha(destination)
with Image.open(destination) as im:
 assert im.size==(1254,1254) and im.mode in ('RGB','RGBA')
 assert im.mode=='RGB' or im.getextrema()[3]==(255,255)
 source=np.asarray(im.convert('RGB'))
requestpath=R/'two-orphan-joints-v1.request.json'
request=read(requestpath)
target=Path(request['referenced_image_paths'][-1])
assert np.array_equal(base[1650:2904,2300:3554],np.asarray(Image.open(target)))
support=[[404,453,476,551],[854,424,930,551]]
mask=np.zeros((1254,1254),dtype=np.uint8)
for x0,y0,x1,y1 in support:
 yy,xx=np.mgrid[y0:y1,x0:x1]
 dist=np.minimum.reduce([xx-x0,yy-y0,x1-1-xx,y1-1-yy])
 mask[y0:y1,x0:x1]=np.rint(np.clip(dist/12,0,1)*255).astype(np.uint8)
maskinfo=png(R/'two-orphan-joints-v2-alpha.png',mask)
assert np.array_equal(np.asarray(Image.open(maskinfo['path'])),mask)
w=mask.astype(np.uint32)[...,None]
old=base[1650:2904,2300:3554]
blended=((old.astype(np.uint32)*(255-w)+source.astype(np.uint32)*w+127)//255).astype(np.uint8)
result=base.copy(); result[1650:2904,2300:3554]=blended
allowed=np.zeros((4096,4096),bool); allowed[1650:2904,2300:3554]=mask>0
assert np.array_equal(result[~allowed],base[~allowed])
context[115:4211,115:4211]=result
candidate=png(T/'candidate/r16_c13-4k-orphan-repair-v2-20261013.png',result)
ctx=png(T/'candidate/r16_c13-context-4326-orphan-repair-v2-20261013.png',context)
images=[]
for label,box in [('repair-scar-a',[2590,2020,2890,2330]),('repair-scar-b',[3040,1990,3360,2330]),('repair-crossing',[2622,1798,3522,2698])]:
 x0,y0,x1,y1=box
 for version,a in [('before',base),('after',result)]:
  item=png(Q/f'{label}-{version}-100pct.png',a[y0:y1,x0:x1]);item.update(cropBoxIn4096=box,resized=False); images.append(item)
record={'schemaVersion':1,'tile':'r16_c13','id':'two-orphan-joints-v1','file':str(destination),'sha256':sha(destination),'width':1254,'height':1254,'route':'builtin','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'generatedAt':receipt['generatedAt'],'timestampBasis':receipt['timestampBasis'],'resizedAfterGeneration':False,'original':evidence(original),'receipt':evidence(receiptpath),'request':evidence(requestpath),'prompt':evidence(R/'two-orphan-joints-v1.prompt.txt'),'references':[evidence(p) for p in request['referenced_image_paths']],'targetDerivation':{'source':b['candidate'],'cropBox':[2300,1650,3554,2904],'resize':False},'status':'native_saved_applied_to_two_local_supports_pending_local_visual_review'}
recordpath=R/'two-orphan-joints-v1-native.png.generation.json'; writej(recordpath,record)
manifest={'schemaVersion':1,'tile':'r16_c13','status':'candidate_pending_local_repair_visual_review','formalAccepted':False,'baseManifest':evidence(basepath),'baseCandidate':b['candidate'],'baseContext':b['context'],'candidate':candidate,'context':ctx,'repairNative':evidence(destination),'repairGenerationRecord':evidence(recordpath),'alpha':maskinfo,'repairSourceCrop':[0,0,1254,1254],'placementInCore':[2300,1650,3554,2904],'alphaSupportBoxesInRepairSource':support,'featherPixels':12,'blendArithmetic':'(base*(255-alpha)+source*alpha+127)//255 using uint32','sourceResampling':False,'sourceUpscaling':False,'registration':False,'colorMatching':False,'programmaticRgbCorrection':False,'baseNativeSourceCount':16,'appliedRepairSourceCount':1,'retainedOriginalSourceCount':19,'replay':{'baseFromSixteenNativesAndSavedAlphaPixelIdentical':True,'repairFromNativeAndSavedAlphaPixelIdentical':True,'outsideRepairSupportsPixelIdentical':True,'allFourOuterEdgesUnchanged':True,'changedPixelCount':int(np.any(result!=base,axis=2).sum())},'reviewImages':images,'script':evidence(__file__)}
manifestpath=T/'candidate/r16_c13-orphan-repair-v2-20261013-manifest.json';writej(manifestpath,manifest)
print(json.dumps({'candidate':candidate,'context':ctx,'manifest':evidence(manifestpath),'repair':evidence(destination),'replay':manifest['replay']},indent=2))
