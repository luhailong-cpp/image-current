from native_work import *
import numpy as np
tid='r03_c13';p=ZONE/'tiles'/f'{tid}.png';d=read(p.with_suffix('.png.derivation.json'))
old=Image.open(ZONE/'qa/history/c5cd412d241b-r03_c13.png').convert('RGB');new=Image.open(p).convert('RGB')
a=np.array(old);b=np.array(new);diff=np.any(a!=b,axis=2);mask=np.zeros(diff.shape,dtype=bool);mask[3072:4096,2048:3072]=True
assert not np.any(diff&~mask)
rebuilt=Image.new('RGB',(4096,4096))
for s in d['sources']:
 assert sha(s['file'])==s['sha256'];rebuilt.paste(Image.open(s['file']).crop(s['coreCrop']),s['tileLocalPaste'])
for s in d['requiredOverlays']:
 assert sha(s['source'])==s['sha256'];rebuilt.paste(Image.open(s['source']).crop(s['coreCrop']),s['tileLocalPaste'])
assert np.array_equal(np.array(rebuilt),b)
review={'tileId':tid,'source':{'file':p.as_posix(),'sha256':sha(p),'size':list(new.size)},'status':'passed_internal_visual_and_native_provenance','reviewedAtUtc':now(),'reviewers':['root','southeast_tile (independent changed-join check)'],'scope':'Original full 16core/24seam/9cross review retained for pixel-identical area. Changed p04_03 full core and all affected seams/crosses re-inspected at 1:1. Whole preview inspected.','priorFullReview':(ZONE/'qa/history/c5cd412d241b-r03_c13-whole-review.json').as_posix(),'changedCore':'r03_c13_p04_03_v3','evidence':[str(ZONE/'qa/r03_c13-final'/n) for n in ['core-4-3-100pct.png','vertical-2-segment-4-100pct.png','vertical-3-segment-4-100pct.png','horizontal-3-segment-3-100pct.png','cross-3-2-100pct.png','cross-3-3-100pct.png']],'resolvedDefect':'Single continuous terrace front edge and wall face; former150-220px vertical discontinuity removed. Lanterns/post preserved.','pixelIdentityOutsideChangedCore':True,'rebuiltNativePixelDifference':0,'baseCoverageMin':1,'baseCoverageMax':1,'uncoveredPixels':0,'finalArtUpscaled':False,'formalAccepted':False,'externalSeams':'west/east previously passed boundaries remain pixel-identical; south generation in progress','actualModel':None,'actualQuality':None}
write(ZONE/'qa/r03_c13-revised-review-20261010.json',review)
d.update(internalReview='passed',status='internal_candidate_passed',formalAccepted=False,reviewRecord=(ZONE/'qa/r03_c13-revised-review-20261010.json').as_posix());write(p.with_suffix('.png.derivation.json'),d)
# Refresh adjacent preview from current exact tiles.
im=Image.new('RGB',(8192,4096));im.paste(Image.open(ZONE/'tiles/r03_c12.png'),(0,0));im.paste(new,(4096,0));im.save(ZONE/'qa/r03_c12-r03_c13-adjacent-context.png');im.resize((2048,1024)).save(ZONE/'qa/r03_c12-r03_c13-adjacent-preview.png')
print(json.dumps({'sha256':sha(p),'review':review['status'],'pixelDifferenceOutsideChangedCore':0,'rebuildDifference':0}))

