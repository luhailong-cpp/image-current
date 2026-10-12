import json,sys,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'candidate/r03_c04-pipeline-minimum-error-5a45bea8726a-ccd4a3.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(BASE).convert('RGB')
defs={'diagonal-gold':{'box':[1653,1421,2907,2675],'roi':[1950,1780,2700,2270]},'finial-joint':{'box':[2463,397,3717,1651],'roi':[3000,740,3280,1160]}}
for name,d in defs.items():
    out=ROOT/name;out.mkdir(parents=True,exist_ok=True)
    context=out/'context-native.png';im.crop(d['box']).save(context)
    record={'id':name,'baseCandidate':str(BASE),'baseCandidateSHA256':sha(BASE),'contextTileBox':d['box'],'contextWorldBox':[d['box'][0]+12288,d['box'][1]+8192,d['box'][2]+12288,d['box'][3]+8192],'proposedRepairTileBox':d['roi'],'file':str(context),'sha256':sha(context),'pixels':[1254,1254],'nativeScale':1,'isLayoutUpscale':False}
    (out/'preparation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))

