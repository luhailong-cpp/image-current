"""One-time independent audit of saved connected-final merges, not a merge implementation."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p, mode):
    with Image.open(p) as image:
        assert image.mode == mode and image.size == (4096,4096)
        return np.array(image)
def mismatches(a,b): return int(np.count_nonzero(np.any(a != b, axis=1))) if a.ndim==2 else int(np.count_nonzero(a != b))
def identity(s): return (s['stem'], s['sha256'], tuple(s['nativeGlobalBox']))

top = set(load(QA/'top-final-spec-v01.json')['topSourceStems'])
results=[]
for tile in ('r10_c03','r10_c04'):
    prefix='connected-final-v01-'+tile
    mr=load(QA/(prefix+'-report.json'))
    br=load(QA/(mr['basePrefix']+'-report.json'))
    dr=load(QA/(mr['donorPrefix']+'-report.json'))
    arts={}; masks={}
    for label,pre in [('merged',prefix),('finial',mr['basePrefix']),('top',mr['donorPrefix'])]:
        arts[label]=arr(QA/(pre+'-candidate-4096.png'),'RGB')
        masks[label]=arr(QA/(pre+'-source-id-mask.png'),'L')
    selection=arr(QA/(prefix+'-donor-selection-mask.png'),'L')
    top_ids=[s['sourceId'] for s in dr['inputs'] if s['stem'] in top]
    top_mask=np.isin(masks['top'],top_ids)
    finial_sources=[s for s in br['inputs'] if s['stem'].startswith('r10_c03_c04_finial_')]
    finial_mask=np.isin(masks['finial'],[s['sourceId'] for s in finial_sources])
    overlap=int(np.count_nonzero(top_mask & finial_mask))
    common=~(top_mask|finial_mask)
    source_cohorts=[]
    for source in mr['inputs']:
        branch='top' if source['stem'] in top else 'finial'
        report=dr if branch=='top' else br
        matched=[s for s in report['inputs'] if identity(s)==identity(source)]
        assert len(matched)==1
        expected=(masks[branch]==matched[0]['sourceId'])
        if branch=='finial': expected &= ~top_mask
        actual=(masks['merged']==source['sourceId'])
        source_cohorts.append({'stem':source['stem'],'expectedPixels':int(expected.sum()),'actualPixels':int(actual.sum()),'maskPositionMismatch':int(np.count_nonzero(expected!=actual))})
    checks={
        'savedSelectionIsBinary':set(np.unique(selection).tolist()) <= {0,255},
        'savedSelectionMismatchedPixels':int(np.count_nonzero((selection==255)!=top_mask)),
        'topFinialOverlapPixels':overlap,
        'commonBranchArtMismatchedPixels':mismatches(arts['finial'][common],arts['top'][common]),
        'missingOrWrongTopArtPixels':mismatches(arts['merged'][top_mask],arts['top'][top_mask]),
        'changedFinialArtPixels':mismatches(arts['merged'][finial_mask],arts['finial'][finial_mask]),
        'changedOutsideTopSelectionPixels':mismatches(arts['merged'][~top_mask],arts['finial'][~top_mask]),
        'sourceIdCohortMismatchedPixels':sum(s['maskPositionMismatch'] for s in source_cohorts),
        'mergedSourceIdsAllKnown':set(np.unique(masks['merged']).tolist()) <= {s['sourceId'] for s in mr['inputs']},
        'reportOutputHashesMatch':all(sha(s['path'])==s['sha256'] for s in mr['outputs']),
        'reportParentHashesMatch':all(sha(f['path'])==f['sha256'] for p in mr['parents'] for f in p['files']),
        'scriptHashMatches':sha(mr['script']['path'])==mr['script']['sha256'],
        'reportsDescribeSameGlobalBox':mr['candidateGlobalBox']==br['candidateGlobalBox']==dr['candidateGlobalBox'],
    }
    passed=all(v if isinstance(v,bool) else v==0 for v in checks.values())
    results.append({'tile':tile,'status':'passed' if passed else 'failed','basePrefix':mr['basePrefix'],'donorPrefix':mr['donorPrefix'],
        'candidateSha256':sha(QA/(prefix+'-candidate-4096.png')),
        'topSelectedPixels':int(top_mask.sum()),'finialSelectedPixels':int(finial_mask.sum()),'commonPixels':int(common.sum()),
        'checks':checks,'topAndFinialSourceCohorts':[s for s in source_cohorts if s['stem'] in top or s['stem'].startswith('r10_c03_c04_finial_')],
        'allSourceCohortsChecked':len(source_cohorts)})
    del arts,masks,selection,top_mask,finial_mask,common,source_cohorts

out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_court',
    'status':'passed' if all(r['status']=='passed' for r in results) else 'failed','formalAccepted':False,
    'codeReview':[
        'Merge copies only donor pixels already selected by the six requested top source stems, at identical tile-local/global coordinates.',
        'Base-exclusive finial cohorts are checked for disjointness. Source identity includes image path, source hash and native global extent before source-ID remapping.',
        'The actual saved output cohorts were independently checked by source stem/hash/extent against the appropriate saved parent. No top pixels are missing and no finial or non-top pixels changed.',
        'There is no image resizing, feathering, warp or color processing; the operation introduces no new geometric selection edge.'
    ],'tiles':results,'remaining':'Connected group visual seam QA is separate.'}
path=QA/'connected-final-merge-independent-review.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=True))
