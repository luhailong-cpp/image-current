from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,sys,datetime
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch,version,source=sys.argv[1:4]
assert patch in ('r06_c12_p14','r06_c12_p24','r06_c12_p34','r06_c12_p44')
stem=patch+'-'+version;target=B/'native'/(stem+'.png')
assert not target.exists()
shutil.copyfile(source,target)
submission=read(B/'records'/(stem+'.submission.json'));receipt=B/'records'/(stem+'.receipt.json');coordinates=read(B/'records/r06_c12.coordinates.json')
coord=next(x for x in coordinates['patches'] if x['id']==patch)
im=Image.open(target);im.load()
record={'schemaVersion':1,'file':str(target),'sha256':sha(target),'patchId':patch,'version':version,'generatedAt':None,'observedAtUtc':read(receipt)['observedAtUtc'],'timeEvidence':'exact generation timestamp not disclosed; observedAtUtc is tool-return observation','width':im.width,'height':im.height,'nativeSize':list(im.size),'format':im.format,'metadataKeys':list(im.info.keys()),'coordinates':coord,'coordinateRecord':{'path':str(B/'records/r06_c12.coordinates.json'),'sha256':sha(B/'records/r06_c12.coordinates.json')},'tool':'image_gen.imagegen','route':'builtin','configSnapshot':submission['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selector and discloses neither actual value','prompt':{'path':str(B/'records'/(stem+'.prompt.txt')),'sha256':sha(B/'records'/(stem+'.prompt.txt'))},'references':submission['references'],'evidence':{'receipt':str(receipt),'receiptSha256':sha(receipt),'selectorsExposed':False,'nativeMetadataKeys':list(im.info.keys())},'source':{'path':source,'sha256':sha(source),'operation':'byte-for-byte copy; no transform'},'dimensionValidation':{'expected':[1254,1254],'actual':list(im.size),'passed':im.size==(1254,1254)},'usable':False,'formalAccepted':False,'status':'candidate_pending_review','nativeResizePerformed':False}
write(str(target)+'.generation.json',record)
assert im.size==(1254,1254)
for arg in sys.argv[4:]:
 side,name=arg.split('=',1);other=B/'native'/name
 neighbor=Image.open(other).convert('RGB');current=im.convert('RGB')
 if side=='left':
  expected=neighbor.crop((1024,0,1254,1254));actual=current.crop((0,0,230,1254))
  strip=Image.new('RGB',(256,1254));strip.paste(neighbor.crop((1011,0,1139,1254)),(0,0));strip.paste(current.crop((115,0,243,1254)),(128,0))
  sp=[1011,0,1139,1254];tp=[115,0,243,1254]
 elif side=='top':
  expected=neighbor.crop((0,1024,1254,1254));actual=current.crop((0,0,1254,230))
  strip=Image.new('RGB',(1254,256));strip.paste(neighbor.crop((0,1011,1254,1139)),(0,0));strip.paste(current.crop((0,115,1254,243)),(0,128))
  sp=[0,1011,1254,1139];tp=[0,115,1254,243]
 else:raise ValueError(side)
 short=other.name.split('_')[-1].split('-')[0]+'-'+patch.split('_')[-1]+'-'+version
 qp=B/'qa'/(short+'-core-seam.png');strip.save(qp)
 q={'kind':'native 1:1 seam audit only','side':side,'sources':[{'path':str(other),'sha256':sha(other)},{'path':str(target),'sha256':sha(target)}],'strip':{'path':str(qp),'sha256':sha(qp),'size':list(strip.size),'seamLocalAxisPosition':128,'neighborSourceBox':sp,'currentSourceBox':tp},'overlapRgbMeanAbsoluteDifference':ImageStat.Stat(ImageChops.difference(expected,actual)).mean,'allPixelsCompared':True,'resizing':False,'feathering':False,'visualQA':'pending; difference is not geometry acceptance','formalAccepted':False}
 write(B/'qa'/(short+'-check.json'),q)
 print(str(qp))
print(json.dumps({'nativePath':str(target),'size':im.size,'sha256':sha(target)}))

