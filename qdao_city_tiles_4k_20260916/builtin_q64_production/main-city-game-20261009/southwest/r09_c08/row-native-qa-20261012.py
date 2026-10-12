from pathlib import Path
import sys,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent.parent
tile,assembly_name,row_s=sys.argv[1:]
assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
row=int(row_s)
assert 1<=row<=4
T=B/tile
assembly=Path(assembly_name)
assert assembly.is_relative_to(T)
A=json.loads(assembly.read_text(encoding='utf-8-sig'))
S=Path(A['output']['file'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(S)==A['output']['sha256']
D=T/'pipeline'/'qa'/assembly.parent.name/f'row{row:02d}-native-20261012'
D.mkdir(parents=True,exist_ok=True)
y=(row-1)*1024
with Image.open(S) as im:
    assert im.width==4096 and im.height>=row*1024
    boxes={'whole-row':[0,y,4096,y+1024]}
    boxes.update({f'vertical-x{x}':[x-119,y,x+119,y+1024] for x in (1024,2048,3072)})
    records=[]
    for name,box in boxes.items():
        p=D/(name+'.png')
        assert not p.exists()
        crop=im.crop(box)
        crop.save(p,format='PNG')
        records.append({'file':str(p),'sha256':sha(p),'nativePixels':list(crop.size),'cropBoxInCoreOutput':box,'sourceResampling':False,'operation':'exact native QA crop only; not new art or delivery'})
E={'tile':tile,'row':row,'sourceAssembly':str(assembly),'sourceAssemblySha256':sha(assembly),'sourceImage':str(S),'sourceImageSha256':sha(S),'crops':records,'formalAccepted':False,'actualModel':None,'actualQuality':None}
manifest=D/'derivation.json'
assert not manifest.exists()
manifest.write_text(json.dumps(E,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaFolder':str(D),'manifest':str(manifest),'cropCount':len(records)}))
