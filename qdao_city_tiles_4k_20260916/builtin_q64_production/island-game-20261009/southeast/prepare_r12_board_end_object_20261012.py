from workflow import *
from PIL import Image
name='r12_c12_board_end_joint_v01'
upper=ROOT/'native/r12_c12_p24_v03.png';lower=ROOT/'native/r12_c12_p34_v02.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(lower).convert('RGB'),(0,256))
im.paste(Image.open(upper).convert('RGB').crop((0,768,1254,1254)),(0,0))
g=ROOT/'guides'/f'{name}.png';assert not g.exists();im.save(g)
parts=[{'file':str(lower),'sha256':sha(lower),'sourceCrop':[0,0,1254,998],'destination':[0,256]},{'file':str(upper),'sha256':sha(upper),'sourceCrop':[0,768,1254,1254],'destination':[0,0],'priority':'overlapping north geometry'}]
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'usableAsFinalArt':False,'tileRelativeOrigin':[2957,1677],'operation':'exact original native crop and paste for whole board object repair guide','sources':parts})
refs=[{'file':str(g),'sha256':sha(g),'role':'whole registered board edit target crossing actual two patch rows'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit image 1 into the same exact 1254-square native crop of a hand-painted daylight golden wood pier. Last three references are layout, material, painting style only. Preserve all outer 115 pixels and the clipped gold finial/column and diagonal rail at lower-left/bottom exactly.
Repair the COMPLETE physical floorboard assembly. There is one anomalous extra groove entering the left around y555 which fades away around x400,y450 inside a broad plank. The left side has two narrower planks meeting one wider plank on the right. Give these three planks a REAL COMPLETE PLANK END CONNECTION: around x400, add one restrained perpendicular end-seam joining the two existing long outer grooves around y294 and y596 at that x. The extra middle groove must meet that perpendicular end-seam cleanly at a T, so all plank boundaries belong to complete boards. This entire end-seam must extend from one outer long boundary to the other, with no floating short mark or fading endpoint inside a board. This solves the differing board widths physically; keep every other long groove uninterrupted and at its existing exact edge endpoints. Do not change board count at the frozen image edges or add other end-seams.
Keep the same warm wood color and painted grain. Use a thin understated brown wood join, no black scratch, metal bracket, embossing or extra prop. Preserve existing shadows, columns, blue water and camera scale. Opaque square, no text or UI."""
pf=ROOT/'prompts'/f'{name}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'tile':'r12_c12','tileRelativeOrigin':[2957,1677]})
print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
