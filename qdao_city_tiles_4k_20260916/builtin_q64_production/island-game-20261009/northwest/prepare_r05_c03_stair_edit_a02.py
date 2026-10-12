from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((Z/'guides/r05_c03_s03_01_a01.input.json').read_text(encoding='utf-8-sig'))
stem='r05_c03_s03_01_a02'
p=Z/'native/r05_c03_s03_01_a01.png'
target={'path':p.as_posix(),'sha256':sha(p),'nativeSize':[1254,1254],'role':'same-coordinate native edit target; change only right staircase front orientation','globalBox':old['globalBox'],'coreBox':old['coreBox'],'generationRecord':{'path':str(p)+'.generation.json','sha256':sha(str(p)+'.generation.json')},'coordinateEvidence':{'path':(Z/'guides/r05_c03_s03_01_a01.input.json').as_posix(),'sha256':sha(Z/'guides/r05_c03_s03_01_a01.input.json')}}
refs=[target]+old['inputs'][:4]
rec={**old,'versionStem':stem,'attempt':'a02','inputs':refs,'imageGenReferencedImagePaths':[x['path'] for x in refs],'inputCount':len(refs),'operation':'same-coordinate native cell edit; change right stair front orientation only','editTarget':target}
for suffix,obj in [('input',rec),('references',refs)]:
 out=Z/'guides'/f'{stem}.{suffix}.json'
 assert not out.exists()
 out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(refs))
