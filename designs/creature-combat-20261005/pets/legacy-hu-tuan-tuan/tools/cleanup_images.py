"""Delete only this task's superseded pixel files after final verification."""
from pathlib import Path
import json, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['verification']['technicalPassed'] and manifest['verification']['presentFrames']==68
    assert (R/'records/final-registration.json').is_file()
    source=(R/'source').resolve()
    assert source.is_relative_to(R.resolve()) and source.name=='source'
    candidates=list(source.rglob('*.png'))
    candidates += [R/'design/E-native.png', R/'qa/cast-E-contact.png',R/'qa/cast-E-normal.png',R/'qa/cast-E-slow.png',R/'qa/hit-W-pre-registration-contact.png',R/'preview/cast-W/contact.png']
    candidates=[p.resolve() for p in candidates if p.is_file()]
    assert all(p.is_relative_to(R.resolve()) and 'runtime' not in p.relative_to(R).parts for p in candidates)
    entries=[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Final registered runtime and regenerated final previews verified; superseded source/intermediate pixel file removed per AGENTS retention policy'} for p in candidates]
    removed={e['file'] for e in entries}
    def mark(value):
        if isinstance(value,dict):
            for key,item in list(value.items()):
                if key=='derivedFrom':
                    for d in item if isinstance(item,list) else [item]:
                        if isinstance(d,dict) and d.get('file') in removed:
                            d.update(deleted=True,retained=False,deletionRecord='records/cleanup.json')
                else: mark(item)
            if value.get('file') in removed:
                value['imageRetention']='deleted after final export verification; textual source evidence retained'
        elif isinstance(value,list):
            for item in value: mark(item)
    for path in R.rglob('*.json'):
        try: d=json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError,OSError): continue
        original=json.dumps(d,ensure_ascii=False,sort_keys=True); mark(d)
        if json.dumps(d,ensure_ascii=False,sort_keys=True)!=original: path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    for p in candidates: p.unlink()
    report={'completedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'scope':str(R),'originalCrossWindowReferencesTouched':False,'hostManagedGenerationCacheTouched':False,'entries':entries,'deletedCount':len(entries)}
    (R/'records/cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Deleted {len(entries)} superseded image files; all 68 final runtime images retained.')
if __name__=='__main__': main()
