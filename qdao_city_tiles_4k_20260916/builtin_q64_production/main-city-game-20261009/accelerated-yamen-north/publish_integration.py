"""Publish exact native context integration retaining previously reviewed seam paths."""
import sys,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
import pipeline as p
mfile=Path(sys.argv[1]);m=p.read(mfile);tile=m['tile'];src=Path(m['integratedComposite']['file'])
im=Image.open(src).convert('RGB');base=Image.open(m['baseCandidate']['file']).convert('RGB');assert im.size==base.size==(4096,4096)
name=f'{tile}-pipeline-fixed-native-contexts-{p.sha(src)[:12]}'
dest=p.ROOT/tile/'candidate'/(name+'.png');p.put_bytes(dest,src.read_bytes())
candidate={'file':str(dest),'sha256':p.sha(dest),'pixels':[4096,4096],'mode':'RGB'}
qa_dir=p.ROOT/tile/'qa'/name;qa=[]
def crop(label,box,rotate=False):
    a=im.crop(box);b=base.crop(box);changed=a.tobytes()!=b.tobytes()
    if rotate:a=a.transpose(Image.Transpose.ROTATE_90)
    rec=p.save_png(qa_dir/(label+'.png'),a)
    rec.update({'cropLTRB':box,'rotationCCW90':rotate,'nativePixelScale':1,'sourceResampled':False,'changedFromPreviouslyReviewedBase':changed,'actuallyViewed':False,'visualVerdict':'pending' if changed else 'pixel-identical to previously reviewed base; see base review'})
    qa.append(rec)
for axis in ('x','y'):
 for pos in (1024,2048,3072):
  for seg in range(4):
   s=seg*1024;box=[pos-160,s,pos+160,s+1024] if axis=='x' else [s,pos-160,s+1024,pos+160]
   crop(f'internal-{axis}{pos}-segment{seg+1:02d}',box,axis=='x')
for y in (1024,2048,3072):
 for x in (1024,2048,3072):crop(f'junction-x{x}-y{y}',[x-160,y-160,x+160,y+160])
sources=[{**p.native_info(p.selected(p.ROOT/tile,s)),**p.coords(tile,s)} for s in p.patch_ids()]
arr=np.array(im);prev=np.array(base);mask=np.array(Image.open(m['combinedSupport']['file']).convert('L'))>0
manifest={'schemaVersion':1,'createdAt':p.now(),'tile':tile,'candidate':candidate,'method':'fixed reviewed baseline seams plus recorded same-coordinate native context repair','nativeSources':sources,'nativeContextIntegration':{'file':str(mfile),'sha256':p.sha(mfile)},'baseCandidate':m['baseCandidate'],'qaFiles':qa,'internalSeamSegments':24,'junctions':9,'operation':'Keep all reviewed baseline pixels outside exact repair support. Copy already blended generated native context pixels at same coordinates within support. No resize, warp, spatial blur, or seam-path recomputation. Source alpha blends are disclosed in context derivation records.','native4096Claim':False,'finalArtUpscaled':False,'verifiedOutsideSupportUnchanged':bool(np.array_equal(arr[~mask],prev[~mask])),'outer160PixelStripsUnchanged':bool(np.array_equal(arr[:160],prev[:160]) and np.array_equal(arr[-160:],prev[-160:]) and np.array_equal(arr[:,:160],prev[:,:160]) and np.array_equal(arr[:,-160:],prev[:,-160:])),'formalAccepted':False}
p.put_json(dest.with_suffix('.assembly.json'),manifest)
p.update_progress()
print(p.json_bytes({'candidate':candidate,'manifest':str(dest.with_suffix('.assembly.json')),'qaDirectory':str(qa_dir),'qaFiles':33,'changedQA':[Path(q['file']).name for q in qa if q['changedFromPreviouslyReviewedBase']],'formalAccepted':False}).decode())
