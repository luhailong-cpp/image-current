import json,sys
from pathlib import Path
from PIL import Image
import pipeline as p
OUT=p.ROOT/'continuation-20261011';OUT.mkdir(exist_ok=True)
d=p.read(p.ROOT/'delivery-20261011-v1/delivery-manifest.json')
for t in d['tiles']:
 assert p.sha(t['candidate'])==t['sha256']
 for s in t['selectedNativeOrDerivedPatches']:p.native_info(s['file'])
pair=[next(t for t in d['tiles'] if t['tile']==n) for n in ('r03_c05','r04_c05')]
base=Image.new('RGB',(4096,1254));base.paste(Image.open(pair[0]['candidate']).crop((0,3184,4096,4096)),(0,0));base.paste(Image.open(pair[1]['candidate']).crop((0,0,4096,342)),(0,912))
info=p.save_png(OUT/'south-conflict-base-strip-native.png',base)
contexts=[]
for i,L in enumerate((0,947,1895,2842),1):
 dest=OUT/f'south-segment{i:02d}';dest.mkdir(exist_ok=True)
 c=p.save_png(dest/'context-native.png',base.crop((L,0,L+1254,1254)))
 rec={**c,'contextNorthTileBox':[L,3184,L+1254,4438],'contextWorldBox':[16384+L,11376,16384+L+1254,12630],'boundaryYInContext':912,'northCandidate':pair[0]['candidate'],'northSHA256':pair[0]['sha256'],'southCandidate':pair[1]['candidate'],'southSHA256':pair[1]['sha256'],'nativeScale':1,'resampled':False,'formalAccepted':False}
 p.put_json(dest/'preparation.json',rec);contexts.append(rec)
inventory={'createdAtUTC':p.now(),'verifiedDeliveredCandidates':[{k:t[k] for k in ('tile','candidate','sha256')} for t in d['tiles']],'verifiedSelectedNativeOrDerivedPatches':64,'unmergedKnownAcceptedRepairs':0,'basis':'Previous delivery chain includes roof-right, left ROI3, finial, diagonal gold, gold strip, rail, lamp/column, r04c05 shaft/stairs. Rejected trials remain unselected. No tool result reported outstanding by final worker handoffs.','newlyPreparedNativeContexts':contexts,'candidateCount':4,'formalAcceptedCount':0,'networkRestorationConfirmedByUserMessage':True,'firstPostRestorationImage':None}
p.put_json(OUT/'initial-local-audit.json',inventory)
record={'status':'local-audit-complete-awaiting-first-restored-builtin-result','updatedAtUTC':p.now(),'currentCandidateCount':4,'coveredAssignedCores':64,'newPixelsGeneratedThisRound':False,'mergedOutputsThisRound':[],'internalFullyPassedTileCount':0,'formalAcceptedCount':0,'externalEdgesPendingUnavailableNeighbors':6,'externalSegmentsPendingUnavailableNeighbors':24,'knownFailedExistingBoundarySegments':7,'remainingGenerationCoordinates':['r03_c04 roof shoulders near tile [583,1008,1278,1218]','r03_c05 internal roof/gold geometry and southern row s04_01..s04_04','r04_c04 rail material patch','r04_c05 minor material/pavement and southern lion-base band'],'blockers':['No first restored image result yet; user reports permission restored. North/east/west neighbor sources unavailable in last inventory.'],'audit':str(OUT/'initial-local-audit.json'),'deliveryIndex':str(p.ROOT/'delivery-20261011-v1/delivery-manifest.json'),'scope':'Only assigned four coordinates. No full-map completion claim.'}
p.put_json(p.ROOT/'local-continuation-20261011.json',record)
print(json.dumps({'out':str(OUT),'candidateCount':4,'selectedPatchesVerified':64,'unmergedAcceptedRepairs':0,'contexts':4}))
