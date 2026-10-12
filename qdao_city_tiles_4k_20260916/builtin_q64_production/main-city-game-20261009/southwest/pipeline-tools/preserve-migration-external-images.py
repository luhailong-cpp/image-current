from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,sys
B=Path(__file__).resolve().parents[1]; W=Path('D:/work/image').resolve()
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=B/'migration-preserved-external-20261011';out.mkdir(exist_ok=True)
found={}; errors=[]
def walk(v,source):
    if isinstance(v,dict):
        for vv in v.values():walk(vv,source)
    elif isinstance(v,list):
        for vv in v:walk(vv,source)
    elif isinstance(v,str) and len(v)<1000 and len(v)>3 and v[1:3] in (':\\',':/'):
        p=Path(v)
        if p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.gif','.bmp','.tiff'):return
        try:
            q=p.resolve()
            if q.is_relative_to(W):return
            found.setdefault(str(q),set()).add(str(source))
        except OSError:pass
for p in list(B.rglob('*.json')):
    if out in p.parents:continue
    try:walk(json.loads(p.read_text(encoding='utf-8-sig')),p)
    except (ValueError,OSError):pass
entries=[];copied=0
for source,refs in sorted(found.items()):
    p=Path(source);entry={'originalExternalPath':source,'referencedBy':sorted(refs)}
    if not p.is_file():
        entry.update(exists=False,workspaceCopy=None);errors.append(source);entries.append(entry);continue
    digest=sha(p);dest=out/(digest+p.suffix.lower())
    if not dest.exists():shutil.copy2(p,dest);copied+=1
    if sha(dest)!=digest:raise RuntimeError('Portable copy differs: '+str(dest))
    entry.update(exists=True,sha256=digest,bytes=p.stat().st_size,workspaceCopy=str(dest),copyVerified=True)
    entries.append(entry)
manifest={'savedAtUtc':now(),'purpose':'Preserve all externally referenced image files including rejected and superseded outputs for computer migration, without removing originals or altering receipts.','sourceFiles':entries,'missingSourcePaths':errors,'copiedThisRun':copied,'uniqueExternalPathCount':len(entries),'originalsPreserved':True}
atomic_json(out/'manifest.json',manifest)
print(json.dumps({'manifest':str(out/'manifest.json'),'externalImages':len(entries),'copied':copied,'missing':errors},ensure_ascii=False))

