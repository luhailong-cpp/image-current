from pathlib import Path
from PIL import Image
import numpy as np,importlib.util,json
import repair as r
D=r.R/'stair-combined';D.mkdir(exist_ok=True)
box=[19853,39320,21107,40960]
base,src=r.crop(box);old=np.array(base)
up=r.read(r.R/'stair-upper-v01/generation.json');lo=r.read(r.R/'stair-lower-v01/generation.json')
for g in [up,lo]:
 assert r.sha(g['file'])==g['sha256']
 for ref in g['references']:assert r.sha(ref['file'])==ref['sha256']
a=np.array(Image.open(up['file']).convert('RGB'));b=np.array(Image.open(lo['file']).convert('RGB'))
spec=importlib.util.spec_from_file_location('quilt',r.SW/'local_repairs.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
band=692;offset=386
seam=q.minimum_error_path(a[band:band+115].transpose(1,0,2),b[band-offset:band-offset+115].transpose(1,0,2),2)
m=q.inclusion_mask(seam,2).T.astype(np.uint32)[...,None]
new=old.copy();new[:band]=a[:band];new[band:band+115]=((a[band:band+115].astype(np.uint32)*(255-m)+b[band-offset:band-offset+115].astype(np.uint32)*m+127)//255).astype(np.uint8);new[band+115:]=b[band+115-offset:]
l,rr=410,915
t,bb=195,1590
alpha=np.zeros(old.shape[:2],np.uint8);alpha[t:bb,l:rr]=255
paths={}
for name,x,reverse in [('left',l,False),('right',rr-115,True)]:
 before=old[t:bb,x:x+115];after=new[t:bb,x:x+115]
 if reverse:before=before[:,::-1];after=after[:,::-1]
 p=q.minimum_error_path(before,after,2);am=q.inclusion_mask(p,2)
 if reverse:am=am[:,::-1]
 alpha[t:bb,x:x+115]=np.minimum(alpha[t:bb,x:x+115],am);paths[name]=p.tolist()
# Keep wood entirely unchanged, with only two-pixel blend at the original stone start.
alpha[t,l:rr]=np.minimum(alpha[t,l:rr],85);alpha[t+1,l:rr]=np.minimum(alpha[t+1,l:rr],170)
p=q.minimum_error_path(old[bb-115:bb,l:rr][::-1].transpose(1,0,2),new[bb-115:bb,l:rr][::-1].transpose(1,0,2),2)
alpha[bb-115:bb,l:rr]=np.minimum(alpha[bb-115:bb,l:rr],q.inclusion_mask(p,2).T[::-1]);paths['bottom']=p.tolist()
# Preserve the two lower original bevels whose native peak shifted by 3-4 px.
# The surrounding material still comes from the native outputs; no geometry is synthesized.
protected=[]
for wy in [40507,40734]:
 cy=wy-box[1];alpha[cy-8:cy+9]=0
 alpha[cy-10]=np.minimum(alpha[cy-10],170);alpha[cy-9]=np.minimum(alpha[cy-9],85)
 alpha[cy+9]=np.minimum(alpha[cy+9],85);alpha[cy+10]=np.minimum(alpha[cy+10],170)
 protected.append([box[0],wy-8,box[2],wy+9])
weight=alpha.astype(np.uint32)[...,None];out=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
mask=alpha>0;change=np.any(old!=out,axis=2)
assert not change[~mask].any()
assert np.array_equal(old[:195],out[:195])
assert np.array_equal(old[-50:],out[-50:])
assert np.array_equal(old[:,915:],out[:,915:])
Image.fromarray(old).save(D/'input.png',optimize=True)
Image.fromarray(out).save(D/'premixed.png',optimize=True)
Image.fromarray(alpha).save(D/'alpha.png')
Image.fromarray(np.uint8(mask)*255).save(D/'copy-mask.png')
# Raw native material union is an audit intermediate, never the delivery mask.
Image.fromarray(new).save(D/'native-union.png',optimize=True)
ys,xs=np.nonzero(mask)
def linestat(z):
 v=z[205:1550].astype(float)
 return {'meanAbsNeighborJump':float(np.abs(v[:,627]-v[:,626]).mean()),'p95AbsNeighborJump':float(np.quantile(np.abs(v[:,627]-v[:,626]).mean(axis=1),.95))}
stats={'before':linestat(old),'after':linestat(out),'changedPixels':int(change.sum()),'maskPixels':int(mask.sum()),'outsideMaskUnchanged':True,'woodRows0to194Unchanged':True,'rightParapetAndContextX915OnUnchanged':True,'last50WorldRows40910to40959Unchanged':True,'sourceCandidatesAndContextsUnchanged':all(r.sha(s['file'])==s['sha256'] and r.sha(s['context'])==s['contextSha256'] for s in src)}
rec={'name':'north-vertical-stair-combined','status':'proposal_pending_parent_visual_review','worldBox':box,'affectedWorldBox':[box[0]+int(xs.min()),box[1]+int(ys.min()),box[0]+int(xs.max())+1,box[1]+int(ys.max())+1],'premixed':str(D/'premixed.png'),'premixedSha256':r.sha(D/'premixed.png'),'input':str(D/'input.png'),'inputSha256':r.sha(D/'input.png'),'copyMask':str(D/'copy-mask.png'),'copyMaskSha256':r.sha(D/'copy-mask.png'),'alpha':str(D/'alpha.png'),'alphaSha256':r.sha(D/'alpha.png'),'sourceCrops':src,'generations':[{'file':str(r.R/n/'generation.json'),'sha256':r.sha(r.R/n/'generation.json')}for n in ['stair-upper-v01','stair-lower-v01']],'actualModel':None,'actualQuality':None,'sourceResampling':False,'generatedNativePixels':[1254,1254],'maxFeatherRadiusPixels':2,'maskWindowInPatch':[l,t,rr,bb],'nativeOverlapSeam':{'worldBand':[39320+band,39320+band+115],'path':seam.tolist()},'outerQuiltingPaths':paths,'copyRule':'Copy premixed once where copy-mask is nonzero; validate input under mask before merge; do not reblend.','formalAccepted':False,'mechanicalQA':stats,'atUtc':r.now()}
r.write(D/'proposal.json',rec)
rec['protectedOriginalBevelWorldBands']=protected
r.write(D/'proposal.json',rec)
# Native QA crops (never resampled).
for nm,c in [('top',[360,175,960,520]),('middle',[360,650,960,1050]),('bottom',[360,1250,960,1640])]:
 Image.fromarray(old).crop(c).save(D/(nm+'-before.png'))
 Image.fromarray(out).crop(c).save(D/(nm+'-after.png'))
r.write(D/'mechanical-qa.json',stats)
print(json.dumps({k:v for k,v in rec.items()if k not in ['outerQuiltingPaths','nativeOverlapSeam','sourceCrops']},ensure_ascii=False))
