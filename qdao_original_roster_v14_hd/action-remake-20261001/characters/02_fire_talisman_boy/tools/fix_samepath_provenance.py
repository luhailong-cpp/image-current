import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
count=0
for p in (R/'records').glob('*.json'):
    if p.name.endswith('.receipt.json'): continue
    d=json.loads(p.read_text(encoding='utf-8-sig'))
    if not isinstance(d,dict): continue
    previous=d.get('supersedes'); export=d.get('export',{})
    if not previous or not export.get('file'): continue
    dest=(R/export['file']).resolve()
    changed=False
    for ref in d.get('references',[]):
        if Path(ref['path']).resolve()==dest and ref.get('sha256')==export.get('sha256'):
            ref['sha256']=previous['sha256']; ref['sha256Evidence']='Corrected from pre-replacement SHA saved in supersedes; target was same path as export.';changed=True
    if changed:p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
print({'repaired_same_path_reference_records':count})
