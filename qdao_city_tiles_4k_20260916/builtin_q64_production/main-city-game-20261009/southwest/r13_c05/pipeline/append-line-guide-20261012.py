from pathlib import Path
from PIL import Image,ImageDraw
import json,sys,hashlib,datetime
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest');tile,patch,attempt,rejected,reason,lines=sys.argv[1:];P=B/tile/'pipeline';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();coords=[list(map(int,x.split(','))) for x in lines.split(';')]
q=P/'guides'/f'{patch}.{attempt}.line-guide-not-art.png';assert not q.exists();im=Image.new('RGB',(1254,1254),(194,198,197));d=ImageDraw.Draw(im)
for xy in coords:d.line(xy,fill=(90,94,93),width=7)
d.text((700,50),'GEOMETRY GUIDE ONLY - NO ART',fill=(70,70,70));im.save(q)
der={'file':str(q),'sha256':sha(q),'category':'mechanical single-line geometry schematic, not game artwork','pixels':[1254,1254],'lines':coords,'purpose':'builtin geometry constraint only','guidePixelsCompositedIntoFinal':False,'sourceLocalGuide':{'file':str(B/tile/'guides'/f'{patch}.layout-only.png'),'sha256':sha(B/tile/'guides'/f'{patch}.layout-only.png')},'coordinateUncertainty':'original overview pixels coarse; guide is interpretation, not verified tolerance or final acceptance','formalAccepted':False};Path(str(q)+'.derivation.json').write_text(json.dumps(der,indent=2)+'\n',encoding='utf-8')
request=P/'prompts'/f'{patch}.{attempt}.request.json';r=json.loads(request.read_text());assert len(r['references'])==4;r['referenced_image_paths'].append(str(q));r['references'].append({'file':str(q),'sha256':sha(q),'role':'Image5 single-line layout schematic geometry only, never final art'});r['lineGuideDerivation']={'file':str(q)+'.derivation.json','sha256':sha(str(q)+'.derivation.json')};request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if rejected!='none':
 receipt=P/'receipts'/f'{patch}.{rejected}.receipt.json';v=json.loads(receipt.read_text());out=receipt.with_name(receipt.name.replace('.receipt.json','.disposition.json'));assert not out.exists();out.write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':v['native'],'explicitlyRejected':True,'reason':reason,'notIngestedOrSelected':True,'localExtractionIntoFinal':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(request),'guide':str(q),'refs':5}))
