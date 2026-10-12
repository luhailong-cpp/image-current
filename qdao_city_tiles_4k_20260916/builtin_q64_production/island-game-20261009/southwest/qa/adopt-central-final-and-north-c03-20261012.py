from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
review=ROOT/'qa'/'central-r11c04-resume-final-root-review.json'
prefix='central-goldfascia-lower-v07-r11_c04';report=ROOT/'qa'/(prefix+'-report.json');r=load(report)
assert r['validation']['mismatchedPixels']==0 and r['validation']['pixelCount']==4096**2
for o in r['outputs'][:2]:assert hashfile(o['path'])==o['sha256']
dump(review,{'reviewer':'root','checkedAtUtc':now(),'candidate':r['outputs'][0],'report':{'path':str(report),'sha256':hashfile(report)},'internalReview':{'status':'pass','segmentsViewed':24,'native100Montages':[str(ROOT/'qa'/(prefix+'-'+axis+'-'+name+str(i)+'-native100.png')) for axis,name in [('vertical','row'),('horizontal','column')] for i in range(1,5)],'note':'Final golden fascia localized repairs and crisp pond repair inspected; all24 original core seam segments re-viewed at native scale.'},'pairedEdges':{'west-r11_c03':{'status':'geometry_pass','segmentsViewed':4,'note':'Roof courses, cap row, timber beams, cream panel and door join remain continuous.'},'north-r10_c04':{'status':'needs_local_native_selection_repair','segmentsViewed':4,'issues':[{'globalApproxBox':[13580,40935,13700,40985],'note':'Blue roof course end has horizontal black spur at tile boundary.'},{'globalApproxBox':[14336,40935,14390,40985],'note':'Possible black groove spur at left of paired c3 view.'}]},'east-r11_c05':'pending neighbor generation','south-r12_c04':'pending neighbor generation'},'allOuterEdgesPassed':False,'formalAccepted':False,'independentReview':'pending'})
a={'path':r['outputs'][0]['path'],'sha256':r['outputs'][0]['sha256'],'dimensions':[4096,4096],'sourceIdMask':r['outputs'][1]['path'],'record':str(report),'sourceReport':str(report),'nativeSourceCount':len(r['inputs']),'nativePixelsVerified':True,'internalPassed':True,'internalTileSeamsPassed':True,'internalStatus':'pass root native24-segment review; independent review pending','review':str(review),'sharedEdges':{'west-r11_c03':'geometry_pass','north-r10_c04':'needs_local_native_selection_repair'},'allOuterTileEdgesPassed':False,'formalAccepted':False}
n=load(ROOT/'qa'/'expansion-north-worker-map.json')['candidateArtifacts']['r08_c03']
nr=load(n['sourceReport']);assert nr['validation']['mismatchedPixels']==0 and nr['validation']['pixelCount']==4096**2
assert hashfile(n['path'])==n['sha256']
for f in ['current-native-map.json','qa/expansion-central-worker-map.json']:
 d=load(ROOT/f);d.setdefault('candidateArtifacts',{})['r11_c04']=a
 if f=='current-native-map.json':d['candidateArtifacts']['r08_c03']=n
 d['updatedAtUtc']=now();dump(ROOT/f,d)
main=load(ROOT/'current-native-map.json');art=main['candidateArtifacts'];s=load(ROOT/'progress.json')
remaining={tile:[{'subrow':ri+1,'subcolumn':ci+1} for ri,row in enumerate(arr) for ci,stem in enumerate(row) if not stem] for tile,arr in main.items() if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list) and any(not x for row in arr for x in row)}
s.update(updatedAtUtc=now(),currentAdopted4kArtifacts=art,currentAdopted4kFiles={k:v['path'] for k,v in art.items()},candidate4kCount=len(art),complete4kCount=len(art),fullyCovered4kCount=len(art),remainingTiles=49-len(art),internalPassed4kCount=sum(bool(v.get('internalPassed') or v.get('internalTileSeamsPassed')) for v in art.values()),formalAcceptedCount=0,currentCandidate=a['path'],currentPatch='central r11c04 full16 and four repair stages reviewed; paired north roof source-selection repair pending',nextStep='Repair north r10c04/r11c04 join and continue central r12..14 c03/c04 missing cores; disjoint workers continue full southwest.',missingCoreCount=784-s['selectedCandidateCoreCount'],savedSourceRecordCount=len(list((ROOT/'native').glob('*.png.generation.json'))),remainingCoreCoordinates=remaining)
dump(ROOT/'progress.json',s)
resume=load(ROOT/'production-resume-20261012.json');resume.update(updatedAtUtc=now(),candidate4kCount=len(art),remainingTilesWithoutFullCandidate=49-len(art),savedSourceRecordCount=s['savedSourceRecordCount'],generatedNativeCount=s['generatedNativeCount'],selectedCandidateCoreCount=s['selectedCandidateCoreCount'],missingCoreCount=s['missingCoreCount'],currentAdopted4kFiles=art,currentCoordinate='r11_c04 north paired roof join repair; central remaining tiles next');dump(ROOT/'production-resume-20261012.json',resume)
assert hashfile(ROOT/'migration-freeze-20261011.json')=='3fa6ba6959db01995e5939314bfade83e68eecf2fcb1647bebad53e2a714f606'
print({'candidates':len(art),'internalPassed':s['internalPassed4kCount'],'selected':s['selectedCandidateCoreCount'],'generated':s['generatedNativeCount'],'formal':0})
