from pathlib import Path
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
P=ROOT.parent
C=json.loads((P/'production-contract.json').read_text(encoding='utf-8-sig'))
T=ROOT/'r04_c04'
for d in ['layout-only','context','prompts','receipts','native','qa','candidate']:(T/d).mkdir(parents=True,exist_ok=True)
box=[12173,15245,13427,16499]
im=Image.open(C['layoutReference']).convert('RGB')
b=[box[0]*im.width/65536,box[1]*im.height/65536,box[2]*im.width/65536,box[3]*im.height/65536]
guide=im.transform((1254,1254),Image.Transform.EXTENT,b,Image.Resampling.BICUBIC)
guide.save(T/'layout-only/s04_01.layout-only.png')
old=P/'northwest/r05_c04/native/s01_01.png'
ni=Image.open(old).convert('RGB')
guide.paste(ni.crop((0,0,1254,230)),(0,1024))
guide.save(T/'context/s04_01.context.png')
region=im.crop((int(12288*im.width/65536),int(8192*im.height/65536),int(20480*im.width/65536),int(16384*im.height/65536)))
region.resize((1024,1024),Image.Resampling.NEAREST).save(ROOT/'assignment-layout-only.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=[T/'context/s04_01.context.png',T/'layout-only/s04_01.layout-only.png',old,Path(C['detailStyleReference']),Path(C['primaryStyleReference'])]
data={'tile':'r04_c04','patch':'s04_01','worldBoxWithHalo':box,'coreCrop':[115,115,1139,1139],'references':[{'path':str(p),'sha256':sha(p),'size':list(Image.open(p).size)} for p in refs],'nativeAnchor':{'sourceBox':[0,0,1254,230],'targetBox':[0,1024,1254,1254]},'actualModel':None,'actualQuality':None}
(T/'receipts/s04_01.preparation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'progress.json').write_text(json.dumps({'status':'generating_first_native_patch','nativeCount':0,'tilesComplete':0,'formalAcceptedCount':0,'nextCoordinate':'r04_c04/s04_01','ownedTiles':['r04_c04','r04_c05','r03_c04','r03_c05'],'builtinOnly':True,'paidApiAllowed':False},indent=2),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
