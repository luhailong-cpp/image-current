"""Publish a frozen, reviewed selection without declaring overall acceptance."""
import argparse
from pathlib import Path
from PIL import Image
from revise_feet_20261003 import ROOT, read, save, sha, now, scoped
from rebuild_previews import build_artifacts
from build_preview import main as build_html

def publish(revision):
    rev = scoped(revision)
    selection = read(rev / 'selection.json')
    assert selection['staticReviewed'] is True
    chosen = selection['selected']
    m = read(ROOT / 'manifest.json')
    before = {f['id']: f for f in read(rev / 'before-manifest.json')['frames']}
    assert not (rev / 'replacement-ledger.json').exists(), 'Already published'
    assert m['timing']['runCycleMs'] == 960 and m['timing']['runFrameMs'] == 60
    assert set(chosen) <= set(before)
    assert all(sha(ROOT / f['path']) == before[f['id']]['sha256'] for f in m['frames'])
    external_updates = {}
    for key, rel in chosen.items():
        src = scoped(rel)
        nr = read(str(src) + '.generation.json')
        assert sha(src) == nr['sha256']
        with Image.open(src) as im:
            assert im.size == (1254,1254) and im.mode == 'RGBA' and im.getextrema()[3] == (0,255)
            a = im.getchannel('A')
            assert all(a.crop(b).getextrema()[1] <= 8 for b in ((0,0,1254,1),(0,1253,1254,1254),(0,0,1,1254),(1253,0,1254,1254)))
        for ri, ref in enumerate(nr['references']):
            ref_path = Path(ref['path']).resolve()
            observed = sha(ref_path) if ref_path.is_file() else None
            if observed == ref['sha256']: continue
            # Other character work can replace a reference after this native was
            # generated. Preserve its recorded digest rather than relabel it.
            assert not ref_path.is_relative_to(ROOT), (key, ref['path'])
            request_path = src.with_suffix('.request.json')
            request = read(request_path)
            submitted = {Path(p).resolve() for p in request['submittedParameters']['referenced_image_paths']}
            assert ref_path in submitted, (key, 'reference absent from actual request')
            frozen = next((r.get('sha256') for r in request.get('references',[]) if Path(r['path']).resolve()==ref_path), None)
            if frozen is not None: assert frozen == ref['sha256'], (key, 'frozen reference digest differs')
            external_updates[(key,ri)] = {'id':key,'path':ref['path'],'recordedSHA256':ref['sha256'],
                'observedCurrentSHA256':observed,'frozenRequestSHA256':frozen,'request':str(request_path),
                'digestEvidence':'matches pre-call request snapshot' if frozen else 'recorded at native receipt/export; request records path but no pre-call digest'}
        assert not (rev / 'superseded-records' / (key+'.json')).exists()
    replacements = []
    for f in m['frames']:
        if f['id'] in chosen:
            src = scoped(chosen[f['id']]); dst = scoped(f['path'])
            record_path = Path(str(src)+'.generation.json'); nr = read(record_path)
            for ri, ref in enumerate(nr['references']):
                if (f['id'],ri) in external_updates:
                    evidence = external_updates[(f['id'],ri)]
                    ref['historicalPath'] = ref.pop('path'); ref['historicalSource'] = True
                    ref['disposition'] = 'external reference changed after recorded generation evidence; original digest retained; external file untouched'
                    ref['digestEvidence'] = evidence['digestEvidence']
            archived = rev / 'superseded-records' / (f['id']+'.json')
            save(archived, read(ROOT / f['sourceRecord']))
            with Image.open(src) as im:
                im.resize((1024,1024), Image.Resampling.LANCZOS).save(dst)
            previous = {'historicalPath':str(dst),'sha256':before[f['id']]['sha256'],'historicalSource':True,'generationRecord':str(archived),'disposition':'previous final replaced after verified edit; text provenance retained'}
            nr['replacesFinal'] = previous
            first = nr['references'][0]
            nr['editSource'] = dict(previous) if Path(first['path']).resolve()==dst else {'path':first['path'],'sha256':first['sha256'],'generationRecord':first['path']+'.generation.json'}
            save(record_path,nr)
            replacement = {'id':f['id'],'path':f['path'],'previousSHA256':before[f['id']]['sha256'],'newSHA256':sha(dst),'source':src.relative_to(ROOT).as_posix(),'sourceSHA256':sha(src),'previousSourceRecord':archived.relative_to(ROOT).as_posix()}
            replacements.append(replacement)
            f.update({'sha256':sha(dst),'origin':'builtin_targeted_pose_edit'})
            f['nativeProvenance']={'historicalPath':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'width':1254,'height':1254,'mode':'RGBA','generationRecord':record_path.relative_to(ROOT).as_posix(),'disposition':'retained_until_cleanup','verifiedBeforeCleanup':False}
            save(ROOT / f['sourceRecord'],{'file':str(dst),'sha256':sha(dst),'width':1024,'height':1024,'mode':'RGBA','derivedFrom':{'path':str(src),'sha256':sha(src),'generationRecord':str(record_path),'dimensions':[1254,1254]},'operation':'uniform entire1254x1254 canvas resampled to1024x1024 Lanczos; no crop/translation/bboxfit/grounding','actualModel':None,'actualQuality':None,'status':'exported','visualApproved':False,'revision':replacement})
        f['visualApproved']=False
        f['visualReviewScope']='Current revision sequence review pending; run support positions under latest user instruction'
        rec=read(ROOT / f['sourceRecord']); rec['visualApproved']=False; save(ROOT / f['sourceRecord'],rec)
    m.update({'formalAccepted':False,'updatedAt':now(),'currentReview':{'status':'exported_sequence_and_run_grounding_review_pending','record':(rev/'selection.json').relative_to(ROOT).as_posix(),'replacedFrames':sorted(chosen),'client':'not_tested'}})
    save(ROOT/'manifest.json',m)
    save(rev/'replacement-ledger.json',{'at':now(),'replacements':replacements})
    save(rev/'publish-external-reference-history.json',{'at':now(),'entries':list(external_updates.values())})
    save(ROOT/'review/final-visual-review.json',{'reviewedAt':now(),'offlineAccepted':False,'scope':'Latest combat direction revision and run grounding review pending','pendingFrames':[f['id'] for f in m['frames']],'clientTested':False})
    save(ROOT/'preview/progress.json',{'frames':196,'offlineAccepted':0,'clientIntegrated':0})
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in m['frames']),encoding='utf-8')
    build_artifacts(m)
    assert build_html()==0
    print(f'Published {len(replacements)} reviewed native edits; final sequence acceptance pending.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('revision');publish(p.parse_args().revision)
