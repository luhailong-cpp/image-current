from pathlib import Path
from datetime import datetime,timezone
import json,shutil,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import production as p
stem='r10_c04_s02_03_v01'
reqpath=ROOT/'prompts'/(stem+'.request.json')
recpath=ROOT/'native'/(stem+'.png.generation.json')
req=p.load(reqpath);rec=p.load(recpath)
archive=ROOT/'receipts'/(stem+'.planned-request-before-guide-collision.json')
assert not archive.exists()
shutil.copy2(reqpath,archive)
planned=req['references'][0]
guide=Path(planned['path']);actual=p.metadata(guide,'coordinate edit target; TOP+RIGHT same-coordinate native strips, RIGHT wins corner after another worker rebuilt guide before generation')
note={'detectedAtUtc':p.now(),'cause':'Other worker prepared the same stem before request-collision check, replacing guide and coordinates with same TOP/RIGHT neighbors but RIGHT-last paste order. Other worker confirmed no imagegen was called.','plannedReference':planned,'actualSavedReference':actual,'guideMtimeUtc':datetime.fromtimestamp(guide.stat().st_mtime,timezone.utc).isoformat(),'promptMtimeUtc':datetime.fromtimestamp((ROOT/'prompts'/(stem+'.prompt.txt')).stat().st_mtime,timezone.utc).isoformat(),'evidence':'Guide modification predates prompt creation and subsequent imagegen invocation. Actual submitted bytes inferred from the sole modified path, mtime and other worker report; builtin tool does not return input-byte hashes. Prompt intended TOP-priority but actual guide has RIGHT-priority at corner.','originalRequestArchive':archive.as_posix(),'geometryDifferenceScope':'230x230 top-right overlap corner; same coordinate sources and layout otherwise.','nativeOutputUnaffected':True}
for path,obj in [(reqpath,req),(recpath,rec)]:
 obj['references'][0]=actual
 obj['referenceCorrection']=note
 p.dump(path,obj)
p.dump(ROOT/'qa'/(stem+'-guide-collision-audit.json'),note)
print(json.dumps(note))

