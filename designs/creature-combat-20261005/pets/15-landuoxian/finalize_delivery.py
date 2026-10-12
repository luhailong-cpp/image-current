"""Finalize only this pet's delivery and apply its approved image-retention policy."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

R = Path(__file__).resolve().parent
EXPECTED_ROOT = Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian').resolve()
assert R == EXPECTED_ROOT

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert read(R/'validation.json')['status'] == 'passed'
    assert read(R/'provenance-audit.json')['status'] == 'passed'
    manifest = read(R/'manifest.json')
    assert manifest['frameCount'] == 68
    now = datetime.now(timezone.utc).isoformat()
    hashes = {f['file']: sha(R/f['file']) for f in manifest['frames']}
    assert all(hashes[f['file']] == f['sha256'] for f in manifest['frames'])
    assert (R/'preview/delivery-proof.jpg').is_file()
    review = {
        'checkedAt': now, 'status': 'passed_asset_review', 'frameCount': 68,
        'scope': '素材静态与浏览器预览验收；不代表客户端接入或战斗系统验收。',
        'methods': [
            'root 与制作子代理累计实看 68 张最终帧、六组接触表和定点修正版。',
            'root 在本机浏览器打开最终 68 帧 Canvas 预览，核对六组 1×、0.25×播放截图样本与帧号推进。',
            '六组分别使用逐帧滑杆定位首帧、受击03/普攻07/施法09和末帧，核对起势、释放、收势。',
            '棋盘及深绿背景检查透明边缘，最终页面加载68/68、图片错误0、浏览器错误/警告0。'
        ],
        'checks': {
            'identity': '墨靛发、象牙青玉杏色衣、金玉饰物沿用原图',
            'directions': 'E斜前朝右下；W独立真斜后朝左上，保留后脑、背衣和鞋跟',
            'anatomy_and_props': '两臂两腿，无翼无尾；右手三玉铎金框、左手玉槌；没有发现换手或额外肢体',
            'chimes': 'E两长铎加一短喇叭口玉铎；W沿用原背面形制，三铎数量一致',
            'motion': '原地反冲、抬槌下挥、举框敲铎和回收动作阶段可辨',
            'closure': '各组末帧回到准备姿态；预览循环用于审查，游戏应一次播放后回待机'
        },
        'limitations': [
            '为逐帧AI绘制，衣褶、飘带与小饰物存在细微绘制差异。',
            '施法E的01→02抬框和10→11回收、普攻E的07→08回腕较快，已在慢放及关键帧中复核。',
            '固定整画布缩放与留边，不做逐帧脚底重对齐；目标脚点不等于每帧足底逐像素重合。',
            '浏览器验收基于实际加载、播放与截图样本；未录制视频或验证客户端渲染、碰撞和战斗时序。'
        ],
        'evidence': ['preview/delivery-proof.jpg'] + ['preview/'+g['id'].replace('/','-')+'-contact.png' for g in manifest['groups']],
        'frameHashes': hashes, 'clientIntegration': 'not_performed'
    }
    write(R/'visual-review.json', review)

    # Only generated/intermediate image files in this pet's provenance folder.
    candidates = sorted(p for p in (R/'provenance').rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'})
    removed = {}
    for p in candidates:
        resolved = p.resolve()
        rel = resolved.relative_to(R)
        assert rel.parts[0] == 'provenance' and not p.is_symlink()
        removed[str(resolved).casefold()] = {'file': rel.as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size,
            'reason': '正式1024透明PNG已落盘并通过技术、来源与视觉检查；清理本地原生图、拒稿、修改前稿或重复检查图。'}
    prior = read(R/'cleanup.json') if (R/'cleanup.json').exists() else None
    if prior and not candidates:
        ledger = prior
    else:
        ledger = {'performedAt': now, 'scope': str(R), 'policy': 'AGENTS.md 素材保留（2026-09-23 用户确认）',
            'status': 'prepared', 'removedImageCount': len(candidates), 'removedBytes': sum(x['bytes'] for x in removed.values()),
            'files': list(removed.values()), 'retained': ['runtime下68张正式PNG','preview下六组接触表、最终截图及HTML','全部逐图模型/质量/来源文字记录'],
            'outsideTaskDirectory': '原E/W身份图、已确认风格图和宿主缓存均未修改；不在本任务清理范围。'}
        write(R/'cleanup.json', ledger)

    def annotate(value):
        if isinstance(value, list):
            for item in value: annotate(item)
        elif isinstance(value, dict):
            for item in list(value.values()): annotate(item)
            for key in ['file','path','nativeFile']:
                v = value.get(key)
                if not isinstance(v, str): continue
                p = Path(v)
                if not p.is_absolute(): p = R/p
                entry = removed.get(str(p.resolve()).casefold())
                if entry:
                    value['removedAfterProduction'] = True
                    value['cleanupRecord'] = 'cleanup.json'
                    value.setdefault('sha256', entry['sha256'])

    # Add cleanup facts; preserve historical prompts, parameters, timestamps and receipts.
    for p in R.rglob('*.generation.json'):
        data = read(p)
        annotate(data)
        write(p, data)
    for f in manifest['frames']:
        p = R/f['generationRecord']; data = read(p)
        data['finalVisualReview'] = {'status': 'passed_asset_review', 'record': 'visual-review.json', 'sha256': f['sha256'], 'checkedAt': now}
        if data.get('visualReview') == 'pending': data['visualReview'] = 'see finalVisualReview'
        if isinstance(data.get('visualQA'), dict): data['visualQA']['motionPreview'] = 'see finalVisualReview; root browser review completed'
        write(p, data)
    for p in candidates:
        assert sha(p) == removed[str(p.resolve()).casefold()]['sha256']
        p.resolve().relative_to(R)
        p.unlink()
    ledger['status'] = 'completed'
    write(R/'cleanup.json', ledger)
    assert hashes == {f['file']: sha(R/f['file']) for f in manifest['frames']}
    print(json.dumps({'frames':68,'removedImages':ledger['removedImageCount'],'runtimeUnchanged':True}, ensure_ascii=False))

if __name__ == '__main__':
    main()
