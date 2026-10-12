from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
T=Path(__file__).resolve().parents[1];B=T.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
patch='p03_01';attempt='macro-topology-v02';old=T/'pipeline/receipts/p03_01.macro-topology-v01.receipt.json';receipt=json.loads(old.read_text())
receipt.update(visualDisposition='rejected: invented continuous inner vertical across y650-1013; bottom horizontal 72px too low; blue inset extends too far right',explicitlyRejected=True)
atomic_json(old,receipt)
req=json.loads((T/'pipeline/prompts/p03_01.macro-topology-v01.request.json').read_text())
target=Path(receipt['sourceOutputPath']);prompt='''Edit IMAGE1 only, preserving its 1254x1254 crop and quiet smooth stone material. Correct three localized geometry errors. (1) Completely remove the inner vertical grout at x337 between y663 and y1013, making this area one continuous quiet stone face. Keep the vertical segment above y655. (2) The long lower horizontal grout is currently at y1086: relocate this joint to y1013 across the crop. Keep other lines in place. The inner short vertical resumes only below y1013. (3) The blue-gray rectangle at lower-left is too wide and meets the lower joint directly. Its solid blue face must end at x245, leaving a pale stone/gray transition from x245 to337. Its solid blue face starts at y1144, with subdued gray-blue transition between y1090 and1144; pale stone remains between the relocated horizontal y1013 and the transition y1090. Preserve crisp restrained bevels and the quiet broad smooth faces. Keep the weak central horizontal division near y500, the right vertical atx965, and top horizontal aty87 unchanged. This is flat stone border and flat muted blue-gray inset, no water ripples or height changes. Images2-4 are reference context only, copy no scene/object. Image5 is material only. No extra lines or objects, no dense texture, no new composition, no zoom. Output opaque1254x1254 PNG.'''
pp=T/'pipeline/prompts'/f'{patch}.{attempt}.prompt.txt';rp=pp.with_name(f'{patch}.{attempt}.request.json')
assert not pp.exists() and not rp.exists();pp.write_text(prompt)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat())
req['references'][0]={'file':str(target),'sha256':sha(target),'role':'actual builtin native edit target; repair inner vertical and blue inset geometry'}
req['referenced_image_paths']=[r['file'] for r in req['references']]
atomic_json(rp,req);print(rp)
