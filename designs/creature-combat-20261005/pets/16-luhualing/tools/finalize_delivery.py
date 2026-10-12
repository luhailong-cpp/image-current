"""Record completed local review and the authorized, task-local image cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()

if sys.argv[1] == 'prepare':
    manifest = read(ROOT/'manifest.json')
    technical = read(ROOT/'validation.json')
    provenance = read(ROOT/'provenance-validation.json')
    assert technical['technicalStatus']=='passed' and technical['presentFrames']==68
    assert provenance['status']=='passed' and provenance['auditedFrameCount']==68
    notes = {
        'hit/E': '受力后仰、峰值与回稳已逐帧看；双手各持原本道具，保持斜前朝右下。',
        'hit/W': '真实斜后视，受力与回稳已看；保留后脑发辫、后腰和鞋跟，非镜像。',
        'attack/E': 'E02持物换手及E05–08过量特效已修复，E07–08释放沿右下方向衔接。',
        'attack/W': '斜后朝左上独立姿态，挥枝释放、回收和收势已看，壶保持屏右。',
        'cast/E': '聚露、释放和回收已看；E10–11露流修短为稀疏露滴，修复画布右侧裁边。',
        'cast/W': 'W02/04/05持壶换侧和W03/04桂枝跨身已修复，枝保持左肩外；W11裁边露流已修复。'
    }
    review = {
        'reviewedAt': now, 'reviewer':'Codex local visual review',
        'status':'passed_local_review', 'dynamicStatus':'passed_local_preview',
        'clientStatus':'not_integrated',
        'method': '逐张查看生成/修复结果，并查看最终六张完整联系表；在本地浏览器实际播放六组正常1×与0.25×慢放，以页面帧计数和截图抽样观察；逐帧控制检查受击03、普攻07、施法11，以及末帧→首帧。此为本地素材审查，未录制完整连续视频，未进行客户端验收。',
        'scope': '身份、E/W视角、道具归属、肢体、受击/释放/回收阶段、透明背景、明显裁边和已发现衔接问题。预览循环用于反复查看，动作本身为单次动作而非移动循环。',
        'groups': [], 'frames': {}
    }
    for g in manifest['groups']:
        key=g['action']+'/'+g['direction']
        review['groups'].append({'action':g['action'],'direction':g['direction'],'frameCount':len(g['files']),'normalPlayback':'reviewed','quarterSpeedPlayback':'reviewed','peakFrameStepping':'reviewed','lastToFirstStepping':'reviewed','note':notes[key]})
    for frame in manifest['frames']:
        p=ROOT/frame['file']
        assert sha(p)==frame['sha256']
        review['frames'][frame['file']]={'sha256':sha(p),'status':'passed_local_review','note':notes[frame['action']+'/'+frame['direction']]}
    write(ROOT/'visual-review.json',review)
    candidates = sorted(p for p in (ROOT/'.work').rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'})
    candidates += [ROOT/'records/attack/review-E.jpg',ROOT/'records/attack/review-W.jpg']
    items=[]
    for p in candidates:
        p=p.resolve(); assert p.is_relative_to(ROOT) and p.is_file()
        items.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'已完成正式导出的原生/拒稿图片' if p.is_relative_to(ROOT/'.work') else '已被最终preview联系表取代的临时审图','status':'planned'})
    assert len(items)==72, f'Unexpected cleanup candidates: {len(items)}'
    write(ROOT/'cleanup.json',{'preparedAt':now,'status':'prepared','policy':'根AGENTS.md 2026-09-23素材保留规则；仅清理本角色目录图片。保留正式runtime、最终preview、prompt、模型/质量/时间/来源和拒稿文字记录。','preCleanupTechnical':'passed 68/68','preCleanupProvenance':'passed 68/68','outsideTaskFiles':'not modified','files':items})
    print(json.dumps({'reviewFrames':len(review['frames']),'cleanupCandidates':len(items),'preCleanupProvenance':provenance['status']}))
elif sys.argv[1] == 'complete':
    cleanup=read(ROOT/'cleanup.json')
    assert all(not (ROOT/item['file']).exists() for item in cleanup['files'])
    for item in cleanup['files']: item['status']='deleted'
    cleanup.update({'status':'completed','completedAt':now,'deletedImageCount':len(cleanup['files']),'remainingGameImages':68,'remainingFinalContactSheets':6})
    write(ROOT/'cleanup.json',cleanup)
    for frame in read(ROOT/'manifest.json')['frames']:
        out=ROOT/frame['file']; derived_path=out.with_suffix('.png.generation.json'); derived=read(derived_path)
        assert out.exists() and sha(out)==derived['sha256']
        derived['derivedFrom'].update({'retained':False,'retentionReason':'最终PNG与来源链验证后，按用户素材保留规则删除本目录原生图片。','cleanupRecord':'cleanup.json'})
        derived['finalReviewRecord']='visual-review.json'
        write(derived_path,derived)
        native_path=ROOT/derived['derivedFrom']['generationRecord']; native=read(native_path)
        native.update({'sourceRetained':False,'sourceRemovalRecord':'cleanup.json','finalOutput':frame['file'],'finalOutputSHA256':derived['sha256'],'exportStatus':'completed','finalReviewRecord':'visual-review.json'})
        native['retentionNote']='本记录保留生成当时的路径、引用SHA、提示词和receipt；任务内原生/中间图片已于正式导出和审查后删除。历史输入SHA不会因同路径后续修图而改写。'
        write(native_path,native)
    print(json.dumps({'deletedImageCount':len(cleanup['files']),'retentionRecordsUpdated':68}))
else:
    raise SystemExit('Use prepare or complete')
