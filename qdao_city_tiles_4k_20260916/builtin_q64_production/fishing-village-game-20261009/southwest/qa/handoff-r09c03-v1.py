import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
ap=Q/'full-tile-r09_c03-assembly.json';assembly=read(ap);tp=Q/'pair-r09c03-c04-v1-trace.json';t=read(tp)
ha=Q/'full-tile-r09_c03-root-horizontal-audit.json';va=Q/'r09_c03-internal-vertical-intersection-qa-v1.json';assert ha.exists()
native=[]
for s in assembly['sources']:
 p=Path(s['path']);assert ref(p)['sha256']==s['sha256'];rp=Path(s['record']);assert ref(rp)['sha256']==s['recordSha256'];g=read(rp)
 for ext in ['.prompt.txt','.request.json','.receipt.json']:
  q=p.with_suffix(ext);assert q.exists()
 with Image.open(p) as im:assert im.size==(1254,1254)
 native.append({'source':ref(p),'generationRecord':ref(rp),'prompt':ref(p.with_suffix('.prompt.txt')),'request':ref(p.with_suffix('.request.json')),'receipt':ref(p.with_suffix('.receipt.json'))})
deltas=[]
for i,v in enumerate(t['tiles']):
 a=np.array(Image.open(t['inputs'][i]['context']['path']).convert('RGB'));b=np.array(Image.open(v['context']['path']).convert('RGB'));d=np.any(a!=b,axis=2);ys,xs=np.where(d)
 deltas.append({'tile':v['tile'],'changedPixelCount':int(d.sum()),'changedContextBBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'coreChangedPixelCount':int(d[115:4211,115:4211].sum()),'southHaloChangedPixelCount':int(d[4211:].sum())})
notes=['Golden foliage, pillar profile and tree branches continuous.','Pillar plinth, tree trunk and sandy ground continuous.','Sand-to-paving border and stone joints continuous.','Paving joints and small inset stone continuous.','Lower paving and cracks continuous.']
audit={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed_internal_39_and_shared_east_5_native_visual_qa','tiles':['r09_c03','r09_c04'],'assembly':ref(ap),'internalQa':{'count':39,'verticalAndIntersections':ref(va),'horizontal':ref(ha)},'eastPairTrace':ref(tp),'sharedViews':[dict(v,result='pass',note=notes[i],viewedAtOriginalDimensions=True) for i,v in enumerate(t['qa'])],'allSharedViewsViewedAtOriginalDimensions':True,'sourcePixelIdentity':t['sourcePixelIdentity'],'nativePixelsResampled':False,'inputDeltas':deltas,'notes':['Pair uses latest block2x2 r09_c04 context; all non-overlap neighbor pixels unchanged.','Southwestern r09_c04 halo corner changed within shared west overlap; unify corner with future r10_c03.','No drawing by code, no feather, no resize or color adjustment. No game/client/capacity tests.'],'formalAcceptedCount':0}
au=Q/'r09_c03-final-art-audit-v1.json';assert not au.exists();au.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
handoff={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r09_c03','status':'native_art_candidate_ready_for_root_canonical_export','scope':'16 native1254 patches, internal39 native QA, latest east neighbor joined and5 native QA passed','finalTile':t['tiles'][0],'neighborUpdated':t['tiles'][1],'finalPairContext':t['context'],'trace':ref(tp),'audit':ref(au),'internalAssembly':ref(ap),'native':native,'actualModel':None,'actualQuality':None,'configurationDisclosure':'Builtin tool does not expose model or quality selectors or actual returned model/quality; all remain null.','restoredNetworkFirstSuccess':{'native':ref(Z/'native/r09_c03_p03_02_v1.png'),'receipt':ref(Z/'native/r09_c03_p03_02_v1.receipt.json')},'nextTile':'r10_c03','nextNorthAnchor':t['tiles'][0]['context'],'nextEastAnchor':ref(Q/'block2x2-r09r10c04c05-v1-r10_c04-context-native.png'),'canonicalExportBy':'root','globalIndexWritten':False,'gitWritten':False}
p=Q/'r09_c03-final-art-handoff-v1.json';assert not p.exists();p.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'handoff':ref(p),'audit':ref(au),'finalTile':t['tiles'][0],'neighborUpdated':t['tiles'][1]}))

