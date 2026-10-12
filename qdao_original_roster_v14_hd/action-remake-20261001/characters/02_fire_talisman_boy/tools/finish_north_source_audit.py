from pathlib import Path
import hashlib,json,datetime
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
iv=json.loads((R/'inventory-run-north.json').read_text(encoding='utf-8-sig'))
rows=[];errors=[]
for e in iv['frames']:
 if e['direction'] not in ['N','W']:continue
 p=R/e['path'];rec=json.loads((R/e['native_evidence']).read_text(encoding='utf-8-sig'));side=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8-sig'))
 native=R/rec['native']['file'];im=Image.open(p);ni=Image.open(native)
 checks={'inventorySha':sha(p)==e['sha256'],'sidecarSha':sha(p)==side['sha256'],'recordSha':sha(p)==rec['export']['sha256'],'nativeSha':sha(native)==rec['native']['sha256'],'rgba1024':im.mode=='RGBA' and im.size==(1024,1024),'native1024OrLarger':min(ni.size)>=1024,'alpha':im.getchannel('A').getextrema()==(0,255),'fullCanvasExportExact':ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()==im.tobytes(),'modelEvidenceHonest':rec.get('actualModel') is None and rec.get('actualQuality') is None,'promptExists':(R/rec['prompt']).is_file()}
 if not all(checks.values()):errors.append({'frame':e['path'],'checks':checks})
 rows.append({'frame':e['path'],'sha256':sha(p),'record':e['native_evidence'],'native':rec['native'],'checks':checks})
duplicates=len({x['sha256'] for x in rows})!=len(rows)
out={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'N/W 32 formal frames and own source chains; no pixel modification','frames':rows,'errors':errors,'exactDuplicates':duplicates,'pass':len(rows)==32 and not errors and not duplicates,'dynamicOrArtPassImplied':False,'clientStatus':'not_integrated'}
(R/'reviews/finish-north-source-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pass':out['pass'],'count':len(rows),'errors':errors,'duplicates':duplicates}))
