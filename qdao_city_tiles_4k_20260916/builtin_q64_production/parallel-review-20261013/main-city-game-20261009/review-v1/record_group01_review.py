from review_existing import *

d=read(GROUP/'manifest.json')
for e in d['crops']:
    assert sha(e['file'])==e['sha256']
    e['actuallyViewed']=True
    e['viewTool']='view_image detail=original; each image individually supplied at stored dimensions'
    e['verdict']='PASS_LOCAL_MAJOR_GEOMETRY'
    if e.get('north')=='r04_c05' and e.get('segment')==4:
        e['notes']='Current full south tile has continuous lion base / jade relief contours; the older disclosed green blurry band is not present at this seam crop.'
    elif e.get('junctionWorldXY')==[17408,16384]:
        e['notes']='Stone edge and joint continue. Minor pale facet tone variation near local x70..210,y250..265; no contour break; does not constitute complete texture uniformity approval.'
    elif 'junctionWorldXY' in e:
        e['notes']='Visible stair/stone/relief contours continuous across the two axes at this junction.'
    else:
        e['notes']='Visible stone step edges, joints and relief contours continue across local y160; no gap or duplicated architectural edge observed.'
d['reviewedAtUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
d['newReviewSummary']={'boundarySegmentsActuallyViewed':8,'subpatchBoundaryJunctionsActuallyViewed':6,'fourTileJunctionsActuallyViewed':1,'localPassCount':15,'newAIRepairRequiredByTheseCrops':0,'oldCropPixelIdenticalCount':2,'oldCropChangedCount':6,'scopeLimit':'Local visible boundary geometry at native scale. Does not certify outside neighbors or the entire map.'}
d['internalReviewReuse']=[
 {'coordinates':['r03_c04','r03_c05','r04_c04','r04_c05'],'evidence':str(ROOT/'accelerated-yamen-north/delivery-20261012-v1/delivery-manifest.json'),'basis':'Current delivery candidate hashes match selected full tiles; internal and assigned shared-boundary QA are recorded passed in this manifest and its linked final records.'},
 {'coordinates':['r05_c04','r05_c05'],'evidence':str(ROOT/'northwest/joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/delivery-summary.json'),'basis':'Current eleven-tile package selects exact slices of this reviewed joint assembly; existing internal and vertical shared-boundary evidence is reused, without reclassifying as formal map acceptance.'}
]
for x in d['internalReviewReuse']:
    x['sha256']=sha(x['evidence'])
d['assemblyAllowedAfterReview']=True
d['groupStatus']='local_internal_evidence_reused_and_current_acceleration_south_boundary_passed; eligible for native pixel mechanical assembly'
d['formalAccepted']=False
d['wholeMapComplete']=False
save(GROUP/'manifest.json',d)
print(json.dumps(d['newReviewSummary'],ensure_ascii=False))
