from pathlib import Path
import sys,re,shutil
from PIL import Image
Z=Path(__file__).resolve().parent;sys.path.insert(0,str(Z))
import production_v2 as p
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
def strings(v):
 if isinstance(v,str):yield v
 elif isinstance(v,dict):
  for k,x in v.items():
   if k!='image_url':yield from strings(x)
 elif isinstance(v,list):
  for x in v:yield from strings(x)
known={};records=[]
for f in Z.rglob('*generation.json'):
 try:m=p.read(f)
 except Exception:continue
 src=m.get('sourceHostFile',m.get('hostOutputPath',m.get('evidence',{}).get('hostOutputPath')))
 if src:known[str(Path(src).resolve()).lower()]=f
receipts=[];unmapped=[];missing=[]
for tile in ('r07_c05','r06_c07','r07_c06'):
 T=Z/tile
 candidates=list((T/'receipts').glob('*result*.json'))+list((T/'bridges').glob('*/tool-receipt.json'))
 for f in candidates:
  try:m=p.read(f)
  except Exception:continue
  found=set()
  for s in strings(m):
   if 'generated_images' not in s:continue
   if s.lower().endswith('.png') and s[:2].endswith(':') and '\n' not in s and len(re.findall(r'[A-Za-z]:',s))==1:found.add(s)
   for match in re.findall(r'[A-Za-z]:[\\/][^:\r\n"]*?generated_images[\\/][0-9a-fA-F-]{36}[\\/][^\\/: \r\n"]+\.png',s):found.add(match)
  for value in found:
   src=Path(value);key=str(src.resolve()).lower();entry={'receipt':ref(f),'hostFile':str(src),'hasGenerationRecord':key in known}
   if key in known:
    entry['generationRecord']=ref(known[key]);receipts.append(entry);continue
   if not src.is_file():missing.append(entry);continue
   with Image.open(src) as im:
    entry.update(format=im.format,pixels=list(im.size),opaque=im.convert('RGBA').getchannel('A').getextrema()==(255,255))
   entry['hostSha256']=p.sha(src)
   D=Z/'recovered-successful-host-outputs-20261012';D.mkdir(exist_ok=True);dst=D/(tile+'-'+src.name)
   if not dst.exists():shutil.copyfile(src,dst)
   assert p.sha(dst)==p.sha(src);entry['preservedCopy']=ref(dst);entry['notSelectedPendingWorldCoordinateEvidence']=True;unmapped.append(entry)
out=Z/'saved-successful-output-audit-20261012-v2.json'
p.write_json(out,{'createdAtUtc':p.now(),'scope':['r07_c05','r06_c07','r07_c06'],'status':'saved_receipts_and_generation_records_audited','knownGenerationHostOutputs':len(known),'receiptHostOutputsAlreadyIngested':len(receipts),'successfulHostOutputsRecoveredWithoutGenerationRecord':unmapped,'referencedHostFilesMissing':missing,'newGenerationSubmitted':False,'existingSourceFilesModified':False,'supersedesAudit':{'file':str(Z/'saved-successful-output-audit-20261012.json'),'reason':'Initial free-text parser accidentally combined the output directory and following complete image path; its reported157 missing paths were malformed parser matches, not actual missing image files.'},'notes':'Receipt-bound outputs copied only if not yet indexed; no model metadata invented and no current generation authorization inferred.'},replace=False)
print({'knownHosts':len(known),'boundReceiptOutputs':len(receipts),'recovered':len(unmapped),'missingHostFiles':len(missing)})
