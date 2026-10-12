from PIL import Image
from pathlib import Path
from workflow import ROOT,read,write,sha
import json
name='r10_c11_pillar-body_v01'; candidate=ROOT/'tiles/r10_c11.candidate-v02.png'
box=[2280,2450,3534,3704]
target=ROOT/'guides'/f'{name}.target.png';detail=ROOT/'guides'/f'{name}.defect.png'
assert not target.exists()
im=Image.open(candidate);im.crop(box).save(target);im.crop([2560,2816,3072,3328]).save(detail)
for f,b in [(target,box),(detail,[2560,2816,3072,3328])]:
    write(Path(str(f)+'.generation.json'),{'file':f.as_posix(),'sha256':sha(f),'source':candidate.as_posix(),'sourceSha256':sha(candidate),'sourceCrop':b,'operation':'unscaled exact candidate crop for edit reference only','usableAsFinalArt':False})
refs=[{'file':target.as_posix(),'sha256':sha(target),'role':'EDIT target: full tall stone pillar body including top/bottom joints and incoming walls'},{'file':detail.as_posix(),'sha256':sha(detail),'role':'unedited defect locator: rectangular scale jump in stone texture across middle of pillar'}]+read(ROOT/'references.json')
prompt='''Use case: precise-object-edit. Edit image1 in its exact native1254 square framing. Image2 is an unmodified detail crop locating the defect. Last three images are full island layout, stone material and approved Q Daoist painted style. Correct ONLY the STONE TEXTURE on the central existing tall courtyard pillar body. Its middle currently has a rectangular horizontal band where the mottled stone pattern changes abruptly to much larger blotches. Replace that artificial image-cut band with one continuous natural soft pale stone material over the ENTIRE pillar front and side, so texture scale, lighting and stone color flow uniformly from top to base. Keep every architectural contour, pillar width, top slab, carved rounded arch outline, base ledges, existing diagonal wall, grass, flowers and paving unchanged. Do not remove the pillar decoration or invent new decoration, cracks, horizontal joints, extra slabs or objects. Keep stone subtle, broad smooth surfaces with low contrast, no noisy grain. Preserve outer230 on all sides, fixed camera, object sizes and daylight. This is material continuity repair across an existing image cut, not a new design. No blur, glow, resizing, zoom, text, interface or watermark. Single native1254 opaque square.'''
pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'sourceCandidate':candidate.as_posix(),'sourceCandidateSha256':sha(candidate),'sourceBox':box})
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
