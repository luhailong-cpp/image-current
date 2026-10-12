"""Preserve textual evidence before replacing a visually rejected generated frame."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parent
action,direction,number,tag,reason=sys.argv[1:6]
stem=f'{int(number):02}'
record=ROOT/f'runtime/{action}/{direction}/{stem}.png.generation.json'
if not record.exists(): record=ROOT/f'records/{action}/{direction}/{stem}.generation.json'
data=json.loads(record.read_text(encoding='utf-8-sig'))
prompt=ROOT/f'prompts/{action}/{direction}/{stem}.txt'; prompt_dest=prompt.with_name(f'{stem}.{tag}.txt')
assert not prompt_dest.exists();prompt.rename(prompt_dest)
receipt=ROOT/f'records/{action}/{direction}/{stem}.receipt.json'
if receipt.exists():
 receipt_dest=receipt.with_name(f'{stem}.{tag}.receipt.json');assert not receipt_dest.exists();receipt.rename(receipt_dest)
 data.setdefault('evidence',{})['receipt']=receipt_dest.relative_to(ROOT).as_posix()
data['prompt']=prompt_dest.relative_to(ROOT).as_posix();data['disposition']='rejected; runtime image replaced after corrected generation';data['rejectionReason']=reason
out=ROOT/f'records/{action}/{direction}/{stem}.{tag}.rejected.json';assert not out.exists();out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
