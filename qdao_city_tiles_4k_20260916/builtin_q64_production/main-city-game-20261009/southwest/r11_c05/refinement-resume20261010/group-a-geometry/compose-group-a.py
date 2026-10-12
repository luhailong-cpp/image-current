from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
import json,hashlib,re
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def jsave(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
 with Image.open(p) as im:size=list(im.size)
 return {'path':str(p),'sha256':sha(p),'pixels':size,'resampled':False}
for v in (1,2,3,4):
 req=read(D/f'request-v{v}.json');receipt=D/f'receipts/group-a-v{v}.receipt.json';rc=read(receipt)
 for ref in req['references']:assert sha(ref['path'])==ref['sha256']
 assert sha(req['promptFile'])==req['promptSha256']
 native=D/f'native/group-a-v{v}.png';src=Path(re.search(r' as (.+?\.png) by default',rc['metadata']['output_hint']).group(1));assert sha(src)==sha(native)
 im=Image.open(native);assert im.size==(1254,1254)
 rec={'id':req['id'],'file':str(native),'sha256':sha(native),'sourceOutput':str(src),'sourceOutputSha256':sha(src),'width':1254,'height':1254,'nativePixelsPreserved':True,'resizedAfterGeneration':False,'actualModel':None,'actualQuality':None,'route':'builtin','tool':'image_gen.imagegen','prompt':req['promptFile'],'promptSha256':req['promptSha256'],'references':req['references'],'receipt':str(receipt),'receiptSha256':sha(receipt),'sourceCrop':req['sourceCrop'],'candidateUse':('G01-G02 removal source' if v==4 else 'rejected because existing diagonal geometry moved')}
 jsave(D/f'native/group-a-v{v}.png.generation.json',rec)
base=read(D/'input/crop-record.json');old=np.array(Image.open(base['target']).convert('RGB'));assert sha(base['target'])==base['targetSha256']
bmanifest_path=D.parent/'B-repair/output/assembly.json';bm=read(bmanifest_path)
bmasks=np.zeros((4326,4326),bool)
for p in bm['patches']:
 m=p['pasteMask'];assert sha(m['path'])==m['sha256'];x0,y0,x1,y1=p['contextBox']
 bmasks[y0:y1,x0:x1]|=np.array(Image.open(m['path']).convert('L'))>0
local_b=bmasks[2100:3354,512:1766]
specs=[
 {'id':'G01-G02','source':D/'native/group-a-v4.png','lines':[([(533,810),(840,1098)],55), ([(716,1173),(840,1098)],52)],'ellipses':[(810,1068,872,1127),(509,786,556,834),(690,1147,743,1200)],'intent':'remove two unsupported NW/SW spurs, retain original NE-SE corner'},
 {'id':'G07','source':D/'G07-worker/native/G07-v1.raw.png','lines':[([(250,559),(422,439),(515,372),(535,374),(650,297)],64), ([(250,560),(423,445),(515,385),(535,372),(650,297)],64), ([(423,395),(423,450)],34)],'ellipses':[],'intent':'use expanded narrow corridor to join misaligned diagonal smoothly; local T-junction endpoint shifts approximately six px, vertical stem and distant diagonal positions preserved'}
]
O=D/'output';Q=D/'qa';candidate=old.copy();combined=np.zeros((1254,1254),bool);patches=[]
for s in specs:
 native=np.array(Image.open(s['source']).convert('RGB'));assert native.shape==old.shape
 mask=Image.new('L',(1254,1254),0);draw=ImageDraw.Draw(mask)
 for pts,w in s['lines']:draw.line(pts,fill=255,width=w,joint='curve')
 for box in s['ellipses']:draw.ellipse(box,fill=255)
 raw=np.array(mask)>0;in1=np.array(mask.filter(ImageFilter.MinFilter(3)))>0;in2=np.array(mask.filter(ImageFilter.MinFilter(5)))>0
 alpha=np.zeros(raw.shape,np.uint8);alpha[raw]=64;alpha[in1]=191;alpha[in2]=255
 active=alpha>0;assert not np.any(active & local_b),f"B mask overlap for {s['id']}"
 assert not np.any(active & combined);assert not active[:10].any() and not active[-10:].any() and not active[:,:10].any() and not active[:,-10:].any()
 weight=alpha.astype(np.uint32)[...,None];blend=((old.astype(np.uint32)*(255-weight)+native.astype(np.uint32)*weight+127)//255).astype(np.uint8)
 candidate[active]=blend[active];combined|=active;ys,xs=np.where(active);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];x0,y0,x1,y1=box
 p=O/(s['id']+'.preblended.patch.png');m=O/(s['id']+'.paste-mask.png');a=O/(s['id']+'.alpha-evidence.png')
 Image.fromarray(blend[y0:y1,x0:x1]).save(p);Image.fromarray((active[y0:y1,x0:x1]*255).astype(np.uint8)).save(m);Image.fromarray(alpha[y0:y1,x0:x1]).save(a)
 patches.append({'id':s['id'],'intent':s['intent'],'nativeSource':info(s['source']),'cropLocalBox':box,'contextBox':[x0+512,y0+2100,x1+512,y1+2100],'tileCoreBox':[x0+397,y0+1985,x1+397,y1+1985],'worldBox':[x0+16781,y0+42945,x1+16781,y1+42945],'patch':info(p),'pasteMask':info(m),'alphaEvidence':info(a),'affectedPixelCount':int(active.sum()),'maskClipGeometryOnly':{'lines':s['lines'],'ellipses':s['ellipses'],'featherRadius':2},'instruction':'Paste using binary mask once at contextBox origin; patch is preblended. Do not paste its entire rectangle, rescale or re-feather.'})
assert np.array_equal(candidate[~combined],old[~combined])
Image.fromarray(candidate).save(O/'A.candidate.native-crop.png');Image.fromarray((combined*255).astype(np.uint8)).save(O/'A.combined-mask.png')
for label,box in [('G07',[200,250,710,630]),('G01-G02',[450,740,960,1230])]:
 for name,a in [('original',old),('candidate',candidate)]:
  Image.fromarray(a).crop(box).save(Q/f'{label}-{name}.png')
 # QA side-by-side is only pixel concatenation, no artwork resizing or annotations.
 pair=np.concatenate([old[box[1]:box[3],box[0]:box[2]],candidate[box[1]:box[3],box[0]:box[2]]],axis=1)
 Image.fromarray(pair).save(Q/f'{label}-original-candidate.png')
manifest={'status':'composed-awaiting-visual-review','formalAccepted':False,'sourceContext':base['sourceContext'],'requiredContextSha256':base['sourceContextSha256'],'sourceCrop':base,'candidate':info(O/'A.candidate.native-crop.png'),'patches':patches,'checks':{'outsideMasksExact':True,'allOuterImageEdgesExact':True,'BmaskPixelIntersection':0,'Bassembly':str(bmanifest_path),'BassemblySha256':sha(bmanifest_path),'resampling':False,'colorAdjustment':False,'geometryWarping':False,'maximumFeatherRadiusPixels':2},'G07LocalGeometryAdjustment':{'TjunctionOriginalDarkestAtX420':439,'generatedDarkestAtX420':445,'deltaPixels':6,'intent':'expanded corridor is a different proposed composition from rejected tiny ROI; retain explicit displacement evidence for parent review'},'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__))}
jsave(O/'assembly.json',manifest)
print(json.dumps({'patches':[{k:p[k] for k in ['id','contextBox','affectedPixelCount']} for p in patches],'checks':manifest['checks']},indent=2))

