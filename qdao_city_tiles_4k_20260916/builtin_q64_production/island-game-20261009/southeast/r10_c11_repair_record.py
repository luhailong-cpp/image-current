import sys,shutil
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
name=sys.argv[1];src=Path(sys.argv[2]);out=ROOT/'native'/f'{name}.png'
shutil.copy2(src,out);im=Image.open(out);assert im.size==(1254,1254)
q=read(ROOT/'prompts'/f'{name}.request.json');box=q['sourceBox']
rec={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':src.as_posix(),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin does not disclose actual model or quality.','evidence':{'toolReceipt':'receipts/'+name+'.json','returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'prompt':q['promptPath'],'promptSha256':sha(Path(q['promptPath'])),'references':q['references'],'coordinate':{'tile':'r10_c11','sourceCandidateBox':box,'nativeGlobalBox':[box[0]+40960,box[1]+36864,box[2]+40960,box[3]+36864]},'resizedAfterGeneration':False,'status':'repair_pending_visual_and_incoming_edge_review'}
write(Path(str(out)+'.generation.json'),rec)
print(__import__('json').dumps({'file':out.as_posix(),'sha256':sha(out),'nativePixels':list(im.size)}))
