from workflow import *
from PIL import Image
name='r13_c12_p14';version='v02'
current=ROOT/'native/r13_c12_p14_v01.png';west=ROOT/'native/r13_c12_p13_v01.png';north=ROOT/'native/r12_c12_p44_v02.png'
im=Image.open(current).convert('RGB')
im.paste(Image.open(west).convert('RGB').crop((1024,0,1254,1254)),(0,0))
im.paste(Image.open(north).convert('RGB').crop((0,1024,1254,1139)),(0,0))
g=ROOT/'guides'/f'{name}.native-context-{version}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'usableAsFinalArt':False,'operation':'Whole native repair edit target; exact actual west overlap prioritized, then only the actual northern core 115px. The north native outside-core halo is not used to overwrite legitimate west beam geometry.','sources':[{'file':str(x),'sha256':sha(x)} for x in [current,west,north]],'placements':[{'source':str(west),'sourceCrop':[1024,0,1254,1254],'destination':[0,0]},{'source':str(north),'sourceCrop':[0,1024,1254,1139],'destination':[0,0]}]})
refs=[{'file':str(g),'sha256':sha(g),'role':'registered full-object repair target; retain existing correct columns and sea'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit image 1 into exactly the same 1254-square native crop. Preserve the two existing columns, correct cap/collar shapes, central long shaft and circular wet foot, sea and their exact locations.
Only repair the COMPLETE diagonal connecting rail at the upper-left of this crop: there is a small stepped kink at the previous y230 reference-strip junction. Make this one actual warm timber rail continuous, straight in perspective, and of unchanged width, running down-right from the top-left to the EXISTING foreground gold cap at left near y435. No step, notch, duplicate rail, new edge or floating sliver. The sharp left230 already holds actual west neighbor geometry, and the top115 holds the actual north core edge. Match those true final-core boundaries smoothly. Do not interpret the top native outside-core halo as an authority to move the west rail. The entire target outside this rail is already correct; copy it faithfully. No new finial, shifted shaft, raised foot, new boards or scenery. Last three references are layout, material and painting style only. Opaque square, no text/UI."""
pf=ROOT/'prompts'/f'{name}_{version}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}_{version}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
write(ROOT/'prompts'/f'{name}_{version}.args.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False})
print(json.dumps({'guide':str(g)}))

