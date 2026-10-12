from pathlib import Path
import json,sys,hashlib,datetime
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest');tile,patch,attempt,rejected,reason=sys.argv[1:];P=B/tile/'pipeline';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
request=P/'prompts'/f'{patch}.{attempt}.request.json';r=json.loads(request.read_text());guide=B/tile/'guides'/f'{patch}.layout-only.png';assert len(r['references'])==4;r['referenced_image_paths'].append(str(guide));r['references'].append({'file':str(guide),'sha256':sha(guide),'role':'Image5 original approved local coarse layout geometry only; viewed; not final artwork'});r['localGuideNotFinal']=True;request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if rejected!='none':
 receipt=P/'receipts'/f'{patch}.{rejected}.receipt.json';q=json.loads(receipt.read_text());out=receipt.with_name(receipt.name.replace('.receipt.json','.disposition.json'));assert not out.exists();out.write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':q['native'],'explicitlyRejected':True,'reason':reason,'notIngestedOrSelected':True,'localExtractionIntoFinal':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(request),'refs':len(r['references'])}))
