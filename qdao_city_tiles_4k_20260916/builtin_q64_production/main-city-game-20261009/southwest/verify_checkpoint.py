
from production import *
selected=[]
selection=json.loads((T/'refinement'/'selection.json').read_text(encoding='utf-8-sig'))
for r in range(1,5):
    for c in range(1,5):
        n=pid(r,c);selected.append(T/selection[n] if n in selection else T/'native'/f'{n}.png.generation.json')
selected+=list((T/'repairs'/'native').glob('*.generation.json'))+list((ROOT/'r11_c05'/'native').glob('*.generation.json'))
errors=[];refs_count=0;entries=[]
for rp in selected:
    rec=json.loads(rp.read_text(encoding='utf-8-sig'));path=Path(rec['file'])
    if not path.exists() or sha(path)!=rec['sha256']:errors.append(f'Native hash mismatch: {path}')
    with Image.open(path) as im:
        if im.size!=(1254,1254):errors.append(f'Native size mismatch: {path}')
    if sha(rec['prompt'])!=rec['promptSha256']:errors.append(f'Prompt hash mismatch: {rp}')
    receipt=Path(rec['evidence']['toolReceipt'])
    rr=json.loads(receipt.read_text(encoding='utf-8-sig'))
    if rr.get('status')!='returned_image' or rr.get('tool')!='image_gen.imagegen':errors.append(f'Invalid receipt: {receipt}')
    for ref in rec['references']:
        refs_count+=1
        if not Path(ref['file']).exists() or sha(ref['file'])!=ref['sha256']:errors.append(f'Reference mismatch: {ref["file"]}')
    if rec.get('actualModel') is not None or rec.get('actualQuality') is not None:errors.append(f'Unexpected actual evidence: {rp}')
    entries.append({'record':str(rp),'recordSha256':sha(rp),'native':str(path),'sha256':rec['sha256'],'referencesChecked':len(rec['references'])})
files=[T/'repairs'/'output'/'r10_c05.repaired.candidate.png',ROOT/'r11_c05'/'output'/'r11_c05.partial-p01_01-p01_04.png']
out=[]
for f in files:
    with Image.open(f) as im:im.load();size=list(im.size);mode=im.mode
    out.append({'file':str(f),'sha256':sha(f),'pixels':size,'mode':mode})
report={'verifiedAtUtc':now(),'selectedNativeSourceCount':len(selected),'referenceChecks':refs_count,'generationRecordCount':len(list(ROOT.rglob('*.generation.json'))),'outputs':out,'entries':entries,'errors':errors,'passed':not errors,'noUpscaling':True,'actualModel':None,'actualQuality':None}
write(ROOT/'verification.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='entries'},ensure_ascii=False))
assert not errors

