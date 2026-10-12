import sys,shutil
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
name='r10_c11_wall-junction_v01'
src=Path(sys.argv[1]); out=ROOT/'native'/f'{name}.png'
shutil.copy2(src,out)
im=Image.open(out); assert im.size==(1254,1254)
request=read(ROOT/'prompts'/f'{name}.request.json')
rec={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':src.as_posix(),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool does not disclose actual model or quality.','evidence':{'toolReceipt':'receipts/'+name+'.json','returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'prompt':request['promptPath'],'promptSha256':sha(Path(request['promptPath'])),'references':request['references'],'coordinate':{'tile':'r10_c11','sourceCandidateBox':request['sourceBox'],'nativeGlobalBox':[42381,39084,43635,40338],'coreLocalBox':[115,115,1139,1139],'candidateDestination':[1536,2335]},'resizedAfterGeneration':False,'status':'junction_candidate_pending_visual_and_incoming_edge_review'}
write(Path(str(out)+'.generation.json'),rec)
print(__import__('json').dumps({'file':out.as_posix(),'sha256':sha(out),'nativePixels':list(im.size)}))
