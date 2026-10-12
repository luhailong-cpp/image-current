from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']=='r10_c11')
refs=read(ROOT/'references.json')
with Image.open(refs[0]['file']) as im:
 for p in tile['patches']:
  f=ROOT/'guides'/f"{p['id']}.layout-only.png";assert not f.exists()
  im.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(f)
  write(Path(str(f)+'.generation.json'),{'file':f.as_posix(),'sha256':sha(f),'generatedAt':now(),'width':1254,'height':1254,'operation':'mechanical fractional-coordinate crop/enlargement for layout guide only; never final artwork','derivedFrom':[refs[0]],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
p=read(ROOT/'progress-r09_c11.json')
for k in ['candidateFile','candidateSha256','qualityReview']:p.pop(k,None)
p.update({'currentTile':'r10_c11','currentPatch':None,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'status':'guides_ready','nextStep':'Generate16 native cores using latest r09_c11 bottom and r10_c12 left anchors','updatedAt':now()})
assert not (ROOT/'progress-r10_c11.json').exists();write(ROOT/'progress-r10_c11.json',p)
print('16 tile-only guides and progress saved')

