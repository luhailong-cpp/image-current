from pathlib import Path
import argparse,json,hashlib
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--stem',required=True);a=p.parse_args()
assert not (Z/'native'/f'{a.stem}.png').exists() and not (Z/'receipts'/f'{a.stem}.receipt.json').exists()
rp=Z/'guides'/f'{a.stem}.references.json';ip=Z/'guides'/f'{a.stem}.input.json'
r=json.loads(rp.read_text());assert isinstance(r,list) and len(r)==5
omitted=r[4];r=r[:4];d=json.loads(ip.read_text());d['inputs']=r
d['generationReferenceStrategy']={'actualSubmittedCount':4,'fullNeighborNotSubmitted':omitted,'reason':'Target guide already contains exact unscaled native overlaps. Omit full neighbor to reduce whole-neighbor composition copying. Native neighbor coordinate/derivation evidence remains preserved.'}
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');ip.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stem':a.stem,'refsCount':4,'inputSha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'refsSha256':hashlib.sha256(rp.read_bytes()).hexdigest()}))
