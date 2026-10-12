"""Resolve current-frame edit inputs from recorded host receipts, without copying images."""
from pathlib import Path
import hashlib, json, re, sys
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'provenance/foot-axis-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strings(v):
    if isinstance(v,dict):
        for item in v.values():yield from strings(item)
    elif isinstance(v,list):
        for item in v:yield from strings(item)
    elif isinstance(v,str):
        yield v
        try: nested=json.loads(v)
        except (ValueError,TypeError):return
        if isinstance(nested,(dict,list)):yield from strings(nested)
def run():
    rows=[]
    for row in read(ROOT/'final-selection.json'):
        if '--all' not in sys.argv and row['action']!='run':continue
        meta=read(ROOT/row['generationRecord']);generation=meta['sourceGeneration'];source=meta['source']
        candidates=[ROOT/source['file']]
        evidence=generation.get('evidence',{})
        values=[evidence]
        for s in strings(evidence):
            p=ROOT/s
            if s.endswith('.json') and p.is_file():values.append(read(p))
        for s in strings(values):
            s=s.replace('\\\\','\\')
            candidates.extend(Path(x) for x in re.findall(r'[A-Za-z]:[\\/][^\r\n\" ]+?\.png',s))
        matches=[]
        for p in candidates:
            if p.is_file() and sha(p)==source['sha256'] and str(p) not in matches:matches.append(str(p))
        rows.append({'action':row['action'],'direction':row['direction'],'frame':row['frame'],'final':row['file'],'finalSha256':row['sha256'],'nativeSha256':source['sha256'],'nativeInput':matches[0] if matches else None,'sourceRecord':row['generationRecord']})
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/('edit-inputs-all.json' if '--all' in sys.argv else 'edit-inputs.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frames':len(rows),'nativeResolved':sum(bool(r['nativeInput']) for r in rows),'missing':[r['direction']+str(r['frame']) for r in rows if not r['nativeInput']]}))
if __name__=='__main__':run()
