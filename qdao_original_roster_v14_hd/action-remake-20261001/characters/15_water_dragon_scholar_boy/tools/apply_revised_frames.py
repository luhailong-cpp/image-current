"""Export explicitly selected repair cels; preserve all other runtime pixels and source history.

Use --select run-SE-06=run-SE-06-archer-v2 --note 'actual static review' --write.
Only whole-canvas 1254 -> 940, fixed offset(42,49). No pose synthesis.
"""
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
import argparse, hashlib, io, json
from PIL import Image
from build_delivery import inspect, pixel_sha, render_main_preview
from render_review_board import load_run_timing, render_review_board
ROOT=Path(__file__).resolve().parents[1]
def sha(data): return hashlib.sha256(data).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def slot(r): return f"{r['action']}-{r['direction']}-{r['frame']:02d}"
def main():
    p=argparse.ArgumentParser();p.add_argument('--select',action='append',required=True);p.add_argument('--note',required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
    m=read(ROOT/'manifest.json');idx=read(ROOT/'sources-index.json');t=load_run_timing();now=datetime.now(timezone.utc).isoformat()
    byslot={r['slot']:r for r in m['frames']};index={slot(r):r for r in idx['frames']}
    # Validate every currently delivered image before changing one.
    for r in m['frames']:
        if sha((ROOT/r['output']).read_bytes())!=r['sha256']: raise ValueError('Current image changed: '+r['slot'])
    writes={};changes=[];selection_updates={};seen=set()
    for item in a.select:
        name,key=item.split('=',1)
        if name in seen or name not in byslot or '/' in key or '\\' in key or '..' in key: raise ValueError('Invalid selection')
        seen.add(name);r=byslot[name];before=deepcopy(r);source=f'sources/new/{key}.png';gp=f'provenance/generation/{key}.json'
        g=read(ROOT/gp);raw=(ROOT/source).read_bytes()
        if sha(raw)!=g['sha256']: raise ValueError('Generation/source SHA mismatch')
        if g['width']!=1254 or g['height']!=1254: raise ValueError('Expected preserved native1254 canvas')
        if any(x['slot']!=name and x['derivedFrom']['sha256']==g['sha256'] for x in m['frames']): raise ValueError('Source already selected elsewhere')
        im,geo=inspect(ROOT/source);im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v));resized=im.resize((940,940),Image.Resampling.LANCZOS)
        out=Image.new('RGBA',(1024,1024));out.alpha_composite(resized,(42,49));buf=io.BytesIO();out.save(buf,format='PNG');png=buf.getvalue();vsha=pixel_sha(out)
        im.close();resized.close();out.close()
        if any(x['slot']!=name and x['sha256']==sha(png) for x in m['frames']): raise ValueError('Duplicate runtime')
        review={'reviewer':'root','reviewedAt':now,'notes':a.note,'scope':'static_selected_pending_complete_sequence_review'}
        origin={'path':source,'sha256':g['sha256'],'generationRecord':gp,'generationRecordSha256':sha((ROOT/gp).read_bytes())}
        d=read(ROOT/r['derivedRecord']);d.update(sha256=sha(png),derivedAt=now,derivedFrom=origin,sourceKind='new',originalGenerationRecord=g,nativeGeometry=geo,visualReview=review,animationApproval='pending_archer_reference_review',userAcceptance='not_reviewed_after_repair',supersedes={'outputSha256':before['sha256'],'derivedFrom':before['derivedFrom']})
        d.pop('offlineReview',None)
        r.update(source=source,sha256=sha(png),derivedFrom=origin,sourceKind='new',visiblePixelSha256=vsha,review=review,visualApproval='accepted_by_selection',animationApproval='pending_archer_reference_review')
        r.pop('offlineReview',None)
        if r['action']=='run': r.update(durationMs=60,timingStatus='user_requested_not_client');d.update(durationMs=60,timingStatus='user_requested_not_client')
        index[name].update(source=source,sha256=g['sha256'],generationRecord=gp,review=review,accepted=True,nativeSingleFrame=True,supersedes=before['derivedFrom'])
        selection_updates[name]=deepcopy(index[name]);writes[ROOT/r['output']]=png;writes[ROOT/r['derivedRecord']]=enc(d)
        changes.append({'slot':name,'source':source,'generationRecord':gp,'sourceSha256':g['sha256'],'outputSha256':sha(png),'previous':before,'review':review})
    # Keep the authoritative group selection files in sync, without rebuilding old sources.
    for selection in (ROOT/'audit').glob('*selection.json'):
        data=read(selection)
        if not isinstance(data,dict) or not isinstance(data.get('frames'),list): continue
        changed=False
        for i,row in enumerate(data['frames']):
            if not all(k in row for k in ('action','direction','frame')): continue
            name=slot(row)
            if name in selection_updates: data['frames'][i]=selection_updates[name];changed=True
        if changed: writes[selection]=enc(data)
    idx_bytes=enc(idx);m['selectionSha256']=sha(idx_bytes);m.update(builtAt=now,animationApproval='pending_archer_reference_review',userAcceptance='not_reviewed_after_repair')
    m.pop('offlineReview',None)
    writes[ROOT/'sources-index.json']=idx_bytes;writes[ROOT/'manifest.json']=enc(m)
    writes[ROOT/'preview/index.html']=render_main_preview(m,t).encode('utf-8');writes[ROOT/'preview/all-directions.html']=render_review_board(m,t).encode('utf-8')
    stamp=now.replace(':','-').replace('.','-');audit=ROOT/'audit/archer-reference'/f'export-{stamp}.json'
    writes[audit]=enc({'at':now,'changes':changes,'unchangedRuntimeCount':196-len(changes),'operation':'fixed whole-canvas export only; unchanged frames untouched'})
    if a.write:
        for path,data in writes.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps({'written':a.write,'replaced':list(seen),'unchangedRuntimeCount':196-len(changes)}))
if __name__=='__main__':main()
