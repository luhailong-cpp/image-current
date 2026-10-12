from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
D=Path(__file__).resolve().parent;BASE=D.parent.parent
manifest=json.loads((D/'r12c08-wall-rock-rail-coordinated-v1.patch-manifest.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('native_source_helper',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
for rec in manifest['patches']:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
reports=[]
boxes={'p14-west':[31488,45056,32000,46080],
       'p14-north':[31744,44800,32768,45312],
       'p14-south':[31744,45824,32768,46336],
       'p14-east':[32512,45056,33024,46080],
       'wall-rock-four-core-cross':[32480,45792,33120,46432],
       'approved-rail-cross':[32384,45056,32896,45568]}
for ident,box in boxes.items():
    im,pieces,missing=sources.extract(box);assert not missing,missing
    path=D/('coordinated-v1-'+ident+'-native.png');assert not path.exists();im.save(path)
    reports.append({'id':ident,'globalBox':box,'file':str(path),'sha256':sha(path),'dimensions':list(im.size),
                    'sourcePieces':pieces,'resamplingApplied':False,'status':'pending_owner_independent_visual_review'})
baseproof=json.loads((D/'r12c08-wall-rock-conditioned-v2.coordinates-provenance.json').read_text(encoding='utf-8'))
unchanged=[{'file':r['file'],'expectedSha256':r['sha256'],'actualSha256':sha(r['file']),
            'unchanged':r['sha256']==sha(r['file'])} for r in baseproof['canonicalManifests']+[baseproof['historicalFreeze']]]
assert all(r['unchanged'] for r in unchanged)
audit={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
       'status':'geometry_candidate_with_material_finish_pending','preferredPatchManifest':str(D/'r12c08-wall-rock-rail-coordinated-v1.patch-manifest.json'),
       'preferredPatchManifestSha256':sha(D/'r12c08-wall-rock-rail-coordinated-v1.patch-manifest.json'),
       'preferredPreview':str(D/'r12c08-wall-rock-conditioned-v8-border-bounded-preview.png'),
       'generatedVersions':['v2','v3','v4','v5','v6','v7','v8'],
       'rejectedWholeCandidateVersions':['v2','v3','v4','v5'],
       'geometryPipeline':'v6 generated common-source wall/rock joint; v7 generated border strips; v8 generated only three small boundary plant corrections; approved rail-v4 replayed exactly into coordinated p14/p11.',
       'observedGeometry':{'G4':'Original large vertical course mismatch eliminated by same generated source across x32768; wall courses and coping face are connected.',
                           'G5':'Original rectangular rock notch at y46080 eliminated; foreground boulder outline is rounded and connects selected lower-rock core.',
                           'outerLeft':'Added truncated rosette removed in v8; stone faces/gaps connect to original left pixels without the previous leaf cliff.',
                           'outerTop':'Coping top-face and diagonal gaps connect; small crevice leaves have been matched to source context; material texture steps remain visible.',
                           'outerRight':'Coping/front-face course outlines are substantially continuous with native right context. Visible material boundary remains; final strict owner review required.',
                           'outerBottom':'Foreground boulder silhouette is continuous. Local rock/leaf material transition is still visible at the horizontal adoption edge.'},
       'materialRisks':['Visible tone/texture rectangles along outer right boundary worldx33100 and within v7 border transitions.',
                        'Local texture/color step near bottom worldy46080 and small foliage junctions needs close owner review.',
                        'No deterministic color correction was applied because this agent was restricted to mechanical native crops/guide composition; all altered art came from actual builtin generation.'],
       'worldAdoptionBoxes':{'wallRock':[32500,45530,33100,46080],'approvedRail':[32470,45066,32800,45491]},
       'canonicalCoreChangesRequired':['r12_c08/p14','r12_c09/p11'],
       'optionalHaloOnlyCandidates':['r12_c08/p24','r12_c09/p21'],
       'nativeEvidence':reports,'sourceSafetyVerification':unchanged,
       'allOriginalsAndFailedDraftsPreserved':True,'resamplingApplied':False,'syntheticGeometricRepairApplied':False,
       'paidApiUsed':False,'canonicalSelectionsModified':False,'zoneProgressModified':False,'historicalFreezeModified':False,
       'formalAccepted':False,'promotedToSelected':False,'usableForFinalAdoption':False,
       'nextRequiredWork':'Owner independently reviews geometry and completes bounded material finish before coordinated canonical adoption of both p14 and p11.'}
(D/'coordinated-v1-native-evidence-and-review.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'review':str(D/'coordinated-v1-native-evidence-and-review.json'),'evidence':[r['file'] for r in reports],'sourceHashesUnchanged':True}))
