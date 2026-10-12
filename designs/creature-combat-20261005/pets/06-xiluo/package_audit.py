"""Record package references and remove only obsolete QA images inside this pet folder."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name, data): (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
report = read(ROOT/'qa/technical-validation.json')
manifest = read(ROOT/'manifest.json')
assert report['technicalStatus'] == 'passed' and report['presentFrames'] == 68
assert len(manifest['frames']) == 68
for frame in manifest['frames']:
    assert sha(ROOT/frame['file']) == frame['sha256'], frame['file']
media = read(ROOT/'preview/media-manifest.json')
assert len(media) == 12
for item in media:
    assert sha(ROOT/item['file']) == item['sha256'], item['file']
    for rel, digest in zip(item['sourceFiles'],item['sourceSha256']):
        assert sha(ROOT/rel) == digest, rel
for rel in ['records/attack/E/07.json','records/attack/E/08.json',
            'records/cast/W/10.json','records/cast/W/11.json','records/attack/W/09.json']:
    assert 'repair' in read(ROOT/rel)['prompt'], rel

refs = []
for role, path in [
    ('original_identity_E','D:/work/image/designs/pets-xianling-20260924/source/06-xiluo-E.png'),
    ('original_identity_W','D:/work/image/designs/pets-xianling-20260924/source/06-xiluo-W.png'),
    ('approved_painted_style','D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png')]:
    p = Path(path)
    with Image.open(p) as im:
        refs.append({'role':role,'path':path,'sha256':sha(p),'width':im.width,'height':im.height,'mode':im.mode,
                     'usage':'Actually attached to every generation/edit; shared reference is read-only',
                     'historicalActualModel':None,'historicalActualQuality':None,
                     'versionNote':'Current file hash only; original generation version is not inferred from this batch target.'})
write('references.json',{'checkedAt':now,'references':refs,'notes':[
    'These three shared identity/style files remain available and are not cleanup targets.',
    'Historical predecessor frame inputs are recorded in per-frame receipts and generation-audit.json.',
    'The current style reference hash may differ from an old upstream manifest; this package does not rewrite shared history.'
]})

review = {'reviewedAt':now,'asset':'06-xiluo','currentFrames':68,
    'singleFrameVisualReview':'completed_with_observations',
    'orderedSequenceContactReview':'completed',
    'realtimePlayback':{'normal':'not_verified','quarterSpeed':'not_verified',
        'reason':'In-app browser rejected the local file URL under its security policy. No workaround was attempted; static contact review and decoded media timing are not claimed as realtime visual playback.'},
    'clientIntegration':'not_tested',
    'mediaDecodeAndTiming':'passed_for_12_WebP_files; see preview/media-manifest.json',
    'reviewMethod':'Actual views of all generated frames and six ordered groups, additional full-size targeted corrections and independent cast reviews; no realtime smoothness assertion.',
    'identityAndAnatomy':'Original coral-apricot crab spirit, celadon cloud shell, ivory silk, osmanthus bell/red knot/jade-gold joints; six walking legs and two pincers with perspective occlusion; E front lower-right, W real rear upper-left.',
    'groups':[
        {'action':'hit','direction':'E','frames':6,'notes':'Recoil, compression and recovery remain in place; front identity and support preserved.'},
        {'action':'hit','direction':'W','frames':6,'notes':'Rear silhouette preserved; visible strong compression and quick spring-back, real-time rhythm not evaluated.'},
        {'action':'attack','direction':'E','frames':12,'notes':'Wind-up, extension, contact and retraction visible in order. Frames07/08 repaired by AI to restore closed pincer finger seams; final replacements viewed.'},
        {'action':'attack','direction':'W','frames':12,'notes':'True rear strike. Frame09 repaired to retain a partial raised-claw recovery between08 and10; final replacement viewed.'},
        {'action':'cast','direction':'E','frames':16,'notes':'Raise/gather/short jade-water release/dissipation/recovery reviewed. Far-side legs partly occluded. See static-review-cast-E.md.'},
        {'action':'cast','direction':'W','frames':16,'notes':'Rear gathering and release visible. Previously incorrect12/13/14 poses corrected. Final10/11 ribbon outer arcs repaired and viewed; see static-review-cast-W.md.'}],
    'acceptedObservations':[
        {'id':'AE-01','detail':'attack E01/E02 to03 has approximately20px of left shell-contour width variation; subsequent03–12 are comparatively stable. No direction flip or added limb, realtime visibility not assessed.'},
        {'id':'CE-01','detail':'cast E frame16 versus01 shell/silk upper contour differs approximately21 export pixels (top119 vs98; bottom985 vs986). This is contour variation, not whole-sprite translation. Actual idle transition needs playback/in-engine review.'},
        {'id':'CW-01','detail':'cast W04 compression and07→08 claw raise are visible pose changes; realtime rhythm is not confirmed.'},
        {'id':'PAINT-01','detail':'Independently generated frames have small shell/texture contour variations; no claim of pixel-registered or seamless idle looping.'},
        {'id':'EDGE-01','detail':'cast W08/09/12 have only low-alpha outermost-column contacts (max29/51/20, no alpha>128), not visible opaque silhouette truncation.'}],
    'correctedCurrentFiles':[{'file':f['file'],'sha256':f['sha256'],'generationRecord':f['generationRecord']} for f in manifest['frames'] if f['file'] in ['runtime/attack/E/07.png','runtime/attack/E/08.png','runtime/attack/W/09.png','runtime/cast/W/10.png','runtime/cast/W/11.png']],
    'currentContactSheets':[f'qa/{a}-{d}-contact.jpg' for a in ['hit','attack','cast'] for d in ['E','W']]}
write('qa/visual-review.json',review)
(ROOT/'STATUS.md').write_text('''# 汐螺交付状态

2026-10-08：受击、普攻、施法六组共68/68张正式素材已完成并落盘，1024×1024 RGBA透明。E斜前右下、W真斜后左上；hit每向6×40ms、attack12×30ms、cast16×45ms。仅原地战斗动作。

本次已完成普攻E07/E08闭钳合缝、W09回收阶段、施法W10/W11绢带触边的真实AI定点修订。当前PNG绑定的SHA、来源记录和manifest已重建；技术核验通过，无缺帧或重复RGBA帧。已实看全部帧及有序联系图。

12个正常/0.25×动画WebP已按真实帧时导出并解码验证，交互预览支持暂停与逐帧。实时连播视觉验收因浏览器本地file安全限制未完成；未绕过限制，不宣称动态通过。cast E收势约21px壳顶轮廓差及其它观察项见qa/visual-review.json。未接入客户端或测试游戏内播放。

逐图模型目标GPT Image2.5/max；内置实际model/quality未披露，均null。原生1254至正式1024仅用每向统一整画布变换；无镜像、复制、平移或插值造帧。历史失败和替换稿仅保留文字证据，不覆盖当前结论。

本包过期加工联系图已在成品及引用验证后清理；宿主外部原生缓存不在本任务可写目录内，未改动且不交付。共享身份/风格参考保留。未读写客户端、兄弟仓库；未做Git操作。

入口：[README](README.md) · [预览](preview.html) · [清单](manifest.json) · [技术验证](qa/technical-validation.json) · [视觉记录](qa/visual-review.json) · [交接](MERGE_HANDOFF.md)
''',encoding='utf-8')

# The task explicitly limits writes to this pet directory. Never alter external host caches.
removed = []
cleanup_path = ROOT/'cleanup.json'
if cleanup_path.exists(): removed = read(cleanup_path).get('removedPackageFiles',[])
obsolete = sorted((ROOT/'qa').glob('static-*.jpg')) + [ROOT/'qa/cast-W-right-edge.png']
for p in obsolete:
    if not p.is_file(): continue
    resolved = p.resolve()
    assert resolved.is_relative_to((ROOT/'qa').resolve()), str(resolved)
    removed.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'removedAt':now,
                    'reason':'Obsolete expanded/intermediate review image; current six contact sheets and textual review retained.'})
    p.unlink()
ledger = read(ROOT/'generation-audit.json')
external = {}
for item in ledger['entries']:
    if item.get('nativePath'):
        p=Path(item['nativePath'])
        assert not p.resolve().is_relative_to(ROOT.resolve()), str(p)
        external[str(p.resolve()).lower()]={'path':str(p),'sha256':item.get('sha256'),
            'exists':p.is_file(),'includedInDelivery':False,'role':'Host-managed native generation cache outside sole writable package directory'}
write('cleanup.json',{'checkedAt':now,'scope':str(ROOT),'finalFrameCount':68,
    'finalReferencesVerifiedBeforeCleanup':True,'removedPackageFiles':removed,
    'retainedPackageImages':['runtime: 68 final RGBA PNGs','preview: 12 final playback WebP files','qa: 6 final contact JPEGs'],
    'originalsOrRejectedImagesInsidePackage':0,'externalNativeCaches':list(external.values()),
    'externalCacheHandling':'Not modified: TASK.md permits writes only within this pet package. Cache pixels are not delivered or required by the game. Their truthful availability and SHA remain recorded.',
    'sharedIdentityAndStyleReferences':'Read-only, retained at original paths',
    'textEvidence':'Prompts, receipts, native SHA, rejected-attempt records and review notes are retained.'})
print(json.dumps({'references':len(refs),'packageIntermediateImagesRemoved':len(removed),'externalCachePaths':len(external),'finalAndPreviewHashesVerified':True}))
