import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';source=QA/'pair-r09c06-c07-v1-context-native.png';im=Image.open(source);ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
items=[('upperwood',[3640,430,4894,1684]),('redfish',[3620,1500,4874,2754]),('lowerwood-floor',[3650,2940,4904,4194])];records=[]
for name,box in items:
 p=QA/('pair-r09c06-c07-'+name+'-source-native-v1.png');assert not p.exists();im.crop(box).save(p);r={'file':ref(p),'source':ref(source),'contextBox':box,'pairTileContextBox':[v-115 for v in box],'globalContextBox':[box[0]+20365,box[1]+32653,box[2]+20365,box[3]+32653],'dimensions':[1254,1254],'operation':'exact native integer crop only','nativePixelsResampled':False};Path(str(p)+'.derivation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');records.append(r)
p=QA/'pair-r09c06-c07-local-repair-plan-v1.json';assert not p.exists();p.write_text(json.dumps({'schemaVersion':1,'sourcePairTrace':ref(QA/'pair-r09c06-c07-v1-trace.json'),'repairs':records,'status':'3 native repair targets pending generation'},indent=2)+'\n',encoding='utf-8');print(ref(p))
