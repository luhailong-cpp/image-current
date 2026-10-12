from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
southPrefix='central-pond-right-crisp-v02-r11_c04';northPrefix='central-north-roof-reselect-v01-r10_c04'
review=ROOT/'qa'/'central-r11c04-pond-right-crisp-v02-west-supplement.json';assert review.exists()
updates={}
for tile,prefix in [('r10_c04',northPrefix),('r11_c04',southPrefix)]:
 rp=ROOT/'qa'/(prefix+'-report.json');r=load(rp);assert r['validation']['mismatchedPixels']==0 and r['validation']['pixelCount']==4096**2
 for o in r['outputs'][:2]:assert hashfile(o['path'])==o['sha256']
 a={'path':r['outputs'][0]['path'],'sha256':r['outputs'][0]['sha256'],'dimensions':[4096,4096],'sourceIdMask':r['outputs'][1]['path'],'record':str(rp),'sourceReport':str(rp),'nativeSourceCount':len({x['sha256'] for x in r['inputs']}),'sourceInputRecordCount':len(r['inputs']),'nativePixelsVerified':True,'internalPassed':True,'internalTileSeamsPassed':True,'allOuterTileEdgesPassed':False,'formalAccepted':False,'mode':'native exact same-global-coordinate binary selection, no interpolation/feathering/painting/warping','review':str(review),'pairedNorthReview':str(ROOT/'qa'/'central-r11c04-resume-final-west-review.json')}
 if tile=='r10_c04':a.update(connectedGroupEdgesPassed=True,internalStatus='previously passed internal/group edges unchanged outside lower north-roof paired repair; repair perimeter independently passed',sharedEdges={'south-r11_c04':'geometry_pass'})
 else:a.update(internalStatus='all24 internal segments reviewed with five localized repair stages; independent right pond supplement passed',sharedEdges={'north-r10_c04':'geometry_pass','west-r11_c03':'geometry_pass'},pendingDetailReview={'southBalusterFinial':'check original soft stone sphere detail against new south neighbor when native pair available'},eastSouthNeighborsPending=True)
 updates[tile]=a
for filename in ['current-native-map.json','qa/expansion-central-worker-map.json']:
 d=load(ROOT/filename);d.setdefault('candidateArtifacts',{}).update(updates if filename=='current-native-map.json' else {'r11_c04':updates['r11_c04']});d['updatedAtUtc']=now();dump(ROOT/filename,d)
main=load(ROOT/'current-native-map.json');main['candidateArtifacts']['r11_c03'].setdefault('sharedEdges',{})['east-r11_c04']='geometry_pass';dump(ROOT/'current-native-map.json',main)
s=load(ROOT/'progress.json');s.update(updatedAtUtc=now(),currentAdopted4kArtifacts=main['candidateArtifacts'],currentAdopted4kFiles={t:a['path'] for t,a in main['candidateArtifacts'].items()},internalPassed4kCount=sum(bool(a.get('internalPassed') or a.get('internalTileSeamsPassed')) for a in main['candidateArtifacts'].values()),currentCandidate=updates['r11_c04']['path'],currentPatch='central r11c04 repaired pond and paired north roof adopted; r12c03 generation underway',currentTile='r12_c03',nextStep='Complete central missing cores r12..14 c03/c04, inspect full tiles and paired edges; workers continue their disjoint regions.',formalAcceptedCount=0)
for e in s['pendingOuterEdges']:
 if e['tile']=='r10_c04' and e['side']=='south':e.update(status='geometry_pass root and independent reviewer',review=str(ROOT/'qa'/'central-r11c04-resume-final-west-review.json'))
s['outerEdgesPendingCount']=sum('pass' not in e['status'] for e in s['pendingOuterEdges']);s['currentCombinedHistorical']=s.get('currentCombined');s['currentCombinedNote']='Previously passed core-group snapshot retains original r10c04 variant; latest currentAdopted4kFiles is authoritative.';dump(ROOT/'progress.json',s)
res=load(ROOT/'production-resume-20261012.json');res.update(updatedAtUtc=now(),currentAdopted4kFiles=main['candidateArtifacts'],currentCoordinate='r12c03 native generation; r11c04 internally reviewed with paired north/west pass, east/south pending');dump(ROOT/'production-resume-20261012.json',res)
dump(ROOT/'qa'/'central-pond-v02-and-north-adoption-20261012.json',{'createdAtUtc':now(),'adopted':updates,'rootNativeViewsActuallySeen':['all4 north reselection perimeter views','all4 north paired panels','all4 pond-right-v02 perimeter views','final horizontal-column4 and vertical-row3/4 native seam panels'],'independentReviews':[str(review),str(ROOT/'qa'/'central-r11c04-resume-final-west-review.json')],'formalAccepted':False,'originalsUnchanged':True})
print({'adopted':{t:a['sha256'] for t,a in updates.items()},'internalPassed':s['internalPassed4kCount'],'formal':0})
