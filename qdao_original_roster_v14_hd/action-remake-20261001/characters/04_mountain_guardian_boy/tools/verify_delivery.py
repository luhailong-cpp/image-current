"""Read-only checks of this character's final frames, records and review media."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib, json
from timing_profile import RUN_FRAME_MS, RUN_CYCLE_MS, RUN_NORMAL_DURATIONS
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    manifest=read(ROOT/'manifest.delivery.json')
    review=read(ROOT/'review.json')
    # Both the initial delivery and follow-up finalizer use this path/SHA binding.
    approval_binding=review.get('rootVisualApproval',{})
    if not isinstance(approval_binding,dict): raise ValueError('review.rootVisualApproval must contain path and sha256')
    approval_name=approval_binding.get('path')
    if not isinstance(approval_name,str) or not approval_name: raise ValueError('Missing current root visual approval path')
    approval_relative=Path(approval_name)
    approval_path=(ROOT/approval_relative).resolve()
    if approval_relative.is_absolute() or '..' in approval_relative.parts or not approval_path.is_relative_to(ROOT/'provenance'/'audit'):
        raise ValueError('Current root visual approval must stay in this character audit directory')
    if sha(approval_path)!=approval_binding.get('sha256'): raise ValueError('Current root visual approval SHA mismatch')
    approval=read(approval_path)
    if approval.get('character')!=ROOT.name: raise ValueError('Current root visual approval character mismatch')
    approved={x['file']:x['sha256'] for x in approval['entries'] if x.get('status')=='visual_passed'}
    errors=[]; count=0; media=0
    timing=read(ROOT/'runtime_timing.json')
    run=timing['run']
    if (RUN_FRAME_MS!=60 or RUN_CYCLE_MS!=960 or run['frameMs']!=RUN_FRAME_MS
            or run['offlineDefaultLoopMs']!=RUN_CYCLE_MS
            or run['offlineFrameDurationsMs']!=RUN_NORMAL_DURATIONS
            or run['previewFrameDurationsMs']!=RUN_NORMAL_DURATIONS):
        errors.append('Current runtime must be uniform60ms/960ms')
    for direction,segments in run['groundContactSegments'].items():
        if len(segments)!=8 or any(x['durationMs']!=120 for x in segments):
            errors.append(direction+': expected eight120ms support-position pairs')
    ms={'run':60,'hit':40,'attack':30,'cast':45}
    technical=read(ROOT/'manifest.technical.json')
    technical_rows={f['path']:f for s in technical['sequences'] for f in s['frames']}
    for s in technical['sequences']:
        if s['frame_ms']!=ms[s['action']] or s['duration_ms']!=s['target_count']*ms[s['action']]:
            errors.append(s['action']+'/'+s['direction']+': technical duration mismatch')
    for row in manifest['files']:
        p=ROOT/row['path']; j=ROOT/row['record']; data=read(j)
        if sha(p)!=row['sha256'] or data['sha256']!=row['sha256']: errors.append(row['path']+': PNG SHA mismatch')
        if sha(j)!=row['recordSha256']: errors.append(row['record']+': record SHA mismatch')
        if data['frameDurationMs']!=ms[data['action']]: errors.append(row['path']+': sidecar timing mismatch')
        if technical_rows.get(row['path'],{}).get('sha256')!=row['sha256']: errors.append(row['path']+': technical inventory stale')
        if technical_rows.get(row['path'],{}).get('source',{}).get('record_sha256')!=row['recordSha256']:
            errors.append(row['path']+': technical sidecar SHA stale')
        if data['action']=='run' and (data['runTiming']['offlinePreviewFrameMs']!=60
                or data['runTiming']['offlinePreviewDefaultLoopMs']!=960
                or data['runTiming']['offlinePreviewFrameDurationsMs']!=RUN_NORMAL_DURATIONS):
            errors.append(row['path']+': runTiming stale')
        visual=data.get('review',{})
        if (approved.get(row['path'])!=row['sha256'] or visual.get('status')!='visual_passed'
                or visual.get('sourceBoundSha256')!=row['sha256']
                or visual.get('approvalRecord')!=approval_name
                or visual.get('approvalSha256')!=approval_binding['sha256']
                or visual.get('automaticallyApproved') is not False): errors.append(row['path']+': current visual binding mismatch')
        with Image.open(p) as im:
            if im.size!=(1024,1024) or im.mode!='RGBA': errors.append(row['path']+': formal format mismatch')
        if data.get('actualModel') is not None or data.get('actualQuality') is not None: errors.append(row['path']+': unconfirmed model changed')
        count+=1
    expected={f'frames/{a}/{d}/frame_{n:02}.png' for a,dirs,num in [('run',['N','NE','E','SE','S','SW','W','NW'],16),('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16)] for d in dirs for n in range(1,num+1)}
    actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'frames').rglob('*.png')}
    if expected!=actual or count!=196: errors.append('196 expected paths mismatch')
    for j in (ROOT/'preview').glob('*.generation.json'):
        data=read(j); p=ROOT/data['file']
        if not p.is_file() or sha(p)!=data['sha256']: errors.append(str(j.name)+': preview SHA mismatch')
        for source in data.get('derivedFrom',[]):
            if sha(ROOT/source['path'])!=source['sha256']: errors.append(str(j.name)+': stale frame '+source['path'])
        if p.suffix.lower() in ('.gif','.apng'):
            with Image.open(p) as im:
                durations=[]
                for n in range(im.n_frames):
                    im.seek(n); durations.append(im.info.get('duration'))
            wanted=data['operation']['durationsMs']
            if durations!=wanted: errors.append(p.name+': encoded GIF/APNG frame duration mismatch')
            if p.suffix.lower()=='.apng':
                expected_ms=60 if p.stem.endswith('_normal') else 240
                if durations!=[expected_ms]*16: errors.append(p.name+': stale run APNG timing')
        media+=1
    if media!=42: errors.append('Expected42 derived preview assets')
    wanted_hashes={row['path']:row['sha256'] for row in manifest['files']}
    actual_hashes={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (ROOT/'frames.sha256').read_text(encoding='utf-8').splitlines()}
    if actual_hashes!=wanted_hashes: errors.append('frames.sha256 is stale')
    remaining=[str(p.relative_to(ROOT)) for ext in ('*.png','*.gif','*.jpg') for p in (ROOT/'provenance').rglob(ext)]
    if remaining: errors.append('provenance images remain after retention cleanup')
    report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'formalFrames':count,'previewAssets':media,'rootVisualApproval':approval_binding,'errors':errors,'remainingProvenanceImages':remaining,'scope':'Current formal/export/approval/source/GIF-APNG encoded frame-duration consistency only; not automated aesthetic approval.','clientIntegration':'not_integrated'}
    (ROOT/'provenance/audit/final_delivery_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    raise SystemExit(1 if errors else 0)
if __name__=='__main__': main()
