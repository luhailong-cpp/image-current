from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path.cwd();p='central-partial-r11c04-rows12-resume-v01'
report=json.loads((R/'qa'/f'{p}-report.json').read_text(encoding='utf-8'))
def meta(path):
    path=Path(path);return {'path':path.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
out={
'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
'reviewer':'WEST independent visual review',
'candidate':meta(report['art']),
'scope':'Only r11_c04 first two rows, all 10 provided native100 seam panels; no old full-area QA repeated.',
'candidateGlobalBox':report['candidateGlobalBox'],
'reviewScale':'1:1',
'reviewedViews':[meta(v) for v in report['views']],
'additionalSubstantiveFindings':[],
'knownFindingExcludedFromNewFindings':{'globalBox':[15575,42099,15675,42429],'description':'Previously reported s02_04 gold fascia step. Root owns repair. This review does not accept the old candidate with that defect and does not review a later replacement.'},
'panelResults':[
{'view':'h1024-c1','status':'no additional geometry defect','note':'Blue roof-tile arc joins and highlights continuous.'},
{'view':'h1024-c2','status':'no additional geometry defect','note':'Diagonal red/gold ridge line and blue tile profiles continuous.'},
{'view':'h1024-c3','status':'no additional geometry defect','note':'Gold scroll outline and adjacent roof tube contours continuous.'},
{'view':'h1024-c4','status':'known defect remains','note':'Gold eave step is the already reported s02_04 issue; no second independent defect identified.'},
{'view':'v1024-r1','status':'no additional geometry defect','note':'Diagonal ridge contours and crossing tile seams meet without a gap.'},
{'view':'v1024-r2','status':'no additional geometry defect','note':'Tile lower ends and fascia meet continuously.'},
{'view':'v2048-r1','status':'no additional geometry defect','note':'Roof tube arcs and highlights continuous.'},
{'view':'v2048-r2','status':'no additional geometry defect','note':'Gold scroll, bracket, blue tile end and timber support coherent; targeted same-coordinate source comparison below.'},
{'view':'v3072-r1','status':'no additional geometry defect','note':'Upper eave and roof tube outlines continuous.'},
{'view':'v3072-r2','status':'no additional geometry defect apart from adjacent known s02_04 step','note':'Lower blue end caps and wood members show no second broken contour.'}],
'suspectedGuideFragmentInvestigation':{
'globalBox':[14225,42730,14445,43008],
'comparisonManifest':meta(R/'qa'/f'{p}-west-compare.json'),
'comparedSources':['r11_c04_s02_02_v01','r11_c04_s02_03_v01'],
'result':'No blurry guide fragment confirmed. The small dark patch by the blue tile end and red support is present as coherent timber shading in both native sources; candidate retains crisp edges.',
'pixelReselectionRecommended':False,
'recommendedSourceAndRoi':None},
'acceptedDifferences':'Minor brush and texture differences without doubled contours or visible gaps.',
'overall':'No additional substantive seam defect beyond the known gold fascia issue; not a full-tile or external-perimeter acceptance.',
'networkCalls':0,'artworkOrSourceSelectionChanged':False}
dest=R/'qa'/f'{p}-west-review.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(dest),'viewCount':len(report['views']),'newFindings':0,'knownGoldEaveIssueStillRequiresRootRepair':True,'reselectionRecommended':False}))

