import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
p='central-r12c04-deckrim-v01-r12_c04'
rp=ROOT/'qa'/f'{p}-report.json';r=load(rp)
art=ROOT/'qa'/f'{p}-candidate-4096.png'
assert r['validation']['mismatchedPixels']==0
review={'recordedAtUtc':now(),'status':'needs_local_repair_and_outer_edges','formalAccepted':False,'nativeSegmentsViewed':24,'baseCandidateSha256':'f718cfdfc34a304248844ed5e890e582ea04d214010db4ed930d6ba57c553968','repairPerimetersViewed':['top','bottom','left','right'],'repairOutcome':'large horizontal deck-rim ledge corrected; left repair border has small beam-edge step, not passed','pending':[{'location':'deck repair local left boundary around x735, lower diagonal beam edge','issue':'small geometry step at binary source change; refine selection or local repair'},{'location':'tile upper-left stair/low-wall turn around local x650..1200,y1700..2300','issue':'staircourse perspective and abrupt turn need localized layout reconciliation'},{'location':'central lotus right stamen cluster','issue':'confirm stray yellow cluster is part of same flower; not accepted yet'},{'location':'all outer tile edges','issue':'paired north/west/east/south native edge review pending'}]}
vp=ROOT/'qa/central-r12c04-review-20261013.json';dump(vp,review)
a={'path':str(art),'sha256':hashfile(art),'dimensions':[4096,4096],'record':str(rp),'sourceReport':str(rp),'sourceIdMask':str(ROOT/'qa'/f'{p}-source-id-mask.png'),'nativeSourceCount':17,'nativePixelsVerified':True,'internalPassed':False,'internalTileSeamsPassed':False,'allOuterTileEdgesPassed':False,'formalAccepted':False,'review':str(vp),'internalStatus':'all24 internal segments and four repair perimeters inspected; localized geometry repairs pending'}
d=load(ROOT/'qa/expansion-central-worker-map.json');d['candidateArtifacts']['r12_c04']=a;d['updatedAtUtc']=now();dump(ROOT/'qa/expansion-central-worker-map.json',d)
print({'tile':'r12_c04','completeCorePositions':16,'savedSourceVersionsThisBatch':19,'candidate':a['path'],'sha256':a['sha256'],'internalPassed':False})
