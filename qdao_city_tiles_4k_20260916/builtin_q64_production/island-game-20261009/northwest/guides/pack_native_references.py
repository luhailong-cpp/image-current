from pathlib import Path
from PIL import Image
import json,hashlib,sys
p=Path(sys.argv[1]); rec=json.loads(p.read_text(encoding='utf-8-sig'))
assert len(rec['inputs']) > 5
sources=rec['inputs'][4:]; ims=[Image.open(x['path']).convert('RGB') for x in sources]
assert len(set(im.height for im in ims))==1
out=p.with_name(p.name.replace('.input.json','.native-reference-contact.png'))
assert not out.exists()
canvas=Image.new('RGB',(sum(im.width for im in ims),ims[0].height))
x=0; placements=[]
for source,im in zip(sources,ims):
    canvas.paste(im,(x,0)); placements.append(dict(source=source,box=[x,0,x+im.width,im.height],resized=False)); x+=im.width
canvas.save(out)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
derivation=dict(file=out.as_posix(),sha256=sha(out),operation='mechanical unresized horizontal reference contact sheet; no painting',size=list(canvas.size),sources=placements,finalArt=False)
out.with_suffix('.png.derivation.json').write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec['unpackedInputs']=rec['inputs']
rec['inputs']=rec['inputs'][:4]+[dict(path=out.as_posix(),sha256=sha(out),nativeSize=list(canvas.size),role='unresized native reference contact: '+'; '.join(str(i+1)+' from left = '+s['role'] for i,s in enumerate(sources)),derivedFrom=placements)]
p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out.as_posix())
