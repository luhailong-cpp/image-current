from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent.parent
def native_for(sidecar):
    s=json.loads(sidecar.read_text(encoding='utf-8-sig'));g=s['sourceGeneration'];e=g['evidence']
    if 'hostPath' in e:f=Path(e['hostPath'])
    else:
        p=Path(e.get('result',e.get('receipt','')));p=p if p.is_absolute() else ROOT/p
        z=json.loads(p.read_text(encoding='utf-8-sig'));raw=z.get('rawToolResult',z)
        if isinstance(raw,str):raw=json.loads(raw)
        m=re.search(r'as (C:.*?\.png) by default',raw.get('output_hint',''))
        if not m: raise ValueError(str(p))
        f=Path(m.group(1))
    assert hashlib.sha256(f.read_bytes()).hexdigest()==s['source']['sha256']
    return str(f)
if __name__=='__main__':
    out={}
    for d,frames in [('E',[3,4,11,12]),('SE',[3,4,5,6,11,12,13,14])]:
        for n in frames:out[f'{d}{n:02}']=native_for(ROOT/f'final/run/{d}/{n:02}.png.generation.json')
    (ROOT/'provenance/ground-contact-20261004/root-position-inputs.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
