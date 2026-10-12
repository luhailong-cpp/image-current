"""Finalize review metadata and prepare a scoped image cleanup plan; does not delete."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
manifest=read(ROOT/'manifest.json')
assert manifest['availableFrames']==68 and manifest['technicalStatus']=='passed'
selected={f['source']['generationRecord'] if isinstance(f.get('source'),dict) and 'generationRecord' in f['source'] else f.get('generationRecord',''): f for f in manifest['frames']}
# Resolve using the unambiguous per-runtime derivation records.
selected={read(ROOT/(f['file']+'.generation.json'))['derivedFrom']['generationRecord']: f for f in manifest['frames']}
source_map={}
records=[]
for path in (ROOT/'records').glob('*.json'):
    d=read(path)
    if not isinstance(d,dict) or not str(d.get('file','')).startswith('source/'): continue
    src=(ROOT/d['file']).resolve()
    assert src.is_relative_to(ROOT)
    assert src.exists() and sha(src)==d['sha256']
    records.append((path,d,src))
    source_map[str(src).lower()]={'sha256':d['sha256'],'generationRecord':path.relative_to(ROOT).as_posix(),'runtime':selected.get(path.relative_to(ROOT).as_posix(),{}).get('file')}
for path,d,src in records:
    key=path.relative_to(ROOT).as_posix()
    if key in selected:
        d['selected']=True
        d['visualStatus']='passed'
        d['visualReviewScope']='All 68 individual frames/contact sheets inspected; browser normal and 0.25 playback sampled; see qa/final-review.json for motion observations.'
        d['currentRuntimeFile']=selected[key]['file']
        d['event']='hit_contact' if d['action']=='hit' and d['frame']==2 else 'attack_strike' if d['action']=='attack' and d['frame']==7 else 'cast_release' if d['action']=='cast' and d['frame']==11 else None
    audits=[]
    for ref in d.get('references',[]):
        val=ref.get('path',''); rp=Path(val)
        rp=(ROOT/rp).resolve() if not rp.is_absolute() else rp.resolve()
        s=source_map.get(str(rp).lower())
        audits.append({'originalPath':val,'historicalInput':True,'sha256':s['sha256'] if s else sha(rp) if rp.is_file() else None,'generationRecord':s['generationRecord'] if s else None,'retainedRuntimeEquivalent':s['runtime'] if s else None,'plannedRemoval':bool(s and rp.name not in ('design-E.png','design-W.png'))})
    d['referenceRetentionAudit']=audits
    write(path,d)
review={
 'reviewedAt':stamp,'staticFrameCount':68,'staticStatus':'reviewed',
 'motionStatus':'browser-playback-reviewed-with-observations',
 'scope':'逐帧与六组总览覆盖68图；在内置浏览器实际运行全部六组1x和0.25x播放，以实时截图采样与逐帧控制核对动作，未作屏幕刷新精度测量或客户端验收。',
 'reviewedRuntimeSha256':{f['id']:f['sha256'] for f in manifest['frames']},
 'groups':[{'action':a,'direction':d,'normalPlaybackRun':True,'slowPlaybackRun':True,'individualFramesReviewed':True} for a in ('hit','attack','cast') for d in ('E','W')],
 'findings':[
   '两向保留白羽红冠幼鹤、金环、青绿金边领巾、两翼两足一尾和单云垫；W独立后视，无胸坠误挂背部。',
   '受击有压缩与颈部反冲，普攻有啄击前伸和回收，施法有抬翼蓄能、前送小云气及收翼。全帧独立AI绘制，无镜像、插值、复制或整体平移补帧。',
   '受击W01/02原先约19像素的导出云底跳动已通过AI重绘降至约4.4像素。施法两向足云较稳定。',
   '普攻峰值仍有云垫轻微起伏及轮廓变化；E06–08头身透视变化、E受击04到05回正较快。本次保留各帧原生姿态，不逐帧对脚掩盖变化。',
   '浏览器已预解码全部68帧；正常及慢速模式可运行，逐帧滑块会暂停播放。播放器截图为采样，不宣称视频级高刷新率测量通过。'
 ],
 'clientIntegration':'not-performed'
}
write(ROOT/'qa/final-review.json',review)
plan=[]
for path,d,src in records:
    if d.get('kind')=='design': continue
    plan.append({'file':src.relative_to(ROOT).as_posix(),'sha256':d['sha256'],'generationRecord':path.relative_to(ROOT).as_posix(),'reason':'selected native exported to verified runtime' if path.relative_to(ROOT).as_posix() in selected else 'unselected/rejected native candidate'})
for src in (ROOT/'qa').glob('*.png'):
    plan.append({'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'reason':'intermediate QA raster replaced by final preview contact sheets'})
write(ROOT/'cleanup-plan.json',{'createdAt':stamp,'root':str(ROOT),'files':plan,'retainedImages':'68 runtime PNG, 2 current direction design PNG, 6 final contact sheets','externalOriginals':'Host-managed image_gen caches outside task write boundary are not modified; original Image identity/style references retained.'})
print(json.dumps({'selected':len(selected),'successfulOutputs':len(records),'cleanupCandidates':len(plan)},ensure_ascii=False))
