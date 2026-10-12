"""Versioned mechanical integration of native AI repairs; never paint or resample."""
import hashlib
import json
from pathlib import Path
from PIL import Image

Z = Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, obj): Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
def ref(p): return {'path':str(p), 'sha256':sha(p)}
def source(p):
    rec=Path(str(p)+'.derived.json')
    if not rec.exists(): rec=Path(str(p)+'.generation.json')
    data=read(rec)
    expected=data.get('sha256') or data.get('image',{}).get('sha256')
    assert sha(p)==expected, p
    return {**ref(p), 'derivedRecord' if rec.name.endswith('.derived.json') else 'generationRecord':ref(rec)}
def image(p):
    im=Image.open(p); im.load(); assert im.size==(1254,1254),p
    return im.convert('RGB')

old=Z/'tiles/r06_c12.candidate.png'
assert sha(old)=='997d0f2d213d60610c5e92f3314da18efbc93131419ea7dd2167c6c69207ae56'
sel=read(Z/'records/r06_c12.selection.json')
coords={v['id']:v for v in read(Z/'records/r06_c12.coordinates.json')['patches']}
beams=[('resume-20261010-beam-A-v1.png',[46405,21940,47659,23194]),('resume-20261010-beam-B-v1.png',[47179,21940,48433,23194])]
replacements={'r06_c12_p34':'resume-20261010-stall-upper-v1.png','r06_c12_p44':'resume-20261010-stall-lower-v1.png','r06_c12_p42':'r07_c12_northrepair42-v1.png','r06_c12_p43':'r07_c12_northrepair43-v1.png'}
outsel={'schemaVersion':1,'tile':'r06_c12','operation':'Native integer crop/paste only. Sources and previous candidate retained.','patches':{}}
for key,value in sel['patches'].items():
    inp=Z/(value if isinstance(value,str) else value['path'])
    box=coords[key]['nativeGlobalBox']; im=image(inp); parents=[source(inp)]; operations=[]
    if key in replacements:
        inp=Z/'native'/replacements[key]; im=image(inp); parents=[source(inp)]
        operations=[{'operation':'identity copy of complete native replacement','source':str(inp),'sourceCropBox':[0,0,1254,1254],'destinationBox':[0,0,1254,1254]}]
    else:
        for name,b in beams:
            intersection=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
            if intersection[0]>=intersection[2] or intersection[1]>=intersection[3]: continue
            path=Z/'native'/name
            crop=[intersection[0]-b[0],intersection[1]-b[1],intersection[2]-b[0],intersection[3]-b[1]]
            dest=[intersection[0]-box[0],intersection[1]-box[1],intersection[2]-box[0],intersection[3]-box[1]]
            im.paste(image(path).crop(crop),dest[:2]); parents.append(source(path))
            operations.append({'operation':'integer crop and opaque paste','source':str(path),'sourceCropBox':crop,'destinationBox':dest,'globalIntersection':intersection})
    if operations:
        out=Z/'native'/f'{key}-resume-v2.png'
        assert not out.exists(),out
        im.save(out)
        assert Image.open(out).convert('RGB').tobytes()==im.tobytes()
        write(Path(str(out)+'.derived.json'),{'schemaVersion':1,**ref(out),'file':str(out),'patchId':key,'coordinates':coords[key],'nativeGlobalBox':box,'pixels':[1254,1254],'derivedFrom':parents,'operation':'Ordered native integer crop and opaque paste; no resampling, painting, blending or color transforms','steps':operations,'actualModel':None,'actualQuality':None,'formalAccepted':False})
        outsel['patches'][key]=ref(out)
    else: outsel['patches'][key]=ref(inp)
write(Z/'records/r06_c12.selection-v2.json',outsel)
assert sha(old)=='997d0f2d213d60610c5e92f3314da18efbc93131419ea7dd2167c6c69207ae56'
print(json.dumps({'selection':str(Z/'records/r06_c12.selection-v2.json'),'nativeSources':16,'oldCandidatePreserved':True}))
