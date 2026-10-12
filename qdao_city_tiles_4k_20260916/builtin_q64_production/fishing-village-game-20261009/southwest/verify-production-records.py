import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]; problems=[]; counts={'images':0,'references':0,'prompts':0,'receipts':0}
for path in sorted((ROOT/'native').glob('*.png.generation.json')):
    rec=json.loads(path.read_text(encoding='utf-8-sig'))
    entry={'record':path.name,'status':rec.get('status'),'file':rec['file']}
    fp=Path(rec['file'])
    try:
        with Image.open(fp) as im:
            size=list(im.size)
        ok=digest(fp)==rec['sha256'] and size==[rec['width'],rec['height']]==[1254,1254]
        if not ok: problems.append({'record':path.name,'kind':'image hash or dimension mismatch'})
        entry['imageVerified']=ok
        counts['images']+=1
    except Exception as ex: problems.append({'record':path.name,'kind':'image unreadable','error':str(ex)})
    entry['references']=[]
    for ref in rec['references']:
        rp=Path(ref['path'])
        ok=rp.is_file() and digest(rp)==ref['sha256']
        entry['references'].append({'path':ref['path'],'sha256':ref['sha256'],'verified':ok})
        counts['references']+=1
        if not ok: problems.append({'record':path.name,'kind':'reference hash mismatch or missing','path':str(rp)})
    prompt=Path(rec['prompt'])
    if prompt.is_file() and prompt.stat().st_size>0: counts['prompts']+=1
    else: problems.append({'record':path.name,'kind':'missing prompt'})
    receipt=Path(rec['evidence']['receipt'])
    if receipt.is_file():
        receipt_data=json.loads(receipt.read_text(encoding='utf-8-sig'))
        if receipt_data.get('finishedAtUtc') and receipt_data.get('result',{}).get('output_hint'): counts['receipts']+=1
        else: problems.append({'record':path.name,'kind':'receipt fields missing'})
    else: problems.append({'record':path.name,'kind':'missing receipt'})
    entry['actualModel']=rec.get('actualModel');entry['actualQuality']=rec.get('actualQuality')
    checks.append(entry)
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'counts':counts,'problemCount':len(problems),'problems':problems,'checks':checks,'scope':'All currently recorded native images; this verifies record integrity only, never visual or model/quality acceptance.'}
out=ROOT/'reference-integrity-audit-latest.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'counts':counts,'problemCount':len(problems),'problems':problems},ensure_ascii=False))
