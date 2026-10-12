from workflow import *
from PIL import Image
import shutil,sys
name,source,receipt=sys.argv[1:4];src=Path(source);out=ROOT/'native'/f'{name}.png';assert not out.exists();shutil.copy2(src,out)
req=read(ROOT/'prompts'/f'{name}.request.json');pf=Path(req['promptPath'])
with Image.open(out) as im:im.load();size=list(im.size);mode=im.mode
assert size==[1254,1254]
rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'mode':mode,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'evidence':{'toolReceipt':receipt,'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'tile':req['tile'],'tileRelativeOrigin':req['tileRelativeOrigin'],'resizedAfterGeneration':False,'status':'candidate_pending_visual_and_outer_join_review'}
write(Path(str(out)+'.generation.json'),rec)
r=read(ROOT/'production-resume-20261012.json');r.update(updatedAtUtc=now(),status='builtin_native_continuation_active',inFlightRequests=[],latestNewOutput={'file':str(out),'sha256':sha(out),'nativeDimensions':size,'generatedAtUtc':rec['generatedAt']});r['firstNewOutput']=r.get('firstNewOutput') or r['latestNewOutput'];r['runtimeIncident']['resolvedBy']='A new original-route builtin image_gen request succeeded; prior agent revoked errors no longer describe current generation availability.';write(ROOT/'production-resume-20261012.json',r)
p=read(ROOT/'progress.json');p.update(updatedAt=now(),status='active_builtin_native_continuation',generationStopped=False,inFlight=False,generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),latestNewOutput=r['latestNewOutput'],lastError=None);write(ROOT/'progress.json',p)
print(json.dumps(r['latestNewOutput']))
