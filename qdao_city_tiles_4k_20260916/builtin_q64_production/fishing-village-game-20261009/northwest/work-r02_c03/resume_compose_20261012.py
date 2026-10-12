from repair_composite import *
from datetime import datetime,timezone

D=W/'resume-20261012-v1'
n='r02_r03_roof_connector_v02'
req=read(D/(n+'.request.json'));rec=read(D/(n+'.receipt.json'))
original=Path(re.search(r' as (C:\\[^\n]+?\.png) by default',rec['output_hint']).group(1))
p=W/'native'/(n+'.png')
if not p.exists():shutil.copy2(original,p)
assert sha(original)==sha(p)
im=Image.open(p);assert im.size==(1254,1254)
g={'file':str(p),'sha256':sha(p),'generatedAtUtc':rec['returnedAtUtc'],'width':1254,'height':1254,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','globalNativeBox':req['globalNativeBox'],'globalCoreBox':[req['globalNativeBox'][0]+115,req['globalNativeBox'][1]+115,req['globalNativeBox'][2]-115,req['globalNativeBox'][3]-115],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in exposes no model/quality selectors or actual response metadata.','references':req['references'],'prompt':str(D/(n+'.prompt.txt')),'promptSha256':sha(D/(n+'.prompt.txt')),'evidence':{'request':str(D/(n+'.request.json')),'requestSha256':sha(D/(n+'.request.json')),'receipt':str(D/(n+'.receipt.json')),'receiptSha256':sha(D/(n+'.receipt.json'))},'toolOriginal':{'file':str(original),'sha256':sha(original)},'status':'candidate-pending-join-review'}
write(str(p)+'.generation.json',g)
F=D/'composition-v1';F.mkdir(exist_ok=True)
a,i,s=loadbase('converge-v1')
patch(a,i,s,n,117,top=(0,160),bottom=(1080,1253),left=(0,200),right=(1094,1253),mode='roof',out=F)
finish(F,a,i,s)
pair=Image.fromarray(a)
for j in range(4):pair.crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(F/f'south-{j+1}.png')
print(json.dumps({'file':str(p),'sha256':sha(p),'final':str(F)}))
