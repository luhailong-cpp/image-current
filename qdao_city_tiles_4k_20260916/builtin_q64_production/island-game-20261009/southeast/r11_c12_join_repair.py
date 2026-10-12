"""r11_c12 two source-native join repair requests and truthful ingest only."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys,os
from datetime import datetime,timezone
R=Path(__file__).parent;mode,kind=sys.argv[1:3];ver=os.environ.get('R11_REPAIR_VERSION','v01');NAME=f'r11_c12_{kind}join_{ver}'
assert kind in ['rail','deck']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat();prog=R/'progress-r11_c12-repair.json'
if not prog.exists():write(prog,{'tile':'r11_c12','status':'repair_prepared','generatedRepairNativeCount':0,'formalAcceptedCount':0,'configSnapshot':read(R/'progress-r10_c13.json')['configSnapshot'],'currentRepair':NAME})
box=[397,2275,1651,3529] if kind=='rail' else [397,2957,1651,4211]
target=R/'guides'/f'{NAME}.target.png';detail=R/'guides'/f'{NAME}.detail.png';candidate=Path(os.environ.get('R11_REPAIR_BASE',str(R/'tiles/r11_c12.candidate-v01.png')))
if mode=='prepare':
 assert not target.exists();a=Image.open(candidate);out=Image.new('RGB',(1254,1254));bottom=min(box[3],4096);out.paste(a.crop((box[0],box[1],box[2],bottom)),(0,0));sources=[{'file':str(candidate),'sha256':sha(candidate),'sourceCrop':[box[0],box[1],box[2],bottom],'destination':[0,0]}]
 if kind=='deck':
  for name,crop,dest in [('r11_c12_p41_v02.png',[512,1139,1139,1254],[0,1139]),('r11_c12_p42_v01.png',[115,1139,742,1254],[627,1139])]:
   f=R/'native'/name;out.paste(Image.open(f).crop(crop),dest);sources.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest})
 out.save(target)
 db=[503,475,753,695] if kind=='rail' else [503,713,753,933]
 out.crop(db).save(detail)
 refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET: exact original-pixel continuous native composition; sole coordinate authority.'},{'file':str(detail),'sha256':sha(detail),'role':'Locator only, exact source crop '+str(db)+' from target, no enlargement; do not output this smaller crop.'}]+read(R/'references.json')
 common="""Use case: precise-object-edit. Correct the FIRST attached native 1254 x 1254 game-art crop, at exactly the same 1254 x 1254 output size and original framing. Image 2 is a native-size locator detail of the defect, not the output target. Last three attachments are approved layout/material/style references only. All content outside the first image is not to be copied into the scene.
Keep all existing forms, their original positions, scale, perspective, daylight and painting style. No added objects. The outer 115-pixel border of the full target is immutable context. Make the fixed object meet every outer entry boundary exactly. No rescaling, stretching, blur, blending, sharpening or replacement scene.
"""
 if kind=='rail':
  specific="""Repair the LOWER wooden horizontal railing beam that slopes upward to the right over turquoise water. Its lower silhouette has an accidental 11-pixel step at target x=627,y=615 (locator x=124,y=140). The beam body grain and highlight also break there. The step is a source seam, NOT a carpentry joint, notch or board end. Redraw the full cross-section of this same lower beam around the join as one straight continuous piece of consistent thickness, with ONE uninterrupted sloping upper edge, lower edge, wood grain and highlight. Connect smoothly to the exact beam geometry on both sides at the perimeter; preserve the real vertical picket rooted in the top of the lower beam. Do not add a joint or cover strip to hide it.
Keep the upper railing beam, paving above, blue water waves and any deck below exactly unchanged. The existing vertical picket must not grow, move or disappear. Output a natural complete continuous lower rail, not two offset rail segments. The locator shows the false step clearly; it must be absent after repair."""
 else:
  specific="""Repair the long dock DECK PLANK JOINT whose diagonal dark groove jumps upward 17 pixels at target x=627,y=839 (locator x=124,y=126). There is an obvious artificial vertical source boundary cutting the wood grain and the groove in the locator. This is NOT a board end, joinery joint, notch or stair. Reconstruct this whole existing plank and its neighboring groove so the two parallel plank edges, bevel highlight, dark joint and wood grain run as ONE straight continuous diagonal through x=627. Preserve the existing plank widths, slopes and all deck board locations. Match the anchored line endpoints on both sides; do not add a seam strip or a new board.
Keep every other board joint and the top deck rim exactly fixed. Preserve turquoise water and existing post portions, daylight, warm honey wood and painterly grain. Do not create a new kink somewhere else or move this offset to another boundary. The entire containing plank is visible in this full target; restore its single uninterrupted geometry."""
 if kind=='rail' and ver=='v02':
  specific='''Repair the full wooden dock railing assembly crossing the false vertical image join at target x=627. Both the UPPER and LOWER parallel diagonal beams have accidental steps at that x coordinate; the lower one drops 11 pixels at y~615, the upper one also kinks near y~100 and y~250. The turquoise water has an artificial straight tone boundary along the same x. These are source seams, NOT carpentry joints or notches. Restore BOTH beams as continuous single straight pieces, preserving their anchored endpoints at left and right, their consistent thickness, highlight, wood grain and their parallel perspective. Keep all three real vertical pickets exactly at their existing positions and sizes; keep their joints physically attached to both continuous beams. The middle picket near x627 must not be duplicated or deleted.
The lower deck rim near y1060 also has a small cut at x627; continue it as a single straight edge with unchanged endpoints. Restore continuous water texture and color across the false vertical source boundary. No new joints, cover strips, boards, objects or ornaments. Preserve all original paving above, posts, gold finial, deck and all outside 115-pixel borders. This is a whole-object join repair with both horizontal rails, all three pickets, water backdrop and lower deck entry geometry present, not a narrow seam band. The close locator focuses the most obvious lower-rail error; the full target shows all parallel elements. Output 1254 x 1254 at unchanged native scale.'''
 if kind=='deck':
  specific+=''' All parallel deck grooves and the long outer rim crossing the same x627 source cut must be made continuous, not just the one in the locator. Repair the complete deck board assembly visible in the target with each plank maintaining one continuous width, slope, dark groove and wood grain. Remove the artificial vertical wood tone boundary through the whole deck. Maintain all existing real board endpoints and the existing number of boards. The upper water already includes accepted native railing repair context and must retain its wave shapes and tone. At the lower center edge the source-cut kink may be corrected through the halo too, while the genuine left/right endpoint geometry stays fixed.'''
 prompt=common+specific;pp=R/'prompts'/f'{NAME}.prompt.txt';pp.write_text(prompt,encoding='utf-8');write(R/'prompts'/f'{NAME}.request.json',{'promptPath':str(pp),'promptSha256':sha(pp),'references':refs,'targetTileBox':box,'sourceComposition':sources,'actualModel':None,'actualQuality':None,'transparent_background':False,'targetPixels':[1254,1254]})
 print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
elif mode=='ingest':
 src=Path(sys.argv[3]);req=read(R/'prompts'/f'{NAME}.request.json');receipt=read(R/'receipts'/f'{NAME}.json');size=list(Image.open(src).size)
 assert size==[1254,1254];assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==Path(req['promptPath']).read_text(encoding='utf-8');assert receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]
 dest=R/'native'/f'{NAME}.png';assert not dest.exists();shutil.copy2(src,dest)
 write(Path(str(dest)+'.generation.json'),{'file':str(dest),'sha256':sha(dest),'width':size[0],'height':size[1],'generatedAt':stamp,'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'configSnapshot':read(prog)['configSnapshot'],'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'targetTileBox':box,'evidence':{'toolReceipt':f'receipts/{NAME}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'status':'pending_visual_boundary_review'})
 d=read(prog);d.update(status='repair_native_received',generatedRepairNativeCount=len(list((R/'native').glob('r11_c12_*join_*.png'))),currentRepair=NAME,updatedAt=stamp);tmp=prog.with_suffix('.pending.json');write(tmp,d);os.replace(tmp,prog)
 print(json.dumps({'file':str(dest),'sha256':sha(dest),'pixels':size}))

