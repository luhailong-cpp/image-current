from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import hashlib,json,numpy as np
d=Path(__file__).parent;t=d.parents[1]
before=Image.open(d/'before-native.png').convert('RGB');after=Image.open(d/'repair-native.png').convert('RGB');assert before.size==after.size==(1254,1254)
# Use only generated pixels for the two exact local defects. No art is procedurally redrawn.
rope=Image.new('L',(1254,1254));ImageDraw.Draw(rope).polygon([(468,419),(511,420),(552,466),(663,468),(709,443),(763,440),(780,514),(746,545),(676,540),(558,546),(490,529),(468,493)],fill=255)
rope=rope.filter(ImageFilter.GaussianBlur(5))
sand=Image.new('L',(1254,1254));ImageDraw.Draw(sand).polygon([(470,137),(540,137),(586,147),(595,386),(526,413),(473,393)],fill=255)
sand=sand.filter(ImageFilter.GaussianBlur(6))
mask=Image.fromarray(np.maximum(np.asarray(rope),np.asarray(sand)).astype('uint8'))
mask.save(d/'native-alpha-mask.png')
comp=Image.composite(after,before,mask);comp.save(d/'after-local-composite-native.png')
old=t/'candidate/r05_c10-4096-candidate-v1.png';new=t/'candidate/r05_c10-4096-candidate-v2.png'
tile=Image.open(old).convert('RGB');tile.paste(comp,(1480,0));tile.save(new)
preview=tile.copy();preview.thumbnail((1024,1024));preview.save(t/'qa/candidate-v2-preview.png')
for name,box in [('rope',(425,365,835,620)),('sand',(440,110,660,420))]:
 a=before.crop(box);z=comp.crop(box);qa=Image.new('RGB',(a.width*2,a.height));qa.paste(a,(0,0));qa.paste(z,(a.width,0));qa.save(d/f'{name}-before-after-native.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((d/'repair.request.json').read_text());receipt=json.loads((d/'repair.receipt.json').read_text());deriv=json.loads((d/'before-native.derivation.json').read_text())
g={'file':str(d/'repair-native.png'),'sha256':sha(d/'repair-native.png'),'nativeDimensions':[1254,1254],'nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool exposes no verified actual model/quality metadata','prompt':req['prompt'],'reference':{'file':str(d/'before-native.png'),'sha256':sha(d/'before-native.png'),'role':req['referenceRoles'][0]},'receipt':receipt,'sourceDerivation':deriv,'mask':{'file':str(d/'native-alpha-mask.png'),'sha256':sha(d/'native-alpha-mask.png'),'bbox':list(mask.getbbox()),'operation':'straight-alpha selection of original-size generated repair pixels; source-over onto candidate, no pixel resampling','ropeFeatherSigma':5,'sandFeatherSigma':6},'targetTileBox':[1480,0,2734,1254],'status':'localized_repair_applied_to_candidate_v2'}
(d/'repair-native.generation.json').write_text(json.dumps(g,indent=2)+'\n')
m=json.loads(old.with_suffix('.manifest.json').read_text());m.update({'file':str(new),'sha256':sha(new),'baseCandidate':str(old),'baseCandidateSha256':sha(old),'repairRecord':str(d/'repair-native.generation.json'),'repairOperation':'local original-pixel alpha composite','formalAccepted':False,'seamReview':'v2 pending'})
new.with_suffix('.manifest.json').write_text(json.dumps(m,indent=2)+'\n')
oldarr=np.asarray(Image.open(old).convert('RGB'));newarr=np.asarray(tile);diff=np.any(oldarr!=newarr,axis=2)
ys,xs=np.where(diff)
assert not diff[:115,:].any() and not diff[:,4095].any()
report={'candidate':str(new),'candidateSha256':sha(new),'changedPixels':int(diff.sum()),'actualChangedTileBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'nativeDimensions':[1254,1254],'north115PixelsUnchanged':True,'eastEdgeUnchanged':True,'actualModel':None,'formalAccepted':False}
(d/'repair-application.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))


