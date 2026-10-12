"""Single native repair of whole paver at r10_c13 first-row junction; mechanical exact pixels only."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,sys,shutil,numpy as np,os
from datetime import datetime,timezone
R=Path(__file__).parent;NAME=os.environ.get('R10_C13_REPAIR_NAME','r10_c13_paver_v01')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
target=R/'guides'/f'{NAME}.target.png'
mode=sys.argv[1]
if mode=='prepare':
 assert not target.exists()
 top=R/'tiles/r09_c13.candidate.png';bottom=R/'tiles/r10_c13.candidate.png'
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(top).crop((397,3981,1651,4096)),(0,0));im.paste(Image.open(bottom).crop((397,0,1651,1139)),(0,115));im.save(target)
 refs=[{'file':str(target),'sha256':sha(target),'role':'Exact original-pixel edit target across two assembled native candidates'}]+read(R/'references.json')
 prompt="""Use case: precise-object-edit. Edit the FIRST attached image, a 1254 x 1254 exact native crop of continuous daylight hand-painted game paving. Output exactly 1254 x 1254 with absolutely unchanged scale, camera, framing and object locations.
The first image is the only coordinate authority for this edit. The last three references are layout overview, materials close-up, and approved mail Daoist painting style. They must not replace or recompose the edit target.
Repair ONE malformed small isolated V/step-like light paving corner at approximately local x=610..655,y=220..280, near the middle-upper part of this image. It lies inside a much larger existing blue-gray slab, where unrelated source joints made a short disconnected duplicate corner. Remove this tiny isolated corner and reconstruct the same single continuous surrounding slab with the matching blue-gray tone, understated mottled paint and dappled tree shadow. Preserve the actual full slab perimeter and its existing diagonal joints around it, including their tangent, width and exact endpoints. The repair must not turn the defect into a new paver, stone chip, extra crack, ornament or loose object.
Keep all other native artwork and every object exactly fixed. In particular preserve the wooden lower crossbeam along the top-right, all complete paving joints, grass tufts and shadows. The outside 115-pixel perimeter is immutable same-coordinate native context; match it exactly. This is a local geometry cleanup within one entire paver, not a new scene or a restyle. Do not blur, enlarge, sharpen, stretch or invent material grain. No new objects, no text, no UI, no people. Opaque native square output."""
 if NAME.endswith('v02'):
  detail=R/'guides'/'r10_c13_paver_v02.detail.png';refs.insert(1,{'file':str(detail),'sha256':sha(detail),'role':'Locator only: exact source crop [450,120,830,360] from target; do not output this crop.'})
  prompt='''Edit attached image 1 at exactly its 1254 x 1254 native resolution and framing. Image 2 is a close locator crop from image 1, solely to identify the defect; output the entire image 1. Last three images are style/material/layout references only.
CRITICAL REQUIRED CHANGE: Image 2 clearly shows a vertical rectangular source-patch tone edge through a blue-gray paving slab, ending at a small pointed white V-shaped corner near the locator center. This vertical edge and little white V/step are both ERRORS. ERASE this false corner AND the whole rectangular tone seam. They are not legitimate paving joints. Paint uninterrupted continuous flat BLUE-GRAY STONE across the former corner. Do not keep, trace, copy or sharpen the V-shape. There must be NO corner, raised white lip, loose stone, line intersection or extra crack there after repair.
In the full target image the malformed area occupies approximately x=590..700, y=125..290. Reconstruct the entire containing slab surface inside its REAL diagonal outer perimeter, preserving the outer perimeter and surrounding neighboring slabs. Real wide dark diagonal slab borders and existing grass are legitimate and must stay fixed. The slab surface should have the same subtle mottled blue-gray painted stone and soft dappled light continuously across x=627; eliminate the vertical patch edge and the bright isolated corner where it ends. Treat shadows as continuous light, not a separate rectangular patch.
Everything outside this one containing slab is immutable. Keep the large wooden beam and its edges absolutely identical; keep the lower paving joints, plants, other shadows and all outer 115-pixel edges identical. Do not invent new slabs, objects, ornaments or text. This is one local repair to an entire existing paver, no scale change, no reframe, no zoom, no resampling or restyle. Return one opaque 1254 x 1254 image matching target exactly except the corrected slab.'''
 pp=R/'prompts'/f'{NAME}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
 req={'promptPath':str(pp),'promptSha256':sha(pp),'references':refs,'actualModel':None,'actualQuality':None,'transparent_background':False,'targetTileBox':[397,-115,1651,1139],'coreDestinationBox':[512,0,1536,1024],'derivedFrom':[{'file':str(top),'sha256':sha(top),'sourceCrop':[397,3981,1651,4096],'destination':[0,0]},{'file':str(bottom),'sha256':sha(bottom),'sourceCrop':[397,0,1651,1139],'destination':[0,115]}]}
 write(R/'prompts'/f'{NAME}.request.json',req)
 print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
elif mode=='ingest':
 src=Path(sys.argv[2]);req=read(R/'prompts'/f'{NAME}.request.json');receipt=read(R/'receipts'/f'{NAME}.json')
 assert Image.open(src).size==(1254,1254)
 assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==Path(req['promptPath']).read_text(encoding='utf-8')
 assert receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]
 dest=R/'native'/f'{NAME}.png';assert not dest.exists();shutil.copy2(src,dest)
 write(Path(str(dest)+'.generation.json'),{'file':str(dest),'sha256':sha(dest),'width':1254,'height':1254,'generatedAt':stamp,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'configSnapshot':read(R/'progress-r10_c13.json')['configSnapshot'],'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'targetTileBox':req['targetTileBox'],'evidence':{'toolReceipt':f'receipts/{NAME}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'status':'pending_visual_review_not_inserted'})
 print(json.dumps({'file':str(dest),'sha256':sha(dest)}))

