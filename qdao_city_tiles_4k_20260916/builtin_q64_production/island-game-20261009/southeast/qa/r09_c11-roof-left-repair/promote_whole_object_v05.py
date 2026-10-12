from pathlib import Path
from PIL import Image
import json,hashlib,shutil
import numpy as np
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;R=Q.parent.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
proposal=Q/'whole-object-v05-proposal.json';d=rd(proposal);results=[];images=[]
for i,(tid,oldver,newver) in enumerate([('r09_c11','v04','v05'),('r09_c12','v08','v09')]):
 o=d['outputs'][i];trial=Path(o['file']);base=Path(o['base']);overlayfile=Path(o['sourceID'])
 assert sh(trial)==o['sha256'] and sh(base)==o['baseSha256'] and sh(overlayfile)==o['sourceIDSha256']
 prev=R/'qa'/f'{tid}-{oldver}';audit=rd(prev/'source-audit.json');assert audit['sha256']==sh(base)
 baseid=Path(audit['sourceID']);assert sh(baseid)==audit['sourceIDSha256']
 owners=np.array(Image.open(baseid),dtype=np.uint16);assert owners.shape==(4096,4096)
 sources=[{k:s[k] for k in ['id','file','sha256','originInTile']} for s in audit['sources']]
 assert set(np.unique(owners)).issubset({s['id'] for s in sources}) and np.all(owners>0)
 overlay=np.asarray(Image.open(overlayfile));assert set(np.unique(overlay))=={0,1,3}
 for s in d['sources']:
  native=Path(s['file']);assert sh(native)==s['sha256'];origin=[s['originInTwoTileCanvas'][0]-i*4096,s['originInTwoTileCanvas'][1]]
  same=next((n for n in sources if Path(n['file']).resolve()==native.resolve() and n['originInTile']==origin),None)
  if not same:
   same={'id':max(q['id'] for q in sources)+1,'file':str(native),'sha256':s['sha256'],'originInTile':origin};sources.append(same)
  owners[overlay==s['id']]=same['id']
 arr=np.asarray(Image.open(trial).convert('RGB'));assert arr.shape==(4096,4096,3)
 replay=np.zeros_like(arr);active=[]
 for s in sources:
  ys,xs=np.where(owners==s['id'])
  if not len(ys):continue
  p=Path(s['file']);assert sh(p)==s['sha256'];native=np.asarray(Image.open(p).convert('RGB'));assert native.shape==(1254,1254,3)
  sx=xs-s['originInTile'][0];sy=ys-s['originInTile'][1]
  assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254
  replay[ys,xs]=native[sy,sx];errors=int(np.count_nonzero(np.any(replay[ys,xs]!=arr[ys,xs],axis=1)));assert errors==0
  s.update({'selectedPixels':int(len(xs)),'mismatchedPixels':errors,'nativeSize':[1254,1254]});active.append(s)
 assert np.array_equal(replay,arr) and sum(s['selectedPixels'] for s in active)==4096**2
 folder=R/'qa'/f'{tid}-{newver}';folder.mkdir(exist_ok=True)
 out=R/'tiles'/f'{tid}.candidate-{newver}.png'
 if out.exists():assert sh(out)==sh(trial)
 else:shutil.copy2(trial,out)
 assert sh(out)==sh(trial)
 idfile=folder/'source-id.png';Image.fromarray(owners).save(idfile)
 rec={'file':str(out),'sha256':sh(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Byte-identical promotion of root-reviewed whole-object trial; base source-ID and source manifest flattened with new exact native 0/1 ownership. No RGB changes, resampling, shifting, blending or recoloring.','sources':active,'sourceID':str(idfile),'sourceIDSha256':sh(idfile),'sourceIdRule':'For tile pixel (x,y) with source ID k use native RGB(x-originInTile[0], y-originInTile[1]).','proposal':str(proposal),'proposalSha256':sh(proposal),'base':str(base),'baseSha256':sh(base),'baseSourceAudit':str(prev/'source-audit.json'),'baseSourceAuditSha256':sh(prev/'source-audit.json'),'baseSourceID':str(baseid),'baseSourceIDSha256':sh(baseid),'trial':str(trial),'trialSha256':sh(trial),'fullCoverage':True,'allContributionsPixelExact':True,'mismatchedPixelCount':0,'totalReplayedPixels':4096**2,'actualModel':None,'actualQuality':None,'status':'promoted_pending_changed_crop_QA','formalAccepted':False}
 wr(Path(str(out)+'.generation.json'),rec);wr(folder/'source-audit.json',rec)
 im=Image.open(out).convert('RGB');old=Image.open(base).convert('RGB');entries=[]
 for e in rd(prev/'seams.json')['entries']:
  box=e['sourceCrop'];p=folder/f"{e['id']}.png";im.crop(box).save(p);same=im.crop(box).tobytes()==old.crop(box).tobytes()
  entries.append({'id':e['id'],'direction':e['direction'],'sourceCrop':box,'file':str(p),'sha256':sh(p),'unchanged':same,'priorEvidence':str(prev/f"{e['id']}.png"),'status':'pixel_identical_inherit_prior_review' if same else 'pending_direct_changed_crop_review'})
 wr(folder/'seams.json',{'createdAt':now(),'candidate':str(out),'candidateSha256':sh(out),'operation':'Exact original-pixel seam crops; no resampling.','seamCount':24,'entries':entries,'formalAccepted':False})
 for rr in range(1,4):
  for cc in range(1,4):
   name=f'junction_{rr}{cc}';box=[cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256];p=folder/f'{name}.png';im.crop(box).save(p);same=im.crop(box).tobytes()==old.crop(box).tobytes()
   entries.append({'id':name,'sourceCrop':box,'file':str(p),'sha256':sh(p),'unchanged':same,'priorEvidence':str(prev/f'{name}.png'),'status':'pixel_identical_inherit_prior_review' if same else 'pending_direct_changed_crop_review'})
 assert len(entries)==33
 delta={'base':str(base),'baseSha256':sh(base),'candidate':str(out),'candidateSha256':sh(out),'entries':entries,'changedEntries':[e['id'] for e in entries if not e['unchanged']]};wr(folder/'prior-reviewed-pixel-replay.json',delta)
 # Preview is explicitly non-production; every inspected seam/junction retains native scale.
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png')
 images.append(im);results.append({'tile':tid,'candidate':str(out),'sha256':sh(out),'sourceCount':len(active),'replayedPixels':4096**2,'mismatchPixels':0,'changedEntries':delta['changedEntries'],'QA':str(folder),'sourceAudit':str(folder/'source-audit.json'),'sourceAuditSha256':sh(folder/'source-audit.json')})
external=Q/'promoted-external';external.mkdir(exist_ok=True);ext=[]
for i in range(4):
 y=i*1024;im=Image.new('RGB',(512,1024));im.paste(images[0].crop((3840,y,4096,y+1024)),(0,0));im.paste(images[1].crop((0,y,256,y+1024)),(256,0));p=external/f'shared-{i+1}.png';im.save(p);ext.append({'file':str(p),'sha256':sh(p),'seamX':256,'tileYRange':[y,y+1024],'noResize':True})
north=Image.open(R/'tiles/r08_c12.candidate-v15.png').convert('RGB')
for i in range(4):
 x=i*1024;im=Image.new('RGB',(1024,512));im.paste(north.crop((x,3840,x+1024,4096)),(0,0));im.paste(images[1].crop((x,0,x+1024,256)),(0,256));p=external/f'north-{i+1}.png';im.save(p);ext.append({'file':str(p),'sha256':sh(p),'seamY':256,'tileXRange':[x,x+1024],'noResize':True})
wr(Q/'promoted-manifest.json',{'createdAt':now(),'status':'promoted_pending_changed_crop_QA','outputs':results,'externalEvidence':ext,'totalReplayedPixels':33554432,'mismatchPixels':0,'sourceIDFlattened':True,'mainProgressOrProductionStateUpdated':False,'formalAccepted':False})
print(json.dumps(results,indent=2))
