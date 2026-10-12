from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
name=sys.argv[1];mode=sys.argv[2];tid='r05_c11'
dp=ZONE/'tiles'/f'{name}.png.derivation.json';d=read(dp);im=Image.open(d['file']).convert('RGB')
assert d['tileId']==tid and sha(d['file'])==d['sha256']
if mode=='boundaries':
 out=ZONE/'qa'/f'{name}-boundaries';assert not out.exists();out.mkdir();sources=[]
 for side,neigh in [('top','r04_c11'),('right','r05_c12')]:
  s=read(ZONE/f'selection-{neigh}.json');p=Path(s.get('candidatePath',ZONE/'tiles'/f'{neigh}.png'));n=Image.open(p).convert('RGB')
  for k in range(4):
   if side=='top':
    x=k*1024;patch=Image.new('RGB',(1024,512));patch.paste(n.crop((x,3840,x+1024,4096)),(0,0));patch.paste(im.crop((x,0,x+1024,256)),(0,256))
   else:
    y=k*1024;patch=Image.new('RGB',(512,1024));patch.paste(im.crop((3840,y,4096,y+1024)),(0,0));patch.paste(n.crop((0,y,256,y+1024)),(256,0))
   patch.save(out/f'{side}-{k+1}-100pct.png')
  sources.append({'side':side,'tileId':neigh,'file':p.as_posix(),'sha256':sha(p)})
 write(out/'provenance.json',{'candidate':d['file'],'candidateSha256':d['sha256'],'sources':sources,'operation':'exact unscaled native256pixel strip each side','status':'pending_visual_review'})
 print(out.as_posix())
elif mode=='review':
 failed=set(sys.argv[3:]);qa=Path(d['inspectionCrops']);files=sorted(qa.glob('*.png'));assert len(files)==49
 entries=[];s=read(ZONE/f'selection-{tid}.json')
 for p in files:
  with Image.open(p) as crop:size=list(crop.size)
  e={'file':p.as_posix(),'sha256':sha(p),'size':size,'resized':False,'inspectionScale':1,'status':'requires_native_repair' if p.name in failed else 'passed_visual_100pct'}
  if p.name.startswith('core-'):
   r,c=map(int,p.name.split('-')[1:3]);ident=s['cores'][r-1][c-1];g=read(ZONE/'native'/f'{ident}.png.generation.json');join=read(ZONE/'qa'/f'{ident}.joins.json')
   assert g['sha256']==join['nativeSha256'] and join['status'].startswith('passed_')
   e['reuseEvidence']={'nativeId':ident,'nativeSha256':g['sha256'],'previousNativeReview':(ZONE/'qa'/f'{ident}.joins.json').as_posix(),'coreUnchanged':True}
  entries.append(e)
 bdir=ZONE/'qa'/f'{name}-boundaries';bound=read(bdir/'provenance.json');bound.update(status='passed_all8_native_boundaries',reviewedAtUtc=now());write(bdir/'provenance.json',bound)
 review={'tileId':tid,'candidatePath':d['file'],'sha256':d['sha256'],'size':[4096,4096],'reviewer':'repair_recovery','reviewedAtUtc':now(),'nativeCoreCount':16,'internalSeamCount':24,'internalCrossCount':9,'status':'requires_native_repair' if failed else 'complete_internal_QA_passed','internalReview':'requires_native_repair' if failed else 'passed16core24seam9cross_native1to1','inspectedCrops':entries,'pendingIssues':sorted(failed),'externalSeams':{'top':'passed_all4segments','right':'passed_all4segments','left':'pending_neighbor','bottom':'pending_neighbor'},'externalReview':(bdir/'provenance.json').as_posix(),'formalAccepted':False,'finalArtUpscaled':False,'blending':'none'}
 rp=ZONE/'qa'/f'{name}-review.json';assert not rp.exists();write(rp,review)
 d.update(internalReview=review['internalReview'],status=review['status'],reviewPath=rp.as_posix(),pendingIssues=review['pendingIssues'],externalSeams=review['externalSeams']);write(dp,d)
 s.update(internalReview=d['internalReview'],pendingIssues=review['pendingIssues'],reviewPath=rp.as_posix(),selectionIsPartialCandidate=False,updatedAtUtc=now());write(ZONE/f'selection-{tid}.json',s)
 p=ZONE/'qa/r05_c11-sol-progress.json';q=read(p);q.update(status=review['status'],candidatePath=d['file'],candidateSha256=d['sha256'],reviewPath=rp.as_posix(),formalAccepted=False,inFlightImagegenCount=0,updatedAtUtc=now());write(p,q)
 print(json.dumps({'review':rp.as_posix(),'status':review['status'],'sha256':d['sha256']}))
