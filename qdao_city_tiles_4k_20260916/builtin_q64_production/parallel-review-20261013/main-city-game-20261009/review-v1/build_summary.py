from review_existing import *
import re
from zoneinfo import ZoneInfo

BASE=OUT.parent
NW=BASE/'northwest-census/v001'
SW=BASE/'southwest-census/v01'
EAST=BASE/'east-census/v20261013-02'

def record_path(d):
    return d.get('file') or d.get('path')

def slot(s):
    s=str(s)
    m=re.fullmatch(r'[sp](\d{2})_(\d{2})',s)
    if m: return [int(m[1]),int(m[2])]
    m=re.fullmatch(r'p([1-4])([1-4])',s)
    if m: return [int(m[1]),int(m[2])]
    raise ValueError(s)

def owner(r,c):
    if f'r{r:02}_c{c:02}' in ['r03_c04','r03_c05','r04_c04','r04_c05']: return 'accelerated-yamen-north'
    return ('north' if r<=8 else 'south')+('west' if c<=8 else 'east')

def build():
    normalized={}
    for t in read(NW/'current-tiles.json')['tiles']:
        k=t['coordinate']; cand=t.get('candidate') or {}
        adopted=t['availableForDelivery'] and cand.get('exists')
        normalized[k]={'coordinate':k,'owner':t['owner'],'current4KCandidate':{'file':record_path(cand),'sha256':cand.get('sha256'),'pixels':cand.get('pixels')} if adopted else None,'fullCurrent4KCandidate':bool(adopted),'selectedCoreSlots':[slot(x['id']) for x in t.get('selectedSources',[]) if x.get('exists')],'selectedCoreCount':t['selectedPatchCount'],'internalStatus':t['internalQA'],'formalAccepted':False,'worldBox':t['worldBox'],'sourceIndex':str(NW/'current-tiles.json'),'sourceManifest':t['assemblyManifest'],'note':'Old r07_c06 candidate excluded because current selection differs' if not adopted else 'Existing reviewed local candidate; external perimeter remains open'}
    for t in read(SW/'current-tiles.json'):
        k=t['tile']; adopted=bool(t.get('currentCandidate'))
        normalized[k]={'coordinate':k,'owner':'southwest','current4KCandidate':{'file':t['currentCandidate'],'sha256':t.get('currentCandidateSha256'),'pixels':t.get('candidateVerification',{}).get('actualPixels')} if adopted else None,'fullCurrent4KCandidate':adopted,'selectedCoreSlots':[slot(s) for s in t['selectedIds']],'selectedCoreCount':t['selectedNativePatchCount'],'internalStatus':t['internalStatus'],'formalAccepted':False,'worldBox':t['coreWorldBox'],'sourceIndex':str(SW/'current-tiles.json'),'sourceManifest':t['nativeManifest'],'note':t['coverageState']}
    for t in read(EAST/'current-tiles.json'):
        k=t['tile']; cand=t.get('currentCandidate') or {}; adopted=bool(t['complete4kCandidate'])
        normalized[k]={'coordinate':k,'owner':t['zone'],'current4KCandidate':{'file':record_path(cand),'sha256':cand.get('sha256'),'pixels':cand.get('pixels')} if adopted else None,'fullCurrent4KCandidate':adopted,'selectedCoreSlots':[slot(x['id']) for x in t['selectedNativeEntries'] if x.get('exists')],'selectedCoreCount':t['existingSelectedCoreCount'],'internalStatus':t['internalStatus'],'formalAccepted':False,'worldBox':t['worldCoreBox'],'sourceIndex':str(EAST/'current-tiles.json'),'sourceManifest':t['nativeManifest'],'note':'Existing source dimensions and hashes verified; QA categories kept separate'}
    for r in range(1,17):
        for c in range(1,17):
            k=f'r{r:02}_c{c:02}'
            if k not in normalized:
                normalized[k]={'coordinate':k,'owner':owner(r,c),'current4KCandidate':None,'fullCurrent4KCandidate':False,'selectedCoreSlots':[],'selectedCoreCount':0,'internalStatus':'NO_SELECTED_SOURCE','formalAccepted':False,'worldBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],'sourceIndex':str(NW/'current-tiles.json') if r<=8 and c<=8 else str(EAST/'current-tiles.json'),'sourceManifest':None,'note':'No selected native core found in scoped census'}
    assert len(normalized)==256
    rows=[normalized[k] for k in sorted(normalized)]
    missing=[]
    for t in rows:
        slots=t['selectedCoreSlots']
        assert len(slots)==t['selectedCoreCount'],t['coordinate']
        assert len({tuple(s) for s in slots})==len(slots)
        for sr in range(1,5):
            for sc in range(1,5):
                if [sr,sc] not in slots:
                    x,y=t['worldBox'][:2]
                    missing.append({'coordinate':t['coordinate'],'owner':t['owner'],'subrow':sr,'subcolumn':sc,'worldCoreBox':[x+(sc-1)*1024,y+(sr-1)*1024,x+sc*1024,y+sr*1024]})
    per_zone={}
    for z in ['northwest','accelerated-yamen-north','northeast','southwest','southeast']:
        zz=[t for t in rows if t['owner']==z]
        per_zone[z]={'assignedCoordinates':len(zz),'current4KCandidates':sum(t['fullCurrent4KCandidate'] for t in zz),'fullSelectedCoreCoordinates':sum(t['selectedCoreCount']==16 for t in zz),'partialCoordinates':sum(0<t['selectedCoreCount']<16 for t in zz),'zeroSelectedCoreCoordinates':sum(t['selectedCoreCount']==0 for t in zz),'selectedCoreSlots':sum(t['selectedCoreCount'] for t in zz),'formalAcceptedCount':0}
    counts={'targetCoordinates':256,'current4KCandidates':sum(t['fullCurrent4KCandidate'] for t in rows),'coordinatesMissingCurrent4KCandidate':sum(not t['fullCurrent4KCandidate'] for t in rows),'fullSelectedCoreCoordinates':sum(t['selectedCoreCount']==16 for t in rows),'partialSourceCoordinates':sum(0<t['selectedCoreCount']<16 for t in rows),'zeroSelectedCoreCoordinates':sum(t['selectedCoreCount']==0 for t in rows),'selectedCoreSlots':sum(t['selectedCoreCount'] for t in rows),'missingCoreSlots':len(missing),'formalAcceptedCount':0}
    assert counts['selectedCoreSlots']+len(missing)==4096
    now=datetime.datetime.now(datetime.timezone.utc)
    meta={'capturedAtUTC':now.isoformat(),'capturedAtAmericaNewYork':now.astimezone(ZoneInfo('America/New_York')).isoformat(),'notLiveStatus':True,'coordinateBasis':'65536x65536 artwork pixels, half-open boxes, tile4096, subcore1024; not client world units','deduplication':'Four yamen acceleration coordinates counted once under accelerated-yamen-north; remaining northwest ownership60','counts':counts,'perOwner':per_zone,'wholeMapComplete':False,'sourceModelMetadata':'Historical unknown/returned-null stays unknown; no relabeling as GPT Image 2.5. Latest project policy permits existing builtin 2.0 fallback.','sourceDisclosure':'Selected slots may point to native-pixel derived repair composites. Full4K candidates are assembled composites, not single image-generation outputs.','sourceIndexes':[str(NW/'current-tiles.json'),str(SW/'current-tiles.json'),str(EAST/'current-tiles.json')]}
    save(OUT/'coverage-summary.json',meta)
    save(OUT/'current-256-coordinate-index.json',{'metadata':meta,'coordinates':rows})
    save(OUT/'missing-current-4k-coordinates.json',{'count':counts['coordinatesMissingCurrent4KCandidate'],'coordinates':[t['coordinate'] for t in rows if not t['fullCurrent4KCandidate']]})
    save(OUT/'missing-native-core-slots.json',{'count':len(missing),'coordinateBasis':meta['coordinateBasis'],'slots':missing})
    borders=[]
    pairs=[(f'r08_c{c:02}',f'r09_c{c:02}','y') for c in range(1,17)]+[(f'r{r:02}_c08',f'r{r:02}_c09','x') for r in range(1,17)]
    for a,b,axis in pairs:
        aa,bb=normalized[a],normalized[b]
        segments=[]
        for s in range(1,5):
            sa=[4,s] if axis=='y' else [s,4]; sb=[1,s] if axis=='y' else [s,1]
            segments.append({'segment':s,'leftOrNorthSelectedCoreAvailable':sa in aa['selectedCoreSlots'],'rightOrSouthSelectedCoreAvailable':sb in bb['selectedCoreSlots']})
        both=aa['fullCurrent4KCandidate'] and bb['fullCurrent4KCandidate']
        borders.append({'leftOrNorth':a,'rightOrSouth':b,'axis':axis,'bothCurrentFullCandidatesAvailable':both,'segments':segments,'status':'PENDING_ACTUAL_REVIEW' if both else 'NEIGHBOR_SOURCE_MISSING; NOT_A_SEAM_PASS','formalAccepted':False})
    save(OUT/'four-zone-boundary-availability.json',{'edgeCount':32,'pairedFullCandidateEdges':sum(x['bothCurrentFullCandidatesAvailable'] for x in borders),'edges':borders,'centralJunction':{'worldXY':[32768,32768],'coordinates':['r08_c08','r08_c09','r09_c08','r09_c09'],'availableFullCandidates':[k for k in ['r08_c08','r08_c09','r09_c08','r09_c09'] if normalized[k]['fullCurrent4KCandidate']],'status':'NEIGHBOR_SOURCE_MISSING'}})
    print(json.dumps(meta,ensure_ascii=False))

if __name__=='__main__': build()
