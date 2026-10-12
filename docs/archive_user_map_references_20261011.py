from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from PIL import Image
root=Path('D:/work/image')
target=root/'designs/user-references/map-style-20261011'
target.mkdir(parents=True,exist_ok=True)
names=[
'codex-clipboard-1bb4028f-b7ac-4aa6-9ad3-41e2742fc63b.jpg',
'codex-clipboard-5fadc52e-81ad-4e26-b563-dd9389b1a47e.jpg',
'codex-clipboard-fee3d0a5-b014-4146-8204-0b1e3b419ea8.jpg',
'codex-clipboard-656c91b2-1d9a-47b4-871a-31bbc817cd31.jpg',
'codex-clipboard-73774509-afff-4a5a-90d8-ff51e3ff1091.jpg',
'codex-clipboard-db15c873-5d45-4ba3-b925-59e645c84c89.jpg',
'codex-clipboard-d353a33b-0a3c-4407-8f5f-d11f2fc8a415.jpg',
'codex-clipboard-fa6eff2a-b4ce-41c0-8c1f-4dbe124b0896.jpg',
'codex-clipboard-9b242a2d-db45-400e-bffd-88974bec6011.jpg',
'codex-clipboard-d5d8f1a1-da68-4050-9879-5d2937250900.jpg',
'codex-clipboard-4343382b-cdfd-4f8f-a552-508084983a7b.jpg',
'codex-clipboard-c144ae2e-e430-4b8e-86b0-a1fbd613a0c7.jpg']
rows=[]
for i,name in enumerate(names,1):
    src=Path('C:/Users/luyua/AppData/Local/Temp')/name
    row={'inputOrder':i,'sourcePath':str(src),'role':'user-provided style reference, not production map'}
    if not src.is_file():
        row['status']='original_temp_not_present'
        rows.append(row);continue
    dst=target/name
    before=hashlib.sha256(src.read_bytes()).hexdigest()
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=before:
        raise RuntimeError('Refusing to overwrite differing archived reference: '+str(dst))
    if not dst.exists():shutil.copy2(src,dst)
    actual=hashlib.sha256(dst.read_bytes()).hexdigest()
    with Image.open(dst) as im: dimensions=list(im.size)
    row.update(status='archived_byte_exact',workspaceRelativePath=dst.relative_to(root).as_posix(),sha256=actual,hashMatches=before==actual,bytes=dst.stat().st_size,dimensions=dimensions)
    rows.append(row)
result={'schemaVersion':1,'archivedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Only 12 exact attachment paths supplied by this user in map conversation; no unrelated Temp or profile scan. Originals left in place.','files':rows,'archivedCount':sum(x['status']=='archived_byte_exact' for x in rows),'missingOriginalCount':sum(x['status']=='original_temp_not_present' for x in rows)}
(target/'archive-index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))

