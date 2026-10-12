from pathlib import Path
import json,hashlib,argparse
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--stem',required=True);p.add_argument('--change',required=True);a=p.parse_args()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((Z/'guides'/f'{a.target}.input.json').read_text(encoding='utf-8-sig'))
target=Z/'native'/f'{a.target}.png'
ref={'path':target.as_posix(),'sha256':sha(target),'nativeSize':[1254,1254],'role':'same-coordinate native edit target; '+a.change,'globalBox':old['globalBox'],'coreBox':old['coreBox'],'generationRecord':{'path':str(target)+'.generation.json','sha256':sha(str(target)+'.generation.json')},'coordinateEvidence':{'path':(Z/'guides'/f'{a.target}.input.json').as_posix(),'sha256':sha(Z/'guides'/f'{a.target}.input.json')}}
refs=[ref]+old['inputs'][:4]
rec={**old,'versionStem':a.stem,'attempt':a.stem.split('_')[-1],'inputs':refs,'imageGenReferencedImagePaths':[x['path'] for x in refs],'inputCount':len(refs),'operation':'same-coordinate native cell edit: '+a.change,'editTarget':ref}
for suffix,obj in [('input',rec),('references',refs)]:
 out=Z/'guides'/f'{a.stem}.{suffix}.json'
 assert not out.exists(),out
 out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(refs))
