from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, os
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p): return np.asarray(Image.open(p).convert('RGB'))
def wr(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
results=[]
for kind in ['rect','natural']:
 m=json.loads((Q/f'{kind}-trial-v01.json').read_text())
 sources={s['id']:(arr(s['file']),s['originInTwoTileCanvas']) for s in m['sources']}
 rec=[];ims=[]
 for i,o in enumerate(m['outputs']):
  trial=arr(o['file']);base=arr(o['base']);sid=np.asarray(Image.open(o['sourceID']))
  assert trial.shape==base.shape==(4096,4096,3) and sid.shape==(4096,4096)
  assert set(np.unique(sid)).issubset({0,1,2})
  replay=base.copy();counts={}
  for k in [1,2]:
   yy,xx=np.where(sid==k);src,(ox,oy)=sources[k];sx=xx+i*4096-ox;sy=yy-oy
   assert len(sx)==0 or (sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254)
   replay[yy,xx]=src[sy,sx];counts[str(k)]={'pixelCount':len(xx),'sourceCropExtent':None if len(xx)==0 else [int(sx.min()),int(sy.min()),int(sx.max())+1,int(sy.max())+1]}
  counts['0']={'pixelCount':int((sid==0).sum()),'source':'exact prior candidate RGB, same coordinate'}
  mismatch=np.any(replay!=trial,2);changed=np.any(base!=trial,2);yy,xx=np.where(changed)
  unchangedEdges={name:bool(np.array_equal(trial[b],base[b])) for name,b in [('north256',np.s_[:256,:]),('south256',np.s_[-256:,:]),('west256',np.s_[:,:256]),('east256',np.s_[:,-256:])]}
  d={'tile':o['tile'],'trial':o['file'],'sha256':sh(o['file']),'mask':o['sourceID'],'maskSha256':sh(o['sourceID']),'base':o['base'],'baseSha256':sh(o['base']),'sourceIDs':counts,'sourceRGBMismatchPixels':int(mismatch.sum()),'fullCoveragePixels':int(sum(v['pixelCount'] for v in counts.values())),'changedPixelsVsBase':int(changed.sum()),'changeBBox':None if len(xx)==0 else [int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],'north256ChangedPixels':int(changed[:256].sum()),'edgeBandsExactVsBase':unchangedEdges,'pixelReplayPass':not mismatch.any(),'resized':False,'blended':False,'colorAdjusted':False,'formalAccepted':False}
  assert d['pixelReplayPass'] and d['fullCoveragePixels']==4096**2 and d['sha256']==o['sha256'] and d['baseSha256']==o['baseSha256']
  rec.append(d);ims.append(Image.fromarray(trial))
 canvas=Image.new('RGB',(8192,4096));canvas.paste(ims[0],(0,0));canvas.paste(ims[1],(4096,0))
 f=Q/f'complete-top-{kind}-v01.png';canvas.crop((3300,0,4554,256)).save(f)
 results.append({'trialType':kind,'outputs':rec,'sources':m['sources'],'topEvidence':{'file':str(f),'sha256':sh(f),'canvasCrop':[3300,0,4554,256]},'provenanceScope':'Incremental exact replay against immutable prior candidates plus the two new native images; prior native lineage remains in each base candidate source-audit.'})
nativeAudit=[]
for pid in ['r09_c11_roof_color_upper_v01','r09_c11_roof_color_lower_v01']:
 p=R/'native'/f'{pid}.png';rp=Path(str(p)+'.generation.json');r=json.loads(rp.read_text());prompt=Path(r['prompt']);receipt=Path(r['evidence']['toolReceipt'])
 refs=[{'file':x['file'],'exists':Path(x['file']).is_file(),'shaMatches':Path(x['file']).is_file() and sh(x['file'])==x['sha256']} for x in r['references']]
 d={'file':str(p),'sha256':sh(p),'dimensions':list(Image.open(p).size),'pngShaMatchesRecord':sh(p)==r['sha256'],'generationRecord':str(rp),'generationRecordSha256':sh(rp),'promptExists':prompt.is_file(),'promptNonempty':bool(prompt.read_text().strip()),'promptShaMatches':sh(prompt)==r['promptSha256'],'references':refs,'receipt':str(receipt),'receiptExists':receipt.is_file(),'receiptSha256':sh(receipt),'actualModel':r['actualModel'],'actualQuality':r['actualQuality'],'configurationIsTargetOnly':'configSnapshotTargetOnly' in r,'submittedParameters':r['submittedParameters']}
 assert d['dimensions']==[1254,1254] and d['pngShaMatchesRecord'] and d['promptShaMatches'] and all(x['shaMatches'] for x in refs) and d['receiptExists'] and d['actualModel'] is None and d['actualQuality'] is None
 nativeAudit.append(d)
u=arr(R/'native/r09_c11_roof_color_upper_v01.png');ctx=arr(R/'guides/r09_c11_roof_color_lower_v01.native-context.png')
anchor={'upperSourceCrop':[0,600,1254,1254],'lowerContextDestination':[0,0,1254,654],'pixelCount':1254*654,'mismatchPixels':int(np.any(u[600:]!=ctx[:654],2).sum()),'note':'Exact input anchor is proven. Generated output is not asserted to be immutable and visually drifted at its left boundary.'}
assert anchor['mismatchPixels']==0
out={'timestamp':datetime.now(timezone.utc).isoformat(),'status':'replay_pass_visual_rejected_do_not_promote','maximumNativeCallsThisRound':2,'successfulNewNativeCount':2,'pendingRequest':False,'additionalGenerationAuthorizedInThisRound':False,'actualModel':None,'actualQuality':None,'nativeAudit':nativeAudit,'trueOverlapAnchor':anchor,'trials':results,'baseLineageAudits':[str(R/'qa/r09_c11-v04/source-audit.json'),str(R/'qa/r09_c12-v08/source-audit.json')],'formalAccepted':False}
wr(Q/'trial-source-replay.json',out)
print(json.dumps({'replayPass':all(x['pixelReplayPass'] for t in results for x in t['outputs']),'trials':[{ 'kind':t['trialType'],'outputs':[{k:o[k] for k in ['tile','sha256','changedPixelsVsBase','changeBBox','north256ChangedPixels','sourceRGBMismatchPixels']} for o in t['outputs']]} for t in results]},indent=2))
