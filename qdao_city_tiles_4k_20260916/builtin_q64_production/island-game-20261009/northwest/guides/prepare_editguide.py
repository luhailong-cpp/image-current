from pathlib import Path
from PIL import Image
import json,hashlib,sys
p=Path(sys.argv[1]); target=Path(sys.argv[2]); r=json.loads(p.read_text(encoding='utf-8-sig')); sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
im=Image.open(target).convert('RGB'); assert im.size==(1254,1254)
sources=[dict(path=target.as_posix(),sha256=sha(target),role='prior native edit target',nativeSize=[1254,1254])]
for n in r['neighbor']:
 im.paste(Image.open(n['path']).convert('RGB').crop(n['sourceCrop']),tuple(n['destination']));sources.append(n)
out=p.with_name(p.name.replace('.input.json','.native-editguide.png'));assert not out.exists();im.save(out)
out.with_suffix('.png.derivation.json').write_text(json.dumps(dict(operation='unresized native editing guide; preserve all selected neighbor overlaps',sources=sources,sha256=sha(out),finalArt=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['layoutOnlyGuide']=r['inputs'][0];r['inputs'][0]=dict(path=out.as_posix(),sha256=sha(out),role='native edit guide with exact neighbor strips; repair transition only',nativeSize=[1254,1254],derivedFrom=sources)
r['inputs'].append(sources[0]);p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
