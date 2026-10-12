import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
d=Path(__file__).resolve().parents[1]
m=d/'candidate/r06_c06-candidate-minimum-error-11a5a56c171b.assembly.json'
a=json.loads(m.read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bad={
 'internal-x2048-segment02': 'Diagonal grout ends abruptly at crop (990,108).',
 'internal-x2048-segment03': 'Diagonal grout ends abruptly at crop (430,152), (818,126), and (1008,61).',
 'internal-x3072-segment01': 'Blue paving grout has disconnected ends around crop (940,230).',
 'internal-x3072-segment02': 'Pale curb grout is disconnected around crop (276,232).',
}
entries=[]
for q in a['qa']:
 n=Path(q['file']).stem
 if not n.startswith('internal-x'): continue
 assert sha(q['file'])==q['sha256']
 findings=[bad[n]] if n in bad else (['Tiny stone/grout nick near crop (1000,46); continuity remains visible; nonblocking.'] if n=='internal-x1024-segment03' else [])
 entries.append({'file':q['file'],'sha256':q['sha256'],'actuallyViewed':True,'nativePixelScale':1,'verdict':'blocking' if n in bad else ('passed_with_nonblocking_texture_variance' if findings else 'passed'),'findings':findings})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':a['output'],'assemblyManifest':{'file':str(m),'sha256':sha(m)},'reviewer':'root','method':'All twelve native 1024x320 vertical seam crops viewed. No approval inherited.','entries':entries,'blockingCount':len(bad),'internalQAComplete':False,'formalAccepted':False}
dest=d/'qa/root-vertical-review-11a5a56c171b.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(dest)
