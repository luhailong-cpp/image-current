from PIL import Image
from pathlib import Path
from workflow import ROOT,read,write,sha,now
tile='r10_c11'; name=tile+'_wall-junction_v01'
candidate=ROOT/'tiles'/f'{tile}.candidate.png'
box=[1421,2220,2675,3474]
target=ROOT/'guides'/f'{name}.target.png'
assert not target.exists()
Image.open(candidate).crop(box).save(target)
write(Path(str(target)+'.generation.json'),{'file':target.as_posix(),'sha256':sha(target),'operation':'unscaled exact crop of current candidate for complete four-patch wall junction repair','source':candidate.as_posix(),'sourceSha256':sha(candidate),'sourceCrop':box,'usableAsFinalArt':False})
detail=ROOT/'qa/r10_c11-junction-32.png'
refs=[{'file':target.as_posix(),'sha256':sha(target),'role':'exact native edit target; crop includes full defective stone slab junction and all incoming boundaries'},{'file':detail.as_posix(),'sha256':sha(detail),'role':'unedited native close crop locating the hard joint terminations; geometry defect to correct, not a new object'}]+read(ROOT/'references.json')
prompt='''Use case: precise-object-edit. Edit image1 at its original native1254 square size. Image2 is an unmodified detail crop showing the defect, not another scene. Last three images give full island layout, stone materials, and approved Q Daoist painting style. Correct the COMPLETE stone-slab junction in image1. This is one continuous tall vertical pale stone wall below one diagonal coping, grass and pavement only at its true foot. Several thin vertical stone joints abruptly terminate or shift sideways along an artificial horizontal image-cut line near y852 in image1. Make these existing joints continuous and physically coherent through that line. Preserve the wall silhouette, diagonal coping, stone panel count and perspective. Do NOT add a horizontal stone seam, new slab, ledge, step, carving, pillar, plant, sphere or any other object. Where a false duplicated vertical joint cannot continue into the existing lower joint, remove that false seam and fill it with the same uninterrupted stone surface. Retain the genuine lower joints at their exact x positions and carry them upward into coherent existing upper slab boundaries. The result should look like the same broad plain wall viewed from the same fixed camera. Keep the outer230 pixels on ALL four sides unchanged; repair only the central native detail, with seamless continuous stone shading and no rectangular cut line. Preserve all paving, wood and grass exactly. No zoom, shift, resize, blur, glow, text, interface or watermark. One opaque native1254 square image.'''
pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'candidateSource':candidate.as_posix(),'candidateSourceSha256':sha(candidate),'sourceBox':box,'intendedReplacementCore':[115,115,1139,1139],'intendedDestination':[1536,2335]})
print(__import__('json').dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
