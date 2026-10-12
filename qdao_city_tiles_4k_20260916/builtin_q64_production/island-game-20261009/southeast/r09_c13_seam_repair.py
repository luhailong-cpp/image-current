"""r09_c13 only: exact native seam crop and receipt-backed repair ingest."""
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,progress
import sys,json,shutil
mode,key=sys.argv[1:3]
line={'seam2':2048,'seam3':3072}[key]
version = sys.argv[4] if mode=='ingest' and len(sys.argv)>4 else 'v01'
name=f'r09_c13_{key}_{version}'
target=ROOT/'guides'/f'{name}.native-target.png'
candidate=ROOT/'tiles/r09_c13.candidate.png'
if mode=='prepare':
 box=[909,line-627,2163,line+627];Image.open(candidate).crop(box).save(target)
 write(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'operation':'exact 1254 native crop spanning horizontal seam y627; no resize or painting','derivedFrom':[{'file':str(candidate),'sha256':sha(candidate),'sourceCrop':box}]})
 desc=('The gold top face of the diagonal timber beam ends abruptly at the horizontal seam, and the upright post side edges have a visible step. Continue the gold top face smoothly to its post junction, and connect the post edges and wood grain across the seam without a horizontal notch. ' if key=='seam2' else 'The thick vertical timber post side edges and lit bevel have a small lateral step at horizontal seam y627. Connect the same post edges, wood grain and bevel continuously across the seam, without an abrupt notch or color line. Do not change the golden chime to the left. ')
 prompt='Use case: precise-object-edit. Edit attached image1 only, preserving exact native 1254x1254 square framing. It is an actual hard-stitched game-art crop, not a blurry guide. Repair the visible horizontal stitching defect at y627. '+desc+'Repair only inside central rectangle x115-1139, y371-883. Keep the outer anchors, especially y0-370 and y884-1253 plus left/right115 columns, pixel-identical. Both outside post sections are fixed anchors: reconcile the small mismatch smoothly within the central band, keeping a plausible upright timber silhouette and no sudden width change. Preserve all existing leaves, small flowers, golden chimes, cap, shadows and stone, except the minimal pixels required for this seam repair. No new objects or decoration. No blur, feathering, ghosting, rescaling, camera move or geometric image warp. Last three images are sole full layout, independent material detail and approved Q Daoist style references only. Crisp rounded bright daylight painting. Output one opaque square.'
 pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
 refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET: actual native hard seam crop; preserve outer anchors'}]+read(ROOT/'references.json')
 write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
 print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
elif mode=='ingest':
 src=Path(sys.argv[3]);out=ROOT/'native'/f'{name}.png';assert not out.exists();shutil.copy2(src,out)
 im=Image.open(out);assert im.size==(1254,1254)
 req=read(ROOT/'prompts'/f'{name}.request.json')
 rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress-r09_c13.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin; tool discloses no model or quality.','prompt':req['promptPath'],'promptSha256':sha(Path(req['promptPath'])),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'status':'native_seam_repair_pending_review','coordinate':{'tile':'r09_c13','nativeBoxRelativeToTile':[909,line-627,2163,line+627],'intendedSourceCrop':[115,371,1139,883],'intendedDestinationBox':[1024,line-256,2048,line+256]}}
 write(Path(str(out)+'.generation.json'),rec)
 preview=Image.open(target).convert('RGB');preview.paste(im.crop((115,371,1139,883)),(115,371))
 p=ROOT/'qa'/f'{name}.hard-insert.png';preview.save(p)
 write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'exact native crop/paste for hard insertion QA','derivedFrom':[{'file':str(target),'sha256':sha(target),'role':'unchanged anchors'},{'file':str(out),'sha256':sha(out),'sourceCrop':[115,371,1139,883],'destination':[115,371]}]})
 d=read(ROOT/'progress-r09_c13.json');progress(status='native_seam_repair_received',currentPatch=name,generatedNativeCount=d['generatedNativeCount']+1)
 print(json.dumps({'file':str(out),'sha256':sha(out),'nativePixels':[1254,1254]}))

