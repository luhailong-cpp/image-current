from pathlib import Path
import importlib.util,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;R=W.parent
spec=importlib.util.spec_from_file_location('assembly',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
plan=m.read(W/'selected.json');assert len(plan['sources'])==16
sources=[];patches={}
for e in plan['sources']:
 p=R/e['file'];r=m.read(R/e['generationRecord']);assert m.sha(p)==e['sha256']==r['sha256'];assert m.sha(R/e['generationRecord'])==e['generationRecordSha256']
 a=np.array(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3);assert r['nativeScaleResampled'] is False
 assert r['actualModel'] is None and r['actualQuality'] is None and r['unverifiedReason']
 for ref in r['references']:assert m.sha(ref['file'])==ref['sha256']
 req=m.read(r['evidence']['request']);receipt=m.read(r['evidence']['receipt']);assert Path(r['prompt']).read_text(encoding='utf-8-sig').strip()==req['prompt'].strip();assert m.sha(receipt['originalFile'])==e['sha256']
 d={**e,'globalNativeBox':r['globalNativeBox'],'globalCoreBox':r['globalCoreBox']};sources.append(d);patches[e['sourceId']]=a
bridges=[(17,0,'r03_c02_s01_c03_c04_bridge_v01'),(18,2,'r03_c02_s03_c02_c03_bridge_v01'),(19,0,'r03_c02_c03_roof_bridge_v01')]
for sid,row,n in bridges:
 p=R/'native'/f'{n}.png';r=m.read(str(p)+'.generation.json');assert m.sha(p)==r['sha256'];a=np.array(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3)
 for ref in r['references']:assert m.sha(ref['file'])==ref['sha256']
 sources.append({'sourceId':sid,'file':str(p.relative_to(R)),'sha256':r['sha256'],'generationRecord':str(p.relative_to(R))+'.generation.json','generationRecordSha256':m.sha(str(p)+'.generation.json'),'globalNativeBox':r['globalNativeBox'],'globalCoreBox':r['globalCoreBox'],'role':'external bridge root-owned' if sid==19 else 'required internal bridge'});patches[sid]=a
def compose(include_external):
 strips=[];stripids=[];seams=[]
 for row in range(4):
  strip=patches[row*4+1].copy();ids=np.full((1254,1254),row*4+1,np.uint8)
  for col in range(1,4):
   sid=row*4+col+1;strip,ids,d=m.append_hard(strip,ids,patches[sid],np.full((1254,1254),sid,np.uint8),f'row{row+1}-col{col}-{col+1}');d.update({'axis':'vertical','row':row+1,'assemblyX':col*1024,'assemblyY':row*1024});seams.append(d)
  for sid,br,n in bridges:
   if br!=row or (sid==19 and not include_external):continue
   s=next(s for s in sources if s['sourceId']==sid);x=s['globalNativeBox'][0]-3981;width=min(1254,4326-x);old=strip[:,x:x+width].copy();a=patches[sid][:,:width];L,lc=m.minimum_vertical_seam(old[:,:115],a[:,:115]);RR=np.full(1254,width,np.int32)
   if width==1254:RR,rc=m.minimum_vertical_seam(a[:,1139:],old[:,1139:]);RR+=1139
   mask=(np.arange(width)[None,:]>=L[:,None])&(np.arange(width)[None,:]<RR[:,None]);strip[:,x:x+width]=np.where(mask[...,None],a,old);ids[:,x:x+width]=np.where(mask,sid,ids[:,x:x+width]);seams.append({'bridge':n,'sourceId':sid,'assemblyX':x,'assemblyY':row*1024,'leftXByY':L.tolist(),'rightXByY':RR.tolist(),'wholeCoreForced':True,'externalTruncatedToTileHalo':width<1254})
  strips.append(strip);stripids.append(ids)
 canvas,ids=strips[0],stripids[0]
 for row in range(1,4):
  a,i,d=m.append_hard(canvas.transpose(1,0,2),ids.T,strips[row].transpose(1,0,2),stripids[row].T,f'row{row}-row{row+1}');canvas,ids=a.transpose(1,0,2),i.T;d.update({'axis':'horizontal','assemblyY':row*1024,'assemblyX':0});seams.append(d)
 return canvas[115:4211,115:4211].copy(),ids[115:4211,115:4211].copy(),seams
for external,name in [(False,'r03_c02.candidate'),(True,'r03_c02.with-root-bridge-context')]:
 out,ids,seams=compose(external);counts=[]
 for s in sources:
  sid=s['sourceId'];ys,xs=np.nonzero(ids==sid)
  if len(xs)==0:continue
  b=s['globalNativeBox'];sx=xs+4096-b[0];sy=ys+8192-b[1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(out[ys,xs],patches[sid][sy,sx]);counts.append({'sourceId':sid,'pixelCount':len(xs),'outputBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
 assert sum(c['pixelCount'] for c in counts)==4096**2
 op=W/'tiles'/name;Image.fromarray(out).save(str(op)+'.png');Image.fromarray(ids).save(str(op)+'.source-id.png');m.write_json(Path(str(op)+'.seams.json'),{'paths':seams,'nativeOverlap':230,'blend':False,'resample':False})
 rec={'tile':'r03_c02','createdAt':datetime.now(timezone.utc).isoformat(),'globalCoreBox':[4096,8192,8192,12288],'size':[4096,4096],'status':'candidate-pending-final-visual-QA','formalAccepted':False,'published':False,'externalRootBridgeIncludedForContext':external,'sources':sources,'contributions':counts,'allPixelsEqualRecordedNativeRGB':True,'pixelCountVerified':4096**2,'resample':False,'feather':False,'colorRewrite':False,'guidePixelsUsed':False,'artifacts':[{'file':str(op)+suffix,'sha256':m.sha(str(op)+suffix)} for suffix in ['.png','.source-id.png','.seams.json']],'script':{'file':str(Path(__file__)),'sha256':m.sha(Path(__file__))}}
 m.write_json(Path(str(op)+'.assembly.json'),rec)
 if external:
  crops=[]
  for axis in ['v','h']:
   for k in range(1,4):
    for j in range(4):
     b=[k*1024-230,j*1024,k*1024+230,(j+1)*1024] if axis=='v' else [j*1024,k*1024-230,(j+1)*1024,k*1024+230]
     p=W/'qa'/f'final-{axis}{k}-segment{j+1}.100pct.png';Image.fromarray(out).crop(b).save(p);crops.append({'file':str(p),'outputBox':b,'purpose':'full-length seam strip segment'})
  for y in range(1,4):
   for x in range(1,4):
    b=[x*1024-300,y*1024-300,x*1024+300,y*1024+300];p=W/'qa'/f'final-intersection-{y}-{x}.100pct.png';Image.fromarray(out).crop(b).save(p);crops.append({'file':str(p),'outputBox':b,'purpose':'intersection'})
  m.write_json(W/'qa/final-native-crops.json',{'source':str(op)+'.png','sha256':m.sha(str(op)+'.png'),'crops':crops,'scale':1})
 print(json.dumps({'candidate':str(op)+'.png','sha256':m.sha(str(op)+'.png'),'pixelProof':4096**2}))
