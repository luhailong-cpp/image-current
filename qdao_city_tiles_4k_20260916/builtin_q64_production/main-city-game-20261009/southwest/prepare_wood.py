
from production import *
R=T/'refinement';n='p01_04'
orig=T/'native'/f'{n}.png';left=T/'native'/'p01_03.png';south=T/'native'/'p02_04.png'
seed=Image.open(orig).convert('RGB')
seed.paste(Image.open(south).crop((0,0,N,2*H)),(0,C))
seed.paste(Image.open(left).crop((C,0,N,N)),(0,0))
seedpath=R/'guides'/f'{n}.native-edit-seed.png';seed.save(seedpath)
refs=[{'file':str(seedpath),'sha256':sha(seedpath),'role':'edit target: native wooden deck crop with exact left and south continuity strips'},
{'file':CONTRACT['layoutReference'],'sha256':sha(CONTRACT['layoutReference']),'role':'whole city geometry reference only, do not output'},
{'file':CONTRACT['detailStyleReference'],'sha256':sha(CONTRACT['detailStyleReference']),'role':'approved material polish and daylight'},
{'file':CONTRACT['primaryStyleReference'],'sha256':sha(CONTRACT['primaryStyleReference']),'role':'approved Daoist chibi painting style'}]
neighbors=[{'file':str(left),'sha256':sha(left),'role':'left neighbor, right230px copied unchanged into left edge'},
{'file':str(south),'sha256':sha(south),'role':'south neighbor, top230px copied unchanged into bottom edge before left overlap; bottom-left corner follows left'}]
prompt='''Use case: precise-object-edit. EDIT ONLY IMAGE1, a 1254x1254 extremely close crop of an arena WOODEN DECK. Keep this exact crop, horizontal plank seams, two ivory curved painted lines, and the grey painted motif clipped by the top edge. The output must contain only the SAME WOOD FLOOR fragment. Never output the whole city in image2 or a new scene.

SINGLE REQUIRED FIX: remove the subtle tonal mismatch between the leftmost 230-pixel continuity strip and the immediately adjoining warm honey-orange wood. It has a faint vertical darker/lighter transition. Make the color and daylight of the plank surface continue smoothly from the LEFT native strip into the rest of that same plank. Preserve the fine wood grain and crisp edges, without blur or smoothing detail. Do not globally brighten, darken, recolor or redesign the crop. Match the original bright honey-orange palette. The ivory arcs and grey paint remain identical.

GEOMETRY AND CONTINUITY LOCK: leftmost 230 pixels and bottommost 230 pixels in image1 contain authentic neighboring artwork. Preserve these as fixed reference for tone and exact location of every board seam, grain and ivory arc. Repair only the slight interior color discontinuity. No change of camera, crop, scale, plank count, curve thickness, motif silhouette or lighting direction. No new objects, cracks, text, labels, borders or watermark. Images2/3/4 are context/style only. Output a single opaque native 1254x1254 patch.'''
promptpath=R/'prompts'/f'{n}.prompt.txt';promptpath.write_text(prompt,encoding='utf-8')
req={'prompt':prompt,'referenced_image_paths':[i['file'] for i in refs],'transparent_background':False,'references':refs,'neighborSources':neighbors,'coordinates':info(1,4),'editSource':{'file':str(orig),'sha256':sha(orig),'generationRecord':str(orig)+'.generation.json'},'submittedParameters':{'model':None,'quality':None},'editIntent':'Local wooden deck tone continuity repair with exact geometry locked'}
write(R/'prompts'/f'{n}.request.json',req)
write(str(seedpath)+'.derivation.json',{'operation':'native overlap composition, no resampling','file':str(seedpath),'sha256':sha(seedpath),'derivedFrom':[req['editSource']]+neighbors})
print(json.dumps({'seed':str(seedpath)}))

