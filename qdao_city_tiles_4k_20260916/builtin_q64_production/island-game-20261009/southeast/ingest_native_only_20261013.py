from workflow import *
from PIL import Image
import sys,shutil
pid,v,srcarg,receipt=sys.argv[1:];src=Path(srcarg);out=ROOT/'native'/f'{pid}_{v}.png'
assert not out.exists(),str(out)
req=read(ROOT/'prompts'/f'{pid}_{v}.request.json');pf=Path(req['promptPath'])
shutil.copy2(src,out)
with Image.open(out) as im:im.load();size=list(im.size);mode=im.mode
assert size==[1254,1254]
record={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','mode':mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'coordinate':patch(pid),'evidence':{'toolReceipt':receipt,'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'resizedAfterGeneration':False,'status':'native_saved_pending_actual_seam_review'}
write(Path(str(out)+'.generation.json'),record)
print(json.dumps({'file':str(out),'sha256':sha(out),'nativePixels':size}))
