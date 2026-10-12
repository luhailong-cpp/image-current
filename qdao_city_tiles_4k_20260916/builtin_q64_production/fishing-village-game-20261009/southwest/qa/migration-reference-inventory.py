import sys
sys.dont_write_bytecode=True
import json,re,hashlib,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent;workspace=Path('D:/work/image').resolve()
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def within(p,root):
 try:p.resolve().relative_to(root);return True
 except ValueError:return False
refs={}
for p in list((z/'native').glob('*.request.json'))+list((z/'native').glob('*.png.generation.json')):
 r=read(p)
 for v in r.get('references',[]):
  if isinstance(v,dict) and v.get('path'):refs[v['path']]=v.get('role','')
for v in read(z/'references.json'):refs[v['path']]=v.get('role','')
external=[];inside=[]
for path,role in refs.items():
 p=Path(path)
 if not p.is_absolute():p=z/p
 if within(p,workspace):
  if not within(p,z):inside.append({'path':p.as_posix(),'role':role,'exists':p.exists(),'sha256':sha(p) if p.exists() and p.is_file() else None})
 else:
  e={'path':p.as_posix(),'role':role,'exists':p.exists()}
  if p.is_file():
   h=sha(p);out=z/'migration-reference-archive'/(h[:16]+'-'+p.name);out.parent.mkdir(exist_ok=True)
   if not out.exists():shutil.copy2(p,out)
   assert sha(out)==h;e.update({'sha256':h,'archivedCopy':out.as_posix(),'byteExact':True})
  external.append(e)
rootOutputs=[]
for p in sorted((z/'native').glob('r11_c06*.png.generation.json')):
 r=read(p);im=Path(r['file']);receipt=Path(r['evidence']['receipt']);rootOutputs.append({'file':im.as_posix(),'sha256':r['sha256'],'verifiedSaved':im.exists() and sha(im)==r['sha256'],'receiptSaved':receipt.exists(),'status':r['status']})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Migration local inventory and byte-exact archival only; no new art or QA.','outsideWorkspaceReferences':external,'insideWorkspaceOutsideZoneReferences':inside,'rootR11SuccessfulOutputs':rootOutputs,'rootUnsavedSuccessfulOutputs':[r for r in rootOutputs if not r['verifiedSaved'] or not r['receiptSaved']],'generatedOriginalsPolicy':'All generated originals retained under C:/Users/luyua/.codex/generated_images; exact adopted native copies and receipts live in zone. Child receipts attest their outputs. No originals deleted.','gitWritten':False}
prod.write(z/'migration-reference-inventory-20261011.json',out)
print(json.dumps({'outsideWorkspaceReferences':len(external),'outsideWorkspaceCopied':sum('archivedCopy' in e for e in external),'insideWorkspaceOutsideZoneReferences':len(inside),'rootR11SavedOutputs':len(rootOutputs),'rootUnsavedSuccessfulOutputs':len(out['rootUnsavedSuccessfulOutputs'])}))
