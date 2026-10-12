"""Native repair request/receipt and exact candidate overlay; no pixel painting."""
from pathlib import Path
from PIL import Image
import sys,json,shutil
from workflow import ROOT,read,write,sha,now,progress
name='r10_c12_h12-repair_v01'
mode=sys.argv[1]
target=ROOT/'guides'/f'{name}.native-target.png'
if mode=='prepare':
 a=ROOT/'tiles/r09_c12.candidate-v02.png';b=ROOT/'tiles/r10_c12.candidate-v01.png'
 im=Image.new('RGB',(1254,1254))
 im.paste(Image.open(a).crop((1306,3981,2560,4096)),(0,0))
 im.paste(Image.open(b).crop((1306,0,2560,1139)),(0,115));im.save(target)
 write(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'operation':'exact crop/paste crossing shifted seam x627; no resize','sources':[{'file':str(a),'sha256':sha(a),'crop':[1306,3981,2560,4096],'destination':[0,0]},{'file':str(b),'sha256':sha(b),'crop':[1306,0,2560,1139],'destination':[0,115]}]})
 refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET: exact native seam crop'}]+read(ROOT/'references.json')
 prompt='Use case: precise-object-edit. Edit attached image 1 only at the faint straight vertical stitching discontinuity x627, mainly paving y300-720. Exact native square 1254x1254 crop. Make the pale gray paving continuous, connecting the short tan diagonal stone joints across x627 with one coherent joint and consistent daylight material texture. Keep the existing red spent firecracker tube, golden column base, shadows, paper scraps and all other objects unchanged. The repair is restricted to narrow band x371-883 and y115-1139; preserve all outer anchor strips exactly. In particular the top115 rows match the neighboring 4K tile and must remain unchanged, and left/right edges must stay continuous for exact hard insertion. No blur, gradient blending, geometric warp or camera shift. Match existing rounded polished Daoist Q painting, natural pale gray stone with restrained thin joints. Last three images are full layout, material and primary approved style only. No new objects, ornaments, characters, labels, interface or watermark. Return one opaque square.'
 pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
 req={'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
 write(ROOT/'prompts'/f'{name}.request.json',req)
 print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
elif mode=='ingest':
 src=Path(sys.argv[2]);out=ROOT/'native'/f'{name}.png';assert not out.exists();shutil.copy2(src,out)
 im=Image.open(out);assert im.size==(1254,1254)
 req=read(ROOT/'prompts'/f'{name}.request.json')
 rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no model/quality selectors or returned identifiers.','prompt':req['promptPath'],'promptSha256':sha(Path(req['promptPath'])),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'status':'seam_repair_candidate_pending_review','coordinate':{'tile':'r10_c12','nativeBoxRelativeToTile':[1306,-115,2560,1139],'intendedSourceCrop':[371,115,883,1139],'intendedDestinationBox':[1677,0,2189,1024]}}
 write(Path(str(out)+'.generation.json'),rec)
 preview=Image.open(target).convert('RGB');preview.paste(im.crop((371,115,883,1139)),(371,115))
 p=ROOT/'qa'/f'{name}.hard-insert.png';preview.save(p)
 write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'exact native crop and hard paste, no resize or blending','sources':[{'file':str(target),'sha256':sha(target),'role':'unchanged surrounding pixels'},{'file':str(out),'sha256':sha(out),'crop':[371,115,883,1139],'destination':[371,115]}]})
 progress(status='seam_repair_received',currentPatch=name,generatedNativeCount=len(list((ROOT/'native').glob('*.png'))))
 print(json.dumps({'file':str(out),'sha256':sha(out),'dimensions':list(im.size)}))
