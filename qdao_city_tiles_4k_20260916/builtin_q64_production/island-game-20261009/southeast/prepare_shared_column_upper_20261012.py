from workflow import *
from PIL import Image
name='r12_c11_c12_shared_column_upper_v01'
a=ROOT/'native/r12_c11_p44_v01.png';b=ROOT/'native/r12_c12_p41_v01.png'
ca=ROOT/'tiles/r12_c11.candidate-sol-20261012-v02.png';cb=ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png'
im=Image.new('RGB',(1254,1254))
parts=[]
def paste(f,box,dest):
 im.paste(Image.open(f).convert('RGB').crop(box),dest)
 parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':list(box),'destination':list(dest)})
paste(a,(512,0,1254,1254),(0,0))
paste(b,(0,0,742,1254),(512,0))
paste(ca,(3469,2957,4096,4096),(0,0))
paste(cb,(0,2957,627,4096),(627,0))
g=ROOT/'guides'/f'{name}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'tile':'r12_c11','tileRelativeOrigin':[3469,2957],'operation':'Registered unchanged source crop/paste, actual final candidate pixels take precedence; edit guide only','sources':parts,'usableAsFinalArt':False})
refs=[{'file':str(g),'sha256':sha(g),'role':'exact registered cross-column full-object edit target'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit the first image only into the same exact opaque 1254-square daylight painted game pier crop. Last three references guide layout, materials and painting style.
One existing shared FOREGROUND GOLD-CAPPED WOOD COLUMN near x490 crosses the middle of this image. Its gold ball and collar are in the upper-middle, near y350..550. Preserve this exact gold cap, collar, column width and placement, deck floorboards, diagonal rail and all surrounding supports.
Repair ONLY the COMPLETE lower shaft of this foreground gold-capped column: currently its shaft prematurely ends in an ornamental wet base near y980. The real long shaft must continue straight downward OUT THROUGH THE BOTTOM EDGE of this crop. Remove its premature ornamental water foot and its false local water contact, then extend this same warm vertical wood shaft, unchanged width and lighting, all the way out the bottom. Do not put any base, foot, waterline or another cap on this column anywhere inside this crop. Its actual base is in the next southern crop.
Retain every other existing support and water contact exactly. A separate independent tall column partly clipped at far left has its correct wet foot here; preserve that foot. Also retain the shorter genuine supports beneath the deck and rail on the right.
Preserve all outer 115 pixel strips exactly, except ONLY where the required shared column shaft crosses the bottom. Do not move the column, its cap, the camera, wood joints, rail, deck edge or shadows. Keep blue painted sea in every existing open gap. No additional props, no duplicate gold cap, no new lines, text or UI. Final pixels must come from this new complete native image."""
pf=ROOT/'prompts'/f'{name}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'tile':'r12_c11','tileRelativeOrigin':[3469,2957],'sharedWithTile':'r12_c12','secondTileRelativeOrigin':[-627,2957]})
write(ROOT/'prompts'/f'{name}.args.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False})
print(json.dumps({'guide':str(g),'name':name}))

