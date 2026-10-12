from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib
from PIL import Image, ImageDraw
B = Path(__file__).resolve().parents[1]
tile,patch,attempt,base_attempt,source_name,lines_json,prefix=sys.argv[1:]
assert tile.endswith('_c05')
T=B/tile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json'
r=json.loads(base.read_text(encoding='utf-8-sig'))
source=Path(source_name); assert source.is_file()
lines=json.loads(lines_json)
guide=T/'pipeline/guides'/f'{patch}.{attempt}.mechanical-lines-not-art.png'
request=T/'pipeline/prompts'/f'{patch}.{attempt}.request.json'
prompt=request.with_name(f'{patch}.{attempt}.prompt.txt')
assert not any(p.exists() for p in (guide,request,prompt))
im=Image.new('RGB',(1254,1254),(245,245,245)); draw=ImageDraw.Draw(im)
for line in lines: draw.line(tuple(line),fill=(45,45,45),width=3)
guide.parent.mkdir(parents=True,exist_ok=True); im.save(guide)
der={'file':str(guide),'sha256':sha(guide),'pixels':[1254,1254],'category':'mechanical geometry constraint only; not game artwork','lines':lines,'derivedFrom':{'file':str(base),'sha256':sha(base)},'sourceResampling':False,'guidePixelsCompositedIntoFinal':False,'coordinateUncertainty':'visual interpretation of native strip and approved coarse layout; not verified acceptance','formalAccepted':False}
Path(str(guide)+'.derivation.json').write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
body=r['prompt'][r['prompt'].index('Use case:'):]
r['prompt']=prefix+'\nImage5 is a mechanical SAME1254 geometry schematic only; its dark lines specify the ONLY grooves and exact framing. Never copy white background or schematic strokes into finished artwork.\n\n'+body
prompt.parent.mkdir(parents=True,exist_ok=True);prompt.write_text(r['prompt'],encoding='utf-8')
r.update(promptFile=str(prompt),promptSha256=sha(prompt),preparedAtUtc=datetime.now(timezone.utc).isoformat(),editBaseRequest={'file':str(base),'sha256':sha(base)})
r['references']=r['references'][:4]
role = ('coarse continuity seed with actual native top/left strips; guide only, not final artwork; viewed before call'
        if 'continuity-seed' in source.name else 'actual native builtin return edit target; viewed before call')
r['references'][0]={'file':str(source),'sha256':sha(source),'role':role}
r['references'].append({'file':str(guide),'sha256':sha(guide),'role':'supporting mechanical line locations only; not final artwork'})
r['referenced_image_paths']=[ref['file'] for ref in r['references']]
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(request),'guide':str(guide)},ensure_ascii=False))
