import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';prefix='repair-r09_c06-final-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def inp(r):p=Path(r['path']);assert sha(p)==r['sha256'];return p
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def savepng(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return ref(p)
def savenpy(p,a):
 assert not p.exists();np.save(p,a);assert np.array_equal(np.load(p),a);return ref(p)
def savejson(p,a):
 assert not p.exists();p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');return ref(p)
object_trace_path=QA/'repair-r09_c06-objects-v4-trace.json';obj=read(object_trace_path)
integration_path=QA/'repair-r09_c06-bcomplete-v3.integration.json';b=read(integration_path)
manifest={'schemaVersion':1,'outputPrefix':prefix,'objectRepairsTrace':ref(object_trace_path),'longObjectIntegration':ref(integration_path),'operation':'hard-mask original B source pixels over accepted A/C/D and counter-corner repair context','noResize':True,'noFeather':True,'noColourCorrection':True,'formalAcceptedCount':0}
manifestref=savejson(QA/(prefix+'.manifest.json'),manifest)
current=rgb(inp(obj['context']));prior=current.copy();ids=np.load(inp(obj['completeContextSourceIds']));assert current.shape==(4326,4326,3) and ids.shape==(4326,4326)
native=rgb(inp(b['sourceNativeComposite']));nids=np.load(inp(b['sourceNativeIds']));mask=np.load(inp(b['objectMask'])).astype(bool);x1,y1,x2,y2=b['contextBox'];assert native.shape==(y2-y1,x2-x1,3) and nids.shape==mask.shape==native.shape[:2]
count=len(obj['repairsInOrder']);assert ids.max()==count
current[y1:y2,x1:x2][mask]=native[mask];ids[y1:y2,x1:x2][mask]=nids[mask]+count
assert np.array_equal(current[y1:y2,x1:x2][~mask],prior[y1:y2,x1:x2][~mask])
source_records=[{'sourceId':0,'role':'unchanged stable native assembly','source':obj['baseContext'],'assemblyTrace':obj['baseAssembly']}]
base=rgb(inp(obj['baseContext']));assert np.array_equal(current[ids==0],base[ids==0])
for order,item in enumerate(obj['repairsInOrder'],1):
 box=item['contextBox'];xx1,yy1,xx2,yy2=box;pix=rgb(inp(item['repair']));sel=ids[yy1:yy2,xx1:xx2]==order;assert np.array_equal(current[yy1:yy2,xx1:xx2][sel],pix[sel]);assert (ids==order).sum()==sel.sum();source_records.append({'sourceId':order,'repairId':item['id'],'source':item['repair'],'contextBox':box,'trace':item['trace'],'retainedPixels':int(sel.sum())})
for source in b['nativeSources']:
 sid=source['sourceId']+count;ox,oy=source['sourceOriginInComposite'];xx1,yy1=x1+ox,y1+oy;pix=rgb(inp(source));sel=ids[yy1:yy1+1254,xx1:xx1+1254]==sid;assert np.array_equal(current[yy1:yy1+1254,xx1:xx1+1254][sel],pix[sel]);assert (ids==sid).sum()==sel.sum();source_records.append({'sourceId':sid,'repairId':'b-complete-post-'+str(source['sourceId']),'source':{k:source[k] for k in ['path','sha256']},'contextBox':[xx1,yy1,xx1+1254,yy1+1254],'trace':b['sourceTrace'],'retainedPixels':int(sel.sum())})
contextref=savepng(QA/(prefix+'-context-native.png'),current);core=current[115:4211,115:4211].copy();coreref=savepng(QA/(prefix+'-candidate-4096.png'),core);idsref=savenpy(QA/(prefix+'-context-source-ids.npy'),ids)
qa=[];coverage=np.zeros((4326,4326),bool)
boxes={'a-fish-leftwood':[485,885,1739,2139],'b-centerwood':[1240,960,2494,2214],'c-rail-redtray':[2500,630,3754,1884],'d-frontpost-paving':[2460,2520,3714,3774],'a-complete-posts':[260,-40,1514,1214],'d-floor':[2600,2840,3854,4094]}
bm=read(QA/'repair-r09_c06-bcomplete-v3.manifest.json')
for name,box in bm['qaCrops'].items():boxes['b-complete-'+name]=[box[0]+1360,box[1]+500,box[2]+1360,box[3]+500]
for name,box in boxes.items():
 xx1,yy1,xx2,yy2=[v+115 for v in box];crop=current[yy1:yy2,xx1:xx2];r=savepng(QA/(prefix+'-'+name+'-100pct.png'),crop);r.update(name=name,tileBox=box,contextBox=[xx1,yy1,xx2,yy2],size=[crop.shape[1],crop.shape[0]],operation='exact native integer crop only');qa.append(r);coverage[yy1:yy2,xx1:xx2]=True
changed=np.any(current!=base,axis=2);assert not (changed&~coverage).any()
assembly=read(inp(obj['baseAssembly']));canonical=[]
for item in assembly['qa']:
 xx1,yy1,xx2,yy2=item['sourceBox'];crop=core[yy1:yy2,xx1:xx2];old=rgb(Path(item['file']));assert sha(item['file'])==item['sha256'];equal=np.array_equal(crop,old)
 r={'original':{'path':item['file'],'sha256':item['sha256']},'coreBox':item['sourceBox'],'unchangedPixelsInherited':bool(equal)}
 if equal:r['current']=r['original'];r['qaMethod']='exact pixel identity inherits prior full-tile visual audit'
 else:
  name=Path(item['file']).name.replace('full-tile-r09_c06',prefix+'-canonical');r['current']=savepng(QA/name,crop);diff=np.any(crop!=old,axis=2);assert not (diff&~coverage[yy1+115:yy2+115,xx1+115:xx2+115]).any();r['changedPixels']=int(diff.sum());r['qaMethod']='all changed pixels lie within original-dimension final repair views; unaffected pixels inherit original audit'
 canonical.append(r)
record={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest':manifestref,'script':ref(Path(__file__)),'context':contextref,'candidate':dict(coreref,cropFromContext=[115,115,4211,4211],globalCoreBox=assembly['output']['globalCoreBox']),'completeContextSourceIds':idsref,'sourceLegend':source_records,'objectRepairsTrace':ref(object_trace_path),'longObjectIntegration':ref(integration_path),'validation':{'allFinalPixelsExactlyMatchRecordedOriginalSource':True,'allSourcesHashVerified':True,'allSavedPixelsVerified':True,'allChangedPixelsCoveredByFinalOriginalDimensionViews':True,'outsideBMaskUnchangedFromObjectsV4':True,'noResize':True,'noFeather':True,'noColourCorrection':True},'qa':qa,'canonicalSeamQa':canonical,'canonicalCounts':{'total':len(canonical),'exactPixelInherited':sum(x['unchangedPixelsInherited'] for x in canonical),'affected':sum(not x['unchangedPixelsInherited'] for x in canonical)},'status':'final_internal_candidate_pending_visual_signoff_external_joins_not_verified','formalAcceptedCount':0,'externalJoinsVerified':False}
trace=savejson(QA/(prefix+'-trace.json'),record);print(json.dumps({'context':contextref,'candidate':coreref,'sourceIds':idsref,'trace':trace,'canonicalCounts':record['canonicalCounts'],'finalQaCrops':len(qa)}))
