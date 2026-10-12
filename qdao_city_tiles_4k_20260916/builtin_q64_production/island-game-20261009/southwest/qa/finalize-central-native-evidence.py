import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
stem=sys.argv[1]
req=load(ROOT/'prompts'/f'{stem}.request.json');receipt=load(ROOT/'receipts'/f'{stem}.tool.json');rec=load(ROOT/'native'/f'{stem}.png.generation.json')
assert all(hashfile(ref['path'])==ref['sha256'] for ref in req['references'])
req.update(submitted=True,submittedAtUtc=receipt['recordedAtUtc'],promptSha256=hashfile(rec['prompt']))
dump(ROOT/'prompts'/f'{stem}.request.json',req)
rec['promptSha256']=req['promptSha256'];rec['receiptSha256']=hashfile(ROOT/'receipts'/f'{stem}.tool.json')
dump(ROOT/'native'/f'{stem}.png.generation.json',rec)
print({'stem':stem,'referencesVerified':True,'outputSha256':rec['sha256']})
