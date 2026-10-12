"""Publish only already-generated native repairs after root original-size review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,os,uuid
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def file(p):return {'path':str(p),'sha256':sha(p)}
def art(p):
 d=file(p)
 with Image.open(p) as im:d['pixels']=list(im.size)
 return d
def atomic(p,d):
 tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
def exclusive(p,d):
 if not p.exists():
  with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
def validate(m):
 for k in ['sourceCandidate','sourceContext','native','generationRecord','receipt','preparation','request','alpha','candidate','context','compositor','replay']:
  assert sha(m[k]['path'])==m[k]['sha256'],k
 for im in m['QAImages']:assert sha(im['path'])==im['sha256']
 base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'))
 new=np.array(Image.open(m['native']['path']).convert('RGB').crop(m['nativeCrop']))
 a=np.array(Image.open(m['alpha']['path']).convert('L'))
 x0,y0,x1,y1=m['pasteBoxIn4096'];old=base[y0:y1,x0:x1].copy()
 assert old.shape==new.shape and old.shape[:2]==a.shape
 base[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-a[:,:,None])+new.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
 assert np.array_equal(base,np.array(Image.open(m['candidate']['path']).convert('RGB')))
 assert np.array_equal(base,np.array(Image.open(m['context']['path']).convert('RGB'))[115:4211,115:4211])
 return base
jobs=[
 ('r14_c15','north-board-joint-20261012-v1','5ce10046c09c4e5ea101d0638cd62de9327869d487762c1804bca74ce971c627','North x230 board end joint extends naturally from the fixed north true core to the existing diagonal plank seam. Five native local/boundary images viewed; no duplicate groove or hard alpha edge seen. North full edge and west stone joins still require their complete review.'),
 ('r14_c14','north-far-east-ledges-20261012-v1','7288055c3509f4603e3006cd23914d5c4acae499180bd79869aafcf40cde8af3','Far-east upper timber bevel/shadow continues into the child; lower ledge and its bright rim, supports, paving and NW630 remain. Nine native images viewed including fixed join, shaped-alpha bottom thirds and east core join. Old x2842/2874 transition remains unresolved, so no full north pass.'),
 ('r13_c16','shore-water-join-20261012-v1','d7c2a1ac688debfbe915c84a05dcce0a254beabd18f22a64652c216307d0c9b3','Former x1173 straight stone/water division and three unapproved clipped leaves are gone. Eleven native repair crops and seven changed full-tile QA crops actually viewed; 46 pixel-identical full-tile/core-join images retain their prior observation. Six full seam bands, nine junctions and four tile edges are covered; west geometry locally connected with paving material watch, north/south pending, east is canvas boundary.')
]
out=[]
for tile,version,expected,observation in jobs:
 T=Z/tile;D=T/'repairs'/version;m=read(D/'composition.json')
 assert m['candidate']['sha256']==expected
 validate(m);L=read(T/'candidate/latest-assembly.json');p=read(T/'progress.json')
 assert L['candidate']['sha256'] in (m['sourceCandidate']['sha256'],expected)
 assert sha(p['candidate']) in (m['sourceCandidate']['sha256'],expected)
 q=D/'root-visual-qa-20261013.json'
 evidence=[dict(e,actuallyViewedAtOriginalPixelSize=True) for e in m['QAImages']]
 report={'schemaVersion':1,'reviewer':'root','recordedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':m['candidate'],'composition':file(D/'composition.json'),'actualNativeEvidence':evidence,'observations':[observation],'localRepairQA':'passed','scalarSourceAlphaReplayRechecked':True,'actualModel':None,'actualQuality':None,'generationCompletedBeforeNewModelRequirement':True,'formalAccepted':False}
 if tile=='r13_c16':
  changed=read(D/'root-changed-evidence/manifest.json')
  assert len(changed['changedEvidence'])==7 and len(changed['pixelIdenticalEvidenceCarriedForward'])==46
  report.update(changedBaseEvidenceActuallyViewed=[dict(e,actuallyViewedAtOriginalPixelSize=True) for e in changed['changedEvidence']],pixelIdenticalEvidenceCarriedForward=changed['pixelIdenticalEvidenceCarriedForward'],baseNativeQA=file(T/'review/root-native-full-qa-20261012/visual-qa.json'),internalArtQA='passed',internalSeamQA='passed')
 elif (D/'visual-qa.json').exists():report['independentLocalQA']=file(D/'visual-qa.json')
 exclusive(q,report)
 cp=T/'candidate'/f'{tile}-4k-{version}-root-reviewed.png';ctx=T/'candidate'/f'{tile}-context-4326-{version}-root-reviewed.png'
 for src,dst in [(m['candidate']['path'],cp),(m['context']['path'],ctx)]:
  if not dst.exists():shutil.copyfile(src,dst)
  assert sha(src)==sha(dst)
 prior={'candidate':m['sourceCandidate'],'context':m['sourceContext'],'previousSelectionManifest':L.get('manifest')} if L['candidate']['sha256']!=expected else read(T/'candidate'/f'{tile}-{version}-selected-manifest.json')['previousSelection']
 mp=T/'candidate'/f'{tile}-{version}-selected-manifest.json'
 exclusive(mp,{'schemaVersion':1,'tile':tile,'selectedAtUtc':datetime.now(timezone.utc).isoformat(),'previousSelection':prior,'localComposition':file(D/'composition.json'),'rootVisualQA':file(q),'candidate':art(cp),'context':art(ctx),'activeNativeCount':16,'formalAccepted':False,'newGenerationSubmitted':False})
 updates={'candidate':str(cp),'context':str(ctx),'assemblyManifest':str(mp),'rootLatestRepairQA':file(q),'currentVersion':version,'currentPatch':None,'formalAccepted':False,'updatedAt':datetime.now(timezone.utc).isoformat()}
 if tile=='r14_c15':
  updates.update(status='internal_visual_pass_north_joint_repaired_remaining_external_pending',internalArtQA='internal_visual_pass',internalSeamQA='passed',externalNeighborSeamQA='north_N01_local_repaired_full_review_pending_west_failed_east_south_pending',nextStep='Review full current north core join; repair west W01/W02/W03/material only through a verified GPT Image 2.5 route.')
 elif tile=='r14_c14':
  updates.update(status='far_east_native_repair_published_remaining_north_west_pending',externalNeighborSeamQA='far_east_local_pass_old_north_endpoint_and_west_pending',nextStep='Resolve old north x2842/2874 transition and frozen common corner through a verified GPT Image 2.5 route; no whole-edge acceptance.')
 else:
  updates.update(status='internal_art_and_seams_pass_external_pending',internalArtQA='passed',internalSeamQA='passed',externalNeighborSeamQA='west_local_geometry_material_watch_north_south_pending_east_canvas_boundary',nextStep='Use preserved candidate for downstream anchors; finish north/south neighbor joins when available and inspect west paving material watch.')
 p.update(updates);atomic(T/'progress.json',p)
 L.update({k:v for k,v in updates.items() if k not in ['candidate','context','assemblyManifest']},candidate=art(cp),context=art(ctx),manifest=file(mp),rootLatestRepairQA=file(q));atomic(T/'candidate/latest-assembly.json',L)
 preview=D/'root-preview-only-1024.png'
 if not preview.exists():
  with Image.open(cp) as im:
   with preview.open('xb') as f:im.resize((1024,1024),Image.Resampling.LANCZOS).save(f,format='PNG')
 out.append({'tile':tile,'candidate':art(cp),'manifest':file(mp),'rootVisualQA':file(q),'formalAccepted':False})
print(json.dumps(out))
