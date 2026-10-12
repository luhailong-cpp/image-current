from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
m=json.loads((Q/'whole-object-trial-v05.json').read_text());sources={s['id']:(np.asarray(Image.open(s['file']).convert('RGB')),s['originInTwoTileCanvas']) for s in m['sources']};outs=[];canvas=Image.new('RGB',(8192,4096))
for i,o in enumerate(m['outputs']):
 a=np.asarray(Image.open(o['file']).convert('RGB'));base=np.asarray(Image.open(o['base']).convert('RGB'));sid=np.asarray(Image.open(o['sourceID']));replay=base.copy();counts={};assert set(np.unique(sid)).issubset({0,1,3})
 for k in [1,3]:
  y,x=np.where(sid==k);src,(ox,oy)=sources[k];sx=x+4096*i-ox;sy=y-oy;assert not len(x) or (sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254);replay[y,x]=src[sy,sx];counts[str(k)]={'pixels':len(x),'sourceCropExtent':None if not len(x) else [int(sx.min()),int(sy.min()),int(sx.max()+1),int(sy.max()+1)]}
 counts['0']={'pixels':int((sid==0).sum()),'source':'exact prior candidate RGB, same coordinate'}
 changed=np.any(a!=base,2);y,x=np.where(changed);mismatch=int(np.any(a!=replay,2).sum());assert mismatch==0 and sum(c['pixels'] for c in counts.values())==4096**2
 out={'tile':o['tile'],'file':o['file'],'sha256':sh(o['file']),'sourceID':o['sourceID'],'sourceIDSha256':sh(o['sourceID']),'base':o['base'],'baseSha256':sh(o['base']),'sourceRGBMismatchPixels':mismatch,'sourceCounts':counts,'changedPixels':int(changed.sum()),'changeBBox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'north256ChangedPixels':int(changed[:256].sum()),'outerWest256Unchanged':bool(np.array_equal(a[:,:256],base[:,:256])),'outerEast256Unchanged':bool(np.array_equal(a[:,-256:],base[:,-256:])),'south256Unchanged':bool(np.array_equal(a[-256:],base[-256:])),'resized':False,'warped':False,'colorAdjusted':False,'blended':False};assert out['sha256']==o['sha256'] and out['baseSha256']==o['baseSha256'];outs.append(out);canvas.paste(Image.fromarray(a),(4096*i,0))
evidence=[]
for n,box in [('minor-upper-left',[3550,440,3760,620]),('minor-upper-mid',[3690,455,3900,625]),('minor-left-foot',[3250,1000,3480,1220]),('shared-1',[3840,0,4352,1024]),('shared-2',[3840,1024,4352,2048])]:
 f=Q/f'whole-object-{n}-v05.png';canvas.crop(box).save(f);evidence.append({'file':str(f),'sha256':sh(f),'twoTileCanvasCrop':box,'nativeScale':True})
north=Image.new('RGB',(1024,512));north.paste(Image.open(R/'tiles/r08_c12.candidate-v15.png').crop((0,3840,1024,4096)),(0,0));north.paste(canvas.crop((4096,0,5120,256)),(0,256));nf=Q/'whole-object-r08north-1-v05.png';north.save(nf);evidence.append({'file':str(nf),'sha256':sh(nf),'composition':'r08c12v15 bottom256 above r09c12 trial top256, x0..1024; no resize'})
# The four foot/right crops have exactly the same pixels as the previously
# inspected v03 because only upper source ownership changed in v05.
same=[]
for name in ['complete-foot','right-foot','left-foot']:
 p=Q/f'whole-object-{name}-v05.png';old=Q/f'whole-object-{name}-v03.png';equal=np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(old)));same.append({'v05':str(p),'v03':str(old),'pixelIdentical':bool(equal)})
report={'timestamp':datetime.now(timezone.utc).isoformat(),'status':'exact_sourceRGB_replay_pass','trialVersion':'whole-object-v05','outputs':outs,'sources':m['sources'],'mask':m['mask'],'maskSha256':sh(m['mask']),'additionalEvidence':evidence,'reusedVisualEvidencePixelEquality':same,'totalPixelsReplayed':2*4096**2,'mismatchPixels':0,'priorCandidateLineageAudits':[str(R/'qa/r09_c11-v04/source-audit.json'),str(R/'qa/r09_c12-v08/source-audit.json')],'newNativeAudit':str(Q/'whole-joint-v01-review.json'),'mainTilesChanged':False,'formalAccepted':False}
wr(Q/'whole-object-v05-source-replay.json',report)
print(json.dumps({'replay':str(Q/'whole-object-v05-source-replay.json'),'outputs':[{k:o[k] for k in ['tile','sha256','changeBBox','north256ChangedPixels']} for o in outs],'sameFootCrops':same},indent=2))
