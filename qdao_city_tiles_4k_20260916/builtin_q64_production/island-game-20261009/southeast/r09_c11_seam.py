from pathlib import Path
from PIL import Image
import json,sys,shutil
from workflow import ROOT,read,write,sha,now,progress
mode,name,*arg=sys.argv[1:]
if mode=='prepare':
 a,b,description=arg
 ap=ROOT/'native'/a;bp=ROOT/'native'/b
 left=Image.open(ap).convert('RGB');right=Image.open(bp).convert('RGB')
 pair=Image.new('RGB',(2278,1254));pair.paste(left.crop((0,0,1139,1254)),(0,0));pair.paste(right.crop((115,0,1254,1254)),(1139,0))
 target=ROOT/'guides'/f'{name}.native-seam-target.png';pair.crop((512,0,1766,1254)).save(target)
 sources=[{'file':p.as_posix(),'sha256':sha(p),'generationRecord':str(p)+'.generation.json'} for p in [ap,bp]]
 write(Path(str(target)+'.generation.json'),{'file':target.as_posix(),'sha256':sha(target),'operation':'unscaled hard-cut pair then native1254 crop crossing center seam at x627; no painting or resampling','derivedFrom':sources,'pairCrop':[512,0,1766,1254]})
 refs=[{'file':target.as_posix(),'sha256':sha(target),'role':'EDIT TARGET, native1254 seam crop, center vertical join x627'}]+read(ROOT/'references.json')
 prompt='Use case: precise-object-edit. Edit image 1, a native1254 square crop crossing a visible vertical stitching error at x627. Preserve the image exact size, framing and all outer borders. Repair ONLY the narrow central vertical band x371-883 so contours and colors flow naturally across x627. Keep every pixel outside x371-883 unchanged, especially left/right/top/bottom anchors. Do not blur or feather a seam; redraw the actual object geometry correctly at native detail. '+description+' The last three images are full-map layout, material reference and approved Q Daoist painting style only. Preserve daylight, original objects, rounded painted finish. No new objects, text, people, UI or watermark. Return one opaque square.'
 pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
 request={'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
 write(ROOT/'prompts'/f'{name}.request.json',request)
 print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False},ensure_ascii=True))
elif mode=='ingest':
 source=Path(arg[0]);out=ROOT/'native'/f'{name}.png';shutil.copy2(source,out);im=Image.open(out);assert im.size==(1254,1254)
 req=read(ROOT/'prompts'/f'{name}.request.json')
 info={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':source.as_posix(),'sourceOutputSha256':sha(source),'configSnapshot':read(ROOT/'progress-r09_c11.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin tool exposes no model or quality selectors and returns neither.','prompt':req['promptPath'],'promptSha256':sha(Path(req['promptPath'])),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'status':'seam_repair_candidate_pending_review'}
 write(Path(str(out)+'.generation.json'),info)
 p=read(ROOT/'progress-r09_c11.json');progress(generatedNativeCount=p['generatedNativeCount']+1,status='seam_repair_received',currentPatch=name)
 print(json.dumps({'file':str(out),'sha256':sha(out),'pixels':list(im.size)}))
