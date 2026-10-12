from pathlib import Path
import sys,json,argparse
sys.dont_write_bytecode=True
import native_batch as n
B=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--key',required=True);p.add_argument('--tile',required=True);p.add_argument('--patch',required=True);p.add_argument('--source',required=True);p.add_argument('--version',required=True)
a=p.parse_args()
assert a.key.startswith('right-') and a.version.startswith('right-')
req=B/'requests'/f'{a.key}.request.json';prompt=B/'prompts'/f'{a.key}.txt';receipt=B/'receipts'/f'{a.key}.receipt.json'
r=json.loads(req.read_text(encoding='utf-8'))
assert r['prompt']==prompt.read_text(encoding='utf-8')
spec={'tile':a.tile,'patch':a.patch,'sourceOutputPath':a.source,'prompt':str(prompt),'receipt':str(receipt),'request':str(req),'references':[{'file':x,'role':f'Actual attached image {i+1}, role defined in saved prompt'} for i,x in enumerate(r['referenced_image_paths'])]}
sp=B/'requests'/f'{a.key}.register.json'
with sp.open('x',encoding='utf-8') as f:json.dump(spec,f,ensure_ascii=False,indent=2)
n.verify_contracts()
registered=n.register(sp,n.Scope(),a.version)
print(json.dumps(registered,ensure_ascii=False))

