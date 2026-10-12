from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib
b=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(b/'delivery/candidate-manifest.json')
checks=[]
for entry in [*m['sources'],m['regionCandidate']]:
    p=Path(entry['file'])
    exists=p.is_file()
    with Image.open(p) as im: dimensions=list(im.size)
    checks.append({'file':str(p),'exists':exists,'dimensions':dimensions,'dimensionsMatch':dimensions==entry['dimensions'],'sha256':sha(p),'shaMatches':sha(p)==entry['sha256']})
qa=[]
for entry in m['qaEvidence']:
    p=Path(entry['file'])
    qa.append({'file':str(p),'exists':p.is_file(),'shaMatches':p.is_file() and sha(p)==entry['sha256']})
tiles=m['coordinates']
raw=[p for t in tiles for p in (b/t/'native').glob('p*-v*.png')]
raw += [p for t in tiles for p in (b/t/'repairs').glob('*/native-result.png')]
raw += [b/'r04_c10/repairs/north-gold-v1/repair-native.png']
raw_dimensions=[]
for p in raw:
    with Image.open(p) as im: raw_dimensions.append(list(im.size))
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'scope':'Assigned four tiles only; recovery check of saved output without regeneration','generationResumed':False,'newGeneratedImages':0,'artifacts':checks,'qaEvidence':qa,'rawGeneratedFilesOnDisk':len(raw),'allRawDimensions1254':all(x==[1254,1254] for x in raw_dimensions),'selectedCoreCount':64,'formalAcceptedCount':0,'exteriorSeamsPending':True,'remainingNeighborPairs':{'north':[['r02_c10','r03_c10'],['r02_c11','r03_c11']],'south':[['r04_c10','r05_c10'],['r04_c11','r05_c11']],'west':[['r03_c09','r03_c10'],['r04_c09','r04_c10']],'east':[['r03_c11','r03_c12'],['r04_c11','r04_c12']]},'bottomRepairPriority':{'tile':'r04_c11','neighbor':'r05_c11','tileXInclusive':[958,1591],'globalXInclusive':[41918,42551],'globalBoundaryY':16384},'nextAction':'Deliver saved four-tile candidates; await cross-region native-neighbor seam review. Do not occupy new coordinates or regenerate completed cores.'}
report['pass']=all(c['exists'] and c['dimensionsMatch'] and c['shaMatches'] for c in checks) and all(c['exists'] and c['shaMatches'] for c in qa) and len(raw)==71 and report['allRawDimensions1254']
out=b/'delivery/resume-check-20261011.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if report['pass']:
    progress=read(b/'progress.json')
    progress['lastRecoveryCheckAt']=report['checkedAt']
    progress['lastRecoveryCheck']=str(out)
    progress['newGeneratedImagesThisRecovery']=0
    progress['remainingNeighborPairs']=report['remainingNeighborPairs']
    temp=b/'progress.recovery.tmp'
    temp.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(b/'progress.json')
print(json.dumps({'pass':report['pass'],'savedCandidates':len(checks)-1,'rawGeneratedFilesOnDisk':len(raw),'newGeneratedImages':0,'artifactMismatch':[c['file'] for c in checks if not c['shaMatches'] or not c['dimensionsMatch']],'qaEvidenceMismatch':[c['file'] for c in qa if not c['shaMatches']],'report':str(out)}))
