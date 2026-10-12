from pathlib import Path
import sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
prior_path=T/'candidate/native-overlays-20261012-v06.json';prior=p.read(prior_path);plan_path=T/'qa/resume-c4-diagnosis-20261013/s03_04-ready-native-roi-plan.json';plan=p.read(plan_path);manifest_path=Path(prior['baseCandidate']['assembly']);base=p.read(manifest_path)
pix=np.array(Image.open(base['output']['file']).convert('RGB'));assert p.sha(base['output']['file'])==base['output']['sha256'];own=np.zeros((4096,4096),np.uint8);sources=[]
for s in base['nativeSources']:
 x,y=(s['column']-1)*1024,(s['row']-1)*1024;own[y:y+1024,x:x+1024]=len(sources);sources.append({**s,'tileOriginXY':[x-115,y-115]})
overlays=list(prior['overlays'])
for q in plan['planOrder']:
 f=Path(q['nativeFile']);g=p.read(f.with_suffix('.png.generation.json'));overlays.append({'id':q['id'],'file':str(f),'sha256':q['sha256'],'nativeWorldBox':g['worldBoxWithHalo'],'sourceROI':q['sourceROI'],'candidateROI':q['candidateROI'],'generationRecord':ref(f.with_suffix('.png.generation.json')),'readyNativePlan':ref(plan_path)})
for o in overlays:
 f=Path(o['file']);assert p.sha(f)==o['sha256'];n=np.array(Image.open(f).convert('RGB'));bx,by,bx2,by2=o['sourceROI'];wx,wy,wx2,wy2=o['nativeWorldBox'];x,y=wx+bx-20480,wy+by-24576;x2,y2=wx+bx2-20480,wy+by2-24576;assert [x,y,x2,y2]==o['candidateROI'];assert 0<=x<x2<=4096 and 0<=y<y2<=4096
 pix[y:y2,x:x2]=n[by:by2,bx:bx2];own[y:y2,x:x2]=len(sources)
 sources.append({'id':o['id'],'file':str(f),'sha256':o['sha256'],'tileOriginXY':[wx-20480,wy-24576],'worldBox':[wx,wy,wx2,wy2],'generationRecord':o.get('generationRecord',ref(f.with_suffix('.png.generation.json'))),'sourceROI':o['sourceROI'],'tileROI':o['candidateROI']})
proof=[]
for i,s in enumerate(sources):
 f=Path(s['file']);ys,xs=np.where(own==i);n=np.array(Image.open(f).convert('RGB'));ox,oy=s['tileOriginXY'];assert n.shape==(1254,1254,3);assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);gr=s['generationRecord']
 if isinstance(gr,str):gr=ref(gr);s['generationRecord']=gr
 assert p.sha(gr['file'])==gr['sha256'];g=p.read(gr['file']);host=g.get('sourceHostFile',g.get('hostOutputPath',g.get('evidence',{}).get('hostOutputPath')));assert host and p.sha(host)==s['sha256'];s['hostOutputFile']=str(host);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactSameWorldNativePixels':True,'hostByteIdentical':True})
assert sum(e['pixelCount'] for e in proof)==16777216
im=Image.fromarray(pix);out=A.save_png(im,T/'candidate/r07_c06-candidate-native-roi-v07.png');owner=A.save_png(Image.fromarray(own),T/'candidate/r07_c06-candidate-native-roi-v07-source-index.png');D=T/'qa/current-v07-native-20261013';D.mkdir(exist_ok=True);qa=A.write_qa(im,out,D/'internal');entries=[]
for name,box,rot in [('r3c4-left',[2797,2048,3277,3072],True),('r3c4-top',[2957,1888,4096,2208],False),('r3c4-bottom',[2957,2912,4096,3232],False),('r3c4-orphan-roi',[3084,2735,3277,2923],False)]:
 v=im.crop(box)
 if rot:v=v.transpose(Image.Transpose.ROTATE_90)
 e=A.save_png(v,D/(name+'.png'));e.update(name=name,cropLTRB=box,rotationCCW90=rot,nativePixelScale=1,actuallyViewed=False);entries.append(e)
external=[];N=Z/'r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.png';W=Z/'r07_c05/candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png';n=Image.open(N).convert('RGB');w=Image.open(W).convert('RGB')
for side,other in [('north',n),('west',w)]:
 band=Image.new('RGB',(4096,640) if side=='north' else (640,4096))
 if side=='north':band.paste(other.crop((0,3776,4096,4096)),(0,0));band.paste(im.crop((0,0,4096,320)),(0,320))
 else:band.paste(other.crop((3776,0,4096,4096)),(0,0));band.paste(im.crop((0,0,320,4096)),(320,0))
 for kind,i in [('segment',j) for j in range(4)]+[('junction',j) for j in range(1,4)]:
  if kind=='segment':v=band.crop((i*1024,0,(i+1)*1024,640)) if side=='north' else band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90);name=f'{side}-segment{i+1:02}'
  else:v=band.crop((i*1024-160,160,i*1024+160,480)) if side=='north' else band.crop((160,i*1024-160,480,i*1024+160));name=f'{side}-junction-{i*1024}'
  e=A.save_png(v,D/'external'/(name+'.png'));e.update(name=name,nativePixelScale=1,actuallyViewed=False);external.append(e)
registry={'schemaVersion':2,'createdAtUtc':p.now(),'tile':'r07_c06','status':'saved_native_sources_assembled_pending_visual_review','candidate':out,'sourceIndex':owner,'nativeSources':sources,'pixelProof':{'status':'passed','checkedPixels':16777216,'sources':proof},'previousRegistry':ref(prior_path),'readyPlan':ref(plan_path),'overlays':overlays,'internalQa':qa,'additionalQa':entries,'externalQa':external,'actualNorth':ref(N),'actualWest':ref(W),'newGenerationSubmitted':False,'sourceResampled':False,'blended':False,'recolored':False,'formalAccepted':False};p.write_json(T/'candidate/native-overlays-20261012-v07.json',registry,replace=False);print({'candidate':out,'registry':str(T/'candidate/native-overlays-20261012-v07.json'),'sourceRecords':len(sources),'fullNativePixelProof':True})
