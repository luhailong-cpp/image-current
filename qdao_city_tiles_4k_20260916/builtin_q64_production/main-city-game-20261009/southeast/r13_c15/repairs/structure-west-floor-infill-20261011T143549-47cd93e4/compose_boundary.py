"""Use actual native west-floor repair through the formal bottom core edge.

Only top/right are interior boundaries. Bottom joins a future external neighbor;
preserving old pixels there would cut the new physical timber joint short.
"""
from pathlib import Path
import sys, importlib.util
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parents[1]))
import structure_repairs as s
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

m=s.read(D/'preparation.json');g=s.read(D/'generation.json')
for a in [m['sourceCandidate'],m['sourceContext'],m['immutableWest'],g['native'],g['receipt'],g['preparation']]:s.checked(a)
source=Image.open(m['target']['path']).convert('RGB');guide=source.copy();hole=m['guideHole'];ImageDraw.Draw(guide).rectangle([hole[0],hole[1],hole[2]-1,hole[3]-1],fill=tuple(m['guideFillRGB']))
assert np.array_equal(np.array(guide),np.array(Image.open(m['guide']['path']).convert('RGB')))
algorithm=s.Z/'assemble_candidate.py';spec=importlib.util.spec_from_file_location('boundary_algo',algorithm);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
crop=[625,640,1254,1254];placement=[0,3482,629,4096]
result=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));old=result[3482:4096,0:629].copy();new=np.array(Image.open(g['native']['path']).convert('RGB').crop(crop));h,w=old.shape[:2];band=32
top=mod.minimum_vertical_seam(old[:band].transpose(1,0,2),new[:band].transpose(1,0,2));right=mod.minimum_vertical_seam(old[:,-band:],new[:,-band:]);a=np.full((h,w),255,np.uint8);a[:band]=np.where(np.arange(band)[:,None]>=top[None,:],255,0);a[:,-band:]=np.minimum(a[:,-band:],np.where(np.arange(band)[None,:]<right[:,None],255,0).astype(np.uint8));a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1)));a[0]=0;a[:,-1]=0
result[3482:4096,0:629]=((old.astype(np.uint32)*(255-a[:,:,None])+new.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
s.png(D/'alpha.png',Image.fromarray(a))
with (D/'seam-paths.npz').open('xb') as f:np.savez_compressed(f,top=top,right=right)
s.png(D/'candidate-4096.png',Image.fromarray(result));ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=result;s.png(D/'context-4326.png',Image.fromarray(ctx))
out=dict(schemaVersion=1,version=m['version'],composedAt=s.now(),sourceCandidate=m['sourceCandidate'],sourceContext=m['sourceContext'],immutableWest=m['immutableWest'],native=g['native'],generation=s.art(D/'generation.json'),preparation=s.art(D/'preparation.json'),nativeSourceCrop=crop,pasteBoxIn4096=placement,plannedCropSuperseded=m['nativeSourceCrop'],cropAdjustmentReason='Generated physical butt joint continues to bottom edge. Preserve native continuation to formal y4096; top starts above foot-contact seam. Only top/right are interior seams.',alpha=s.art(D/'alpha.png'),seamPaths=s.art(D/'seam-paths.npz'),algorithm=s.art(algorithm),compositor=s.art(__file__),replayHelper=s.art(s.__file__),candidate=s.art(D/'candidate-4096.png'),context=s.art(D/'context-4326.png'),operation='Exact native crop; minimum-error top/right paths in32px bands; Gaussian radius1 alpha; uint32 rounded blending. No left/bottom blend to old pixels. No resampling, warp, or transform.',resized=False,formalAccepted=False,status='independent_candidate_pending_local_visual_QA',southExternalEdgeChangedX=[0,629],southExternalQA='pending',guideReplay=True)
s.write(D/'composition.json',out);s.replay(m['version']);review=source.copy();review.paste(Image.fromarray(result).crop(placement),tuple(crop[:2]));s.png(D/'review-composed-1254.png',review)
print(s.json.dumps({'composition':str(D/'composition.json'),'candidate':out['candidate'],'context':out['context']}))
