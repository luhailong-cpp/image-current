from pathlib import Path
import json,hashlib,datetime,gc
from PIL import Image
import numpy as np
OUT=Path(__file__).resolve().parent
I=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
T={x['tileId']:x for x in I['tiles'] if x['fullCoverage']}
(OUT/'native-assemblies').mkdir(exist_ok=True)
(OUT/'seams-100pct').mkdir(exist_ok=True)
def sh(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def inf(p,**extra):
 with Image.open(p) as im:d={'file':Path(p).as_posix(),'sha256':sh(p),'dimensions':list(im.size)}
 return dict(d,**extra)
def cut(a,b,axis,name):
 with Image.open(T[a]['file']) as ia, Image.open(T[b]['file']) as ib:
  if axis=='vertical':
   im=Image.new('RGB',(2048,1024));boxes=[]
   for j in range(4):
    part=Image.new('RGB',(512,1024));part.paste(ia.crop((3840,j*1024,4096,(j+1)*1024)),(0,0));part.paste(ib.crop((0,j*1024,256,(j+1)*1024)),(256,0));im.paste(part,(j*512,0));boxes.append({'leftTileCrop':[3840,j*1024,4096,(j+1)*1024],'rightTileCrop':[0,j*1024,256,(j+1)*1024],'montageBox':[j*512,0,(j+1)*512,1024]})
  else:
   im=Image.new('RGB',(2048,1024));boxes=[]
   for j in range(4):
    part=Image.new('RGB',(1024,512));part.paste(ia.crop((j*1024,3840,(j+1)*1024,4096)),(0,0));part.paste(ib.crop((j*1024,0,(j+1)*1024,256)),(0,256));px=(j%2)*1024;py=(j//2)*512;im.paste(part,(px,py));boxes.append({'upperTileCrop':[j*1024,3840,(j+1)*1024,4096],'lowerTileCrop':[j*1024,0,(j+1)*1024,256],'montageBox':[px,py,px+1024,py+512]})
  p=OUT/'seams-100pct'/f'{name}.png';im.save(p);im.close()
  return inf(p,pair=[a,b],axis=axis,scale='1:1 exact pixels; unscaled montage',panels=boxes,inputHashes={a:T[a]['sha256'],b:T[b]['sha256']},status='pending_actual_view_image')
def cross(ids,name):
 im=Image.new('RGB',(1024,1024))
 cropboxes=[(3584,3584,4096,4096),(0,3584,512,4096),(3584,0,4096,512),(0,0,512,512)]
 for k,(t,box) in enumerate(zip(ids,cropboxes)):
  with Image.open(T[t]['file']) as src:im.paste(src.crop(box),((k%2)*512,(k//2)*512))
 p=OUT/'seams-100pct'/f'{name}.png';im.save(p);im.close()
 return inf(p,tiles=ids,cropBoxes=cropboxes,inputHashes={t:T[t]['sha256'] for t in ids},scale='1:1 exact corner pixels',status='pending_actual_view_image')
manifest={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assemblies':[],'seams':[],'junctions':[]}
# Only this four-tile group has current recorded internal passes throughout.
ids=['r10_c03','r10_c04','r11_c03','r11_c04']
im=Image.new('RGB',(8192,8192))
for k,t in enumerate(ids):
 with Image.open(T[t]['file']) as src:im.paste(src,((k%2)*4096,(k//2)*4096))
p=OUT/'native-assemblies/current-r10-r11-c03-c04-native-8192-v01.png';im.save(p)
verify=[]
for k,t in enumerate(ids):
 with Image.open(T[t]['file']) as src:
  cutim=im.crop(((k%2)*4096,(k//2)*4096,(k%2+1)*4096,(k//2+1)*4096))
  bad=int(np.count_nonzero(np.any(np.asarray(cutim)!=np.asarray(src.convert('RGB')),axis=2)))
  verify.append({'tileId':t,'mismatchedPixels':bad});cutim.close()
preview=im.resize((2048,2048),Image.Resampling.LANCZOS);pp=OUT/'native-assemblies/current-r10-r11-c03-c04-preview-2048-NOT-native.png';preview.save(pp);preview.close();im.close();gc.collect()
manifest['assemblies'].append(inf(p,tiles=ids,inputHashes={t:T[t]['sha256'] for t in ids},algorithm='exact 4096-grid paste; no feather, resize, recolor, AI or filling',pixelCopyValidation=verify,preview=inf(pp,resampledPreviewOnly=True),acceptance='local candidate assembly; internal/pair evidence reviewed; exterior not accepted'))
pairs=[('r08_c03','r08_c04','vertical'),('r08_c03','r09_c03','horizontal'),('r09_c05','r10_c05','horizontal'),('r09_c04','r09_c05','vertical'),('r10_c04','r10_c05','vertical')]
for a,b,ax in pairs:manifest['seams'].append(cut(a,b,ax,f'{a}-{b}-{ax}-native100-v01'))
for ids in [['r08_c03','r08_c04','r09_c03','r09_c04'],['r09_c04','r09_c05','r10_c04','r10_c05'],['r09_c02','r09_c03','r10_c02','r10_c03'],['r10_c03','r10_c04','r11_c03','r11_c04']]:
 manifest['junctions'].append(cross(ids,'cross-'+ids[0]+'-'+ids[-1]+'-native100-v01'))
(OUT/'assembly-review-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'assemblyCount':len(manifest['assemblies']),'newSeamMontages':len(manifest['seams']),'junctions':len(manifest['junctions'])}))
