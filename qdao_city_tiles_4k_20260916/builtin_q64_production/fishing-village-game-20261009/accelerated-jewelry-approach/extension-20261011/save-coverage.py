from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1];e=b/'extension-20261011'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
items=[]
for t in ['r05_c10','r05_c11']:
    im=Image.new('RGBA',(4096,4096),(0,0,0,0));cores=[]
    for r in range(1,5):
        for c in range(1,5):
            p=b/t/'records'/f'p{r}{c}.selection.json'
            if not p.exists():continue
            s=read(p);native=Image.open(s['file']).convert('RGBA');assert native.size==(1254,1254)
            im.paste(native.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));cores.append({'core':f'p{r}{c}','source':s['file'],'sha256':s['sha256']})
    out=b/t/'qa/native-coverage-partial.png';im.save(out)
    preview=im.copy();preview.thumbnail((1024,1024));preview.save(b/t/'qa/native-coverage-preview.png')
    items.append({'tile':t,'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions':[4096,4096],'selectedCoreCount':len(cores),'missingCoreCount':16-len(cores),'sources':cores,'classification':'Coverage inspection only; transparent holes are unproduced core regions, not a final candidate','nativePixelsResized':False})
report={'savedAt':datetime.now(timezone.utc).isoformat(),'tiles':items,'formalAccepted':False}
(e/'native-coverage-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'savedNativeCoverage':[{k:v for k,v in t.items() if k in ['tile','selectedCoreCount','missingCoreCount']} for t in items]}))
