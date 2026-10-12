import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest")
now=datetime.now(timezone.utc).isoformat()
refs=json.loads((z/'references.json').read_text(encoding='utf-8-sig'))
p=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg")
h=hashlib.sha256(p.read_bytes()).hexdigest()
assert h=='c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63'
refs[2]={'path':p.as_posix(),'role':'primary user-provided approved Daoist Q painterly style, future requests from 2026-10-10; do not copy UI, figures or night lighting','sha256':h,'dimensions':list(Image.open(p).size)}
(z/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
helper=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_lantern/r09_c15/assembly-contract-v1/snapshots/3c9fb69c334985b7-seam_helpers.py")
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='3c9fb69c334985b77a51b254b59b5945bec893e746bda0ff71b0d41dca167a48'
(z/'tools').mkdir(exist_ok=True)
shutil.copyfile(helper,z/'tools'/'seam_helpers.py')
ack={'status':'art_production_resumed','atUtc':now,'source':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/production-resume.json','newArtworkAllowed':True,'builtinOnly':True,'assignedRows':[8,14],'assignedColumns':[1,7],'target4kCount':49,'firstClosure':['r09_c04','r09_c05','r10_c04','r10_c05'],'nextStep':'Repair joint wood rails, redraw whole staircase structure, complete r10_c05 fourth row; inspect all shared edges and central corner; continue remaining assigned tiles.','formalAcceptedCount':0,'currentSelectedNativeSlotCount':80,'missingNativeCoreSlotCount':704,'primaryStyle':refs[2],'historicalRecordsUnchanged':True,'worldSize':None,'capacity5000Validated':False}
(z/'resume-ack-20261010.json').write_text(json.dumps(ack,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'))
progress.update(status='resumed_contiguous_2x2_production',updatedAtUtc=now,nextStep=ack['nextStep'],resumeAcknowledgement=(z/'resume-ack-20261010.json').as_posix(),dependencyWarningNote='Future style replaced by verified user JPG; byte-identical seam helper copied inside this zone. Historical missing paths preserved in old records.')
(z/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':ack['status'],'refs':refs,'helper':str(z/'tools'/'seam_helpers.py')}))

