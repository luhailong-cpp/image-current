"""Record the reviewed step-foot fix and exact impact on the current candidates."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; QA=ROOT/'qa'
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):
    with Image.open(p) as im: return np.array(im)
manifest=load(QA/'connected-stepfoot-v01-manifest.json')
tiles=[]
for tile in ['r10_c03','r10_c04']:
    oldp='connected-final-v01-'+tile; newp='connected-stepfoot-v01-'+tile
    old=image(QA/(oldp+'-candidate-4096.png')); new=image(QA/(newp+'-candidate-4096.png'))
    selected=image(QA/(newp+'-repair-selection-mask.png'))==255
    report=load(QA/(newp+'-report.json'))
    prev=load(QA/(oldp+'-report.json')); oldids=image(QA/(oldp+'-source-id-mask.png'))
    finial=np.isin(oldids,[s['sourceId'] for s in prev['inputs'] if s['stem'].startswith('r10_c03_c04_finial_')])
    changed=np.any(old!=new,axis=2)
    yy,xx=np.where(selected)
    record={'tile':tile,'candidatePrefix':newp,'candidateSha256':sha(QA/(newp+'-candidate-4096.png')),
        'selectedPixels':int(selected.sum()),'changedPixels':int(changed.sum()),
        'changedOutsideSelectionPixels':int(np.count_nonzero(changed & ~selected)),
        'selectionGlobalBounds':[int(xx.min())+prev['candidateGlobalBox'][0],int(yy.min())+36864,int(xx.max())+1+prev['candidateGlobalBox'][0],int(yy.max())+1+36864],
        'previousFinialBackgroundSourcePixelsReplaced':int(np.count_nonzero(selected & finial)),
        'anyPixelsChangedAtOrBelowGlobalY37430':int(np.count_nonzero(changed[37430-36864:])),
        'fullSourcePixelValidation':report['validation']}
    assert record['changedOutsideSelectionPixels']==0 and record['anyPixelsChangedAtOrBelowGlobalY37430']==0
    tiles.append(record)
hash_checks=[]
for n in [1,2,3,6,7,8]:
    a=QA/f'connected-group-v01-horizontal-{n}-native100.png'
    b=QA/f'connected-stepfoot-group-v01-horizontal-{n}-native100.png'
    equal=sha(a)==sha(b); assert equal
    hash_checks.append({'horizontalView':n,'pngHashesEqual':equal,'sha256':sha(b)})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_court','formalAccepted':False,
    'originalGroup':'connected-group-v01','originalGroupStatus':'four-way junction rejected for detached diagonal brick joint near [12245,37190,12310,37250]',
    'horizontalViewsOriginal1to8':'All eight viewed at native scale; leaf, rope, wood frame, stone steps, red paper, paving and wood furniture geometry continuous. Mild natural wood/stone brush variation accepted.',
    'repairStatus':'passed_local_composite_visual_qa',
    'resolvedGroup':'connected-stepfoot-group-v01',
    'spec':'connected-stepfoot-v01-spec.json',
    'repairSource':'r09_r10_c04_steps_join_v01','repairSourceWasReused':True,
    'repairROI':[[0,800,500,1150]],'band':40,'mandatoryTarget':[[50,890,280,1040]],
    'sharedSelectionMaskSha256':manifest['sharedSelectionMask']['sha256'],
    'newViewsReviewed':['connected-stepfoot-v01-roi1-top-base-first-candidate-second-100pct.png','connected-stepfoot-v01-roi1-bottom-base-first-candidate-second-100pct.png','connected-stepfoot-v01-roi1-left-base-first-candidate-second-100pct.png','connected-stepfoot-v01-roi1-right-base-first-candidate-second-100pct.png','connected-stepfoot-group-v01-four-way-junction-native100.png','connected-stepfoot-group-v01-horizontal-4-native100.png','connected-stepfoot-group-v01-horizontal-5-native100.png','connected-stepfoot-group-v01-vertical-5-native100.png'],
    'visualFindings':['Detached diagonal old brick-joint fragment is fully removed by selecting the continuous native AI step tread and paving geometry.','All four new selection perimeters are continuous; no detached contour, sharp geometry shift or new rectangular patch found.','The new four-way junction and affected horizontal views 4/5 pass. The other six horizontal views are byte-identical to those already reviewed.','The small overlap with upper-finial source replaces background paving only; selection ends before global y37430, while the viewed gold ball and finial are lower and remain byte-identical.'],
    'unchangedHorizontalViews':hash_checks,'tiles':tiles,
    'scopeLimit':'This review covers the current four-tile group horizontal seam and repaired junction only. The complete 49-tile zone and external group perimeter remain unfinished.'}
fp=QA/'connected-group-v01-horizontal-review.json'
fp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(fp),'repairStatus':out['repairStatus'],'tiles':[{k:v for k,v in t.items() if k!='fullSourcePixelValidation'} for t in tiles]},ensure_ascii=True))
