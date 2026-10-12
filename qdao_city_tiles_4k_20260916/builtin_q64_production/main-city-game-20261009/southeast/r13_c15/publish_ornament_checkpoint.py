from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value): Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

mp = T/'repairs/ornaments-composition-v1.json'
m = read(mp)
assert sha(m['base']) == m['baseSha256']
replay = Image.open(m['base']).convert('RGB')
for step in m['steps']:
    assert sha(step['native']) == step['nativeSha256']
    assert sha(step['alpha']) == step['alphaSha256']
    native = Image.open(step['native']).convert('RGB')
    assert native.size == (1254,1254)
    replay.paste(native.crop(step['nativeCropBox']), tuple(step['tilePlacementBox'][:2]), Image.open(step['alpha']).convert('L'))
core = Image.open(m['candidate']['path']).convert('RGB')
context = Image.open(m['context']['path']).convert('RGB')
assert core.size == (4096,4096) and context.size == (4326,4326)
assert replay.tobytes() == core.tobytes() == context.crop((115,115,4211,4211)).tobytes()
assert sha(m['candidate']['path']) == m['candidate']['sha256']
assert sha(m['context']['path']) == m['context']['sha256']

now = datetime.now(timezone.utc).isoformat()
qa = {'tile':'r13_c15','reviewedAtUtc':now,'candidateSha256':m['candidate']['sha256'],
      'scope':'Two ornament removal regions at native pixel scale, including their composition perimeter.',
      'localVisualQA':'passed','exactReplayVerified':True,'formalAccepted':False,
      'findings':[
          {'repair':'remove-bell-v1','result':'Unapproved top tassel removed; green wall and wood structure remain continuous across the repair perimeter. Rabbit and steamer unchanged outside the mask.'},
          {'repair':'remove-extra-cap-v1','result':'Extra small bottom cap removed; floor grain and existing plank grooves continue across the repair perimeter. The approved large lower-left cap is retained.'}],
      'reviewImages':[str(T/'repairs/remove-bell-v1/applied-context-1254.png'),str(T/'repairs/remove-extra-cap-v1/applied-context-1254.png')],
      'remainingQA':'Internal table and lower-left wood discontinuities plus west bottom plank groove endpoints remain failed per independent-20261011/visual-qa.json.'}
qpath=T/'repairs/ornaments-visual-qa-v1.json'; write(qpath,qa)
latest=T/'candidate/latest-assembly.json'
baseline=T/'candidate/latest-base-assembly-34f6632d.json'
previous=read(latest)
if not baseline.exists():
    assert previous['candidate']['sha256'] == m['baseSha256']
    shutil.copyfile(latest,baseline)
elif previous['candidate']['sha256'] not in (m['baseSha256'],m['candidate']['sha256']):
    raise RuntimeError('A newer checkpoint exists; do not replace it with this ornament checkpoint')
write(latest,{'schemaVersion':1,'tile':'r13_c15','updatedAtUtc':now,
      'status':'ornaments_repaired_structural_seams_pending',
      'manifest':{'path':str(mp),'sha256':sha(mp)},'context':m['context'],'candidate':m['candidate'],
      'baseAssemblyPointer':str(baseline),'localVisualQA':str(qpath),'formalAccepted':False})
p=read(T/'progress.json')
p.update(updatedAt=now,status='ornaments_repaired_structural_seams_pending',candidate=m['candidate']['path'],context=m['context']['path'],
         assemblyManifest=str(mp),internalArtQA='failed_remaining_structural_discontinuities',internalSeamQA='failed',
         externalNeighborSeamQA='west_failed_other_edges_pending',localOrnamentQA='passed',localOrnamentQAReport=str(qpath),
         nextStep='Apply independently reviewed native repairs to table contour, lower-left board joint and three west plank groove ends; then repeat full seam and neighbor QA.',
         formalAccepted=False)
write(T/'progress.json',p)
print(json.dumps({'candidate':m['candidate'],'localOrnamentQA':'passed','formalAccepted':False}))
