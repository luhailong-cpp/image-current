import sys,json,hashlib,datetime,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
name=sys.argv[1];source=Path(sys.argv[2])
target=root/(name+'.generated-v1.png')
assert not target.exists(),target
shutil.copy2(source,target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
request=root/(name+'.request-v1.json')
record={'schemaVersion':1,'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'route':'builtin-image_gen','actualModel':None,'requestedSize':[1254,1254],'actualSize':list(Image.open(target).size),'toolReturnedPath':str(source),'savedPath':str(target),'sha256':sha(target),'requestPath':request.name,'requestSha256':sha(request),'operation':'unaltered copy','status':'native-generated-candidate-pending-QA'}
with (root/(name+'.receipt-v1.json')).open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps(record))
