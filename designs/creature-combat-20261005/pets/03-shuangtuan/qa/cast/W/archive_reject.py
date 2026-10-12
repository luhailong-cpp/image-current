from pathlib import Path
import json, shutil, hashlib, sys
BASE=Path(__file__).resolve().parents[3]
n,tag,reason=sys.argv[1:]
stem=f'{int(n):02d}'
alias=f'{stem}-rejected-{tag}'
source=BASE/'source/cast/W'/f'{stem}.png'
dest=source.with_name(f'{alias}.png')
shutil.copyfile(source,dest)
record_path=BASE/'records/cast/W'/f'{stem}.generation.json'
record=json.loads(record_path.read_text(encoding='utf-8'))
shutil.copyfile(BASE/'records/cast/W'/f'{stem}.receipt.json',BASE/'records/cast/W'/f'{alias}.receipt.json')
shutil.copyfile(BASE/'prompts/cast/W'/f'{stem}.txt',BASE/'prompts/cast/W'/f'{alias}.txt')
record.update(file=f'source/cast/W/{alias}.png',sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),width=record['native']['width'],height=record['native']['height'],visualStatus='rejected: '+reason,prompt=f'prompts/cast/W/{alias}.txt',operation='native generated image; rejected before delivery')
record['evidence']['receipt']=f'records/cast/W/{alias}.receipt.json'
record.pop('derivedFrom',None)
(BASE/'records/cast/W'/f'{alias}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(alias)
