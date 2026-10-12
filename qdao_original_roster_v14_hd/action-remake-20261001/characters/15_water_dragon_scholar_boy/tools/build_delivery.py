#!/usr/bin/env python3
"""水龙书生私有离线导出器（Python 3.10+ / Pillow，无需其他包）。

默认只读预检：python tools/build_delivery.py
写出：python tools/build_delivery.py --write
不同成品必须明确允许替换：python tools/build_delivery.py --write --replace
只列输入接口示例：python tools/build_delivery.py --example

仅扫描本角色 sources/new/**/*.png、sources/reused/**/*.png；绝不自动选最高版本。
sources-index.json 的 frames 是人工逐帧选表，accepted=true 才有资格导出。
选表缺失合法：产生 196 个空槽，绝不填图。每帧必须是至少 1024 的方形
原生单帧 RGBA PNG；nativeSingleFrame=true 是人工核实声明，不由尺寸推定。
generationRecord 指向本角色内原始逐图回执/其保真副本；内容整段保留于派生记录。
coordinateSystem.root 是 1024 全局画布坐标中的虚拟根锚点，必须主审离线复核。
全局坐标只允许整幅画布等比降采样至 940 并固定放入 1024 画布(42,49)，不逐帧贴脚。
索引不接受逐帧变换。没有生成、重画、镜像、补帧、插值或修改源图的功能。

--write 仅可写本角色 runtime/、provenance/derived/、manifest.json 及 preview 的两个离线 HTML。
既有 runtime 含未选槽时直接失败，不擅自删除旧资源。预检和写出均不把导出、
播放或像素唯一性当成动作/美术验收通过。客户端状态始终记录未接入/未测试。
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps
from render_review_board import TIMELINE_JS, json_for_html, load_run_timing, render_review_board, review_notice

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (ROOT / 'sources/new', ROOT / 'sources/reused')
SIZE = 1024
CONTENT_SIZE = 940
CONTENT_OFFSET = (42, 49)
SPECS = {
    'run': (('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'), 16, 60),
    'hit': (('E', 'W'), 6, 40),
    'attack': (('E', 'W'), 12, 30),
    'cast': (('E', 'W'), 16, 45),
}
EXAMPLE = {
    'schemaVersion': 1,
    'coordinateSystem': {
        'canvas': [1024, 1024], 'root': [512, 940],
        'note': '示例数值；请换成本角色经人工核实的全局虚拟根锚点。',
        'reviewedBy': '填写审阅者', 'reviewedAt': '填写带时区时间',
    },
    'frames': [{
        'action': 'hit', 'direction': 'E', 'frame': 3,
        'source': 'sources/new/hit-E-03.png', 'sha256': '填写64位实际SHA256',
        'accepted': True, 'nativeSingleFrame': True,
        'generationRecord': 'provenance/receipts/hit-E-03.json',
        'review': {'reviewer': '填写审阅者', 'reviewedAt': '填写带时区时间',
                   'notes': '填写身份、手脚、持物、方向、比例及透明边缘实际审阅结论'},
        'event': None,
    }],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f'禁止越出本角色目录: {value}')
    return path


def relative(path: Path) -> str:
    return safe_path(path).relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(result, dict):
        raise ValueError(f'要求 JSON 对象: {path}')
    return result


def inspect(path: Path) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        if source.format != 'PNG' or source.mode != 'RGBA':
            raise ValueError(f'要求原生 PNG RGBA: {relative(path)}')
        if source.width != source.height or source.width < SIZE:
            raise ValueError(f'要求至少 1024 的原生方形单帧: {relative(path)} {source.size}')
        source.load()
        result = source.copy()
    alpha = result.getchannel('A')
    threshold = alpha.point(lambda a: 255 if a > 8 else 0)
    bbox = threshold.getbbox()
    if not bbox or alpha.getextrema() != (0, 255):
        result.close()
        raise ValueError(f'透明/主体像素不完整: {relative(path)}')
    if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == result.width or bbox[3] == result.height:
        result.close()
        raise ValueError(f'主体触画布边缘，需人工修正: {relative(path)}')
    return result, {'width': result.width, 'height': result.height, 'mode': 'RGBA',
                    'format': 'PNG', 'visibleBBoxForAuditOnly': list(bbox),
                    'alphaExtrema': list(alpha.getextrema())}


def pixel_sha(image: Image.Image) -> str:
    # Ignore hidden RGB only for duplicate comparisons; never alter exported pixels.
    alpha = image.getchannel('A')
    canonical = Image.new('RGBA', image.size)
    canonical.paste(image, (0, 0), alpha.point(lambda a: 255 if a > 8 else 0))
    return digest(canonical.tobytes())


def inventory() -> list[dict]:
    rows = []
    for directory in SOURCE_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob('*.png')):
            path = safe_path(path)
            row = {'source': relative(path), 'sha256': digest(path.read_bytes()),
                   'sourceKind': 'reused' if directory.name == 'reused' else 'new'}
            try:
                with Image.open(path) as im:
                    row.update(width=im.width, height=im.height, mode=im.mode)
            except OSError as error:
                row['readError'] = str(error)
            rows.append(row)
    return rows


def slots() -> list[dict]:
    result = []
    for action, (directions, count, duration) in SPECS.items():
        for direction in directions:
            for number in range(1, count + 1):
                result.append({'slot': f'{action}-{direction}-{number:02d}',
                               'action': action, 'direction': direction, 'frame': number,
                               'durationMs': duration, 'timingStatus': 'user_requested_not_client' if action == 'run' else 'planned', 'source': None, 'output': None,
                               'status': 'missing', 'visualApproval': 'not_reviewed',
                               'derivedFrom': None, 'sha256': None, 'event': None})
    return result


def prepare() -> tuple[dict, list[tuple[Path, bytes]]]:
    index_path = safe_path('sources-index.json')
    index = read_json(index_path) if index_path.exists() else {'frames': []}
    if not isinstance(index.get('frames'), list):
        raise ValueError('sources-index.json 的 frames 必须是数组')
    if any(not isinstance(item, dict) for item in index['frames']):
        raise ValueError('frames 每一项必须是对象')
    inv = inventory()
    available = {row['source']: row for row in inv}
    entries = slots()
    by_slot = {row['slot']: row for row in entries}
    selected, pending, used_sources, pixels, mirrors = set(), [], set(), {}, {}
    coordinate = index.get('coordinateSystem')
    accepted = [item for item in index['frames'] if item.get('accepted') is True]
    if accepted:
        if not isinstance(coordinate, dict) or coordinate.get('canvas') != [SIZE, SIZE]:
            raise ValueError('有接受帧时必须指定统一 coordinateSystem.canvas=[1024,1024]')
        root = coordinate.get('root')
        if not isinstance(root, list) or len(root) != 2 or any(type(v) not in (int, float) or not 0 <= v <= SIZE for v in root):
            raise ValueError('coordinateSystem.root 必须是已核实的全局二维虚拟根锚点')
        if not all(coordinate.get(k) for k in ('note', 'reviewedBy', 'reviewedAt')):
            raise ValueError('统一根锚点必须记录 note/reviewedBy/reviewedAt')
    now = datetime.now(timezone.utc).isoformat()
    for item in index['frames']:
        if not isinstance(item, dict):
            raise ValueError('frames 每一项必须是对象')
        action, direction, number = item.get('action'), item.get('direction'), item.get('frame')
        if type(number) is not int:
            raise ValueError('frame 必须是整数')
        slot = f'{action}-{direction}-{number:02d}'
        if slot not in by_slot:
            raise ValueError(f'不合法的槽位: {slot}')
        if item.get('accepted') is not True:
            continue
        if slot in selected:
            raise ValueError(f'同槽重复接受: {slot}')
        selected.add(slot)
        if any(key in item for key in ('transform', 'scale', 'offset', 'crop', 'anchor', 'root')):
            raise ValueError(f'禁止逐帧变换参数: {slot}')
        if item.get('nativeSingleFrame') is not True:
            raise ValueError(f'必须核实为原生单帧，不能用图集小格: {slot}')
        review = item.get('review', {})
        if not all(review.get(k) for k in ('reviewer', 'reviewedAt', 'notes')):
            raise ValueError(f'缺少逐帧人工 review: {slot}')
        path = safe_path(item.get('source', ''))
        source_rel = relative(path)
        if source_rel not in available:
            raise ValueError(f'输入必须位于 sources/new 或 sources/reused: {source_rel}')
        if source_rel in used_sources:
            raise ValueError(f'同一原图被用于多个槽: {source_rel}')
        used_sources.add(source_rel)
        source_sha = digest(path.read_bytes())
        if item.get('sha256', '').lower() != source_sha:
            raise ValueError(f'选表与源图 SHA 不匹配: {slot}')
        receipt_path = safe_path(item.get('generationRecord', ''))
        receipt_bytes = receipt_path.read_bytes()
        receipt = read_json(receipt_path)
        # Old receipts keep their original schema and historical machine paths intact.
        recorded_sha = receipt.get('sha256') or receipt.get('sourceSha256')
        if recorded_sha and recorded_sha.lower() != source_sha:
            raise ValueError(f'原始回执与源图 SHA 不匹配: {slot}')
        image, geometry = inspect(path)
        native_size = image.width
        image.putalpha(image.getchannel('A').point(lambda value: 0 if value <= 8 else value))
        content = image.resize((CONTENT_SIZE, CONTENT_SIZE), Image.Resampling.LANCZOS)
        output = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        output.alpha_composite(content, CONTENT_OFFSET)
        content.close()
        image.close()
        key = pixel_sha(output)
        mirror_key = pixel_sha(ImageOps.mirror(output))
        if key in pixels or key in mirrors:
            output.close()
            raise ValueError(f'与 {pixels.get(key, mirrors.get(key))} 完全重复或镜像: {slot}')
        pixels[key], mirrors[mirror_key] = slot, slot
        buffer = io.BytesIO()
        output.save(buffer, format='PNG')
        output.close()
        png = buffer.getvalue()
        out_path = safe_path(f'runtime/{action}/{direction}/{number:02d}.png')
        derived_path = safe_path(f'provenance/derived/{slot}.json')
        derived_from = {'path': source_rel, 'sha256': source_sha,
                        'generationRecord': relative(receipt_path),
                        'generationRecordSha256': digest(receipt_bytes)}
        transform = {'kind': 'uniform_whole_canvas_downsample',
                     'nativeCanvas': [native_size, native_size], 'outputCanvas': [SIZE, SIZE],
                     'factor': CONTENT_SIZE / native_size, 'offset': list(CONTENT_OFFSET),
                     'scaledWholeCanvas': [CONTENT_SIZE, CONTENT_SIZE],
                     'alphaCleanup': 'source alpha <= 8 set to 0 uniformly; no anatomy editing',
                     'coordinateSystem': coordinate, 'bboxUsedForTransform': False,
                     'perFrameGroundAlignment': False, 'poseSynthesis': False,
                     'filter': 'Pillow LANCZOS; fixed whole-canvas transform retained from prior run manifest'}
        record = {'schemaVersion': 1, 'character': ROOT.name, 'slot': slot,
                  'file': relative(out_path), 'sha256': digest(png), 'derivedAt': now,
                  'derivedFrom': derived_from, 'sourceKind': available[source_rel]['sourceKind'],
                  'originalGenerationRecord': receipt, 'nativeGeometry': geometry,
                  'operation': transform, 'visualReview': review,
                  'animationApproval': 'pending', 'clientIntegration': 'not_integrated',
                  'clientRuntimeAcceptance': 'not_tested'}
        pending.extend([(out_path, png), (derived_path, encode_json(record))])
        by_slot[slot].update(source=source_rel, output=relative(out_path), sha256=digest(png),
                             status='accepted_pending_export', visualApproval='accepted_by_selection',
                             derivedFrom=derived_from, derivedRecord=relative(derived_path),
                             event=item.get('event'), sourceKind=available[source_rel]['sourceKind'],
                             visiblePixelSha256=key, review=review)
    expected_runtime = {path for path, _ in pending if path.suffix == '.png'}
    existing = {safe_path(path) for path in safe_path('runtime').rglob('*.png')} if safe_path('runtime').exists() else set()
    stale = existing - expected_runtime
    if stale:
        raise ValueError('存在未被本次选表选中的成品，拒绝忽略/删除: ' + ', '.join(relative(p) for p in sorted(stale)))
    groups = []
    for action, (directions, count, duration) in SPECS.items():
        for direction in directions:
            group = [row for row in entries if row['action'] == action and row['direction'] == direction]
            present = sum(row['output'] is not None for row in group)
            groups.append({'action': action, 'direction': direction, 'expected': count,
                           'accepted': present, 'durationMs': duration, 'cycleMs': count * duration,
                           'timingStatus': 'user_requested_not_client' if action == 'run' else 'planned',
                           'trialCyclesMs': [] if action == 'run' else None,
                           'missing': [row['frame'] for row in group if row['output'] is None],
                           'animationApproval': 'pending' if present == count else 'incomplete_not_reviewable'})
    manifest = {'schemaVersion': 1, 'character': ROOT.name, 'builtAt': now,
                'timeZone': 'America/New_York', 'expected': 196, 'accepted': len(selected),
                'exported': 0, 'missing': 196 - len(selected), 'coordinateSystem': coordinate,
                'inventory': inv, 'frames': entries, 'groups': groups,
                'selection': relative(index_path) if index_path.exists() else None,
                'selectionSha256': digest(index_path.read_bytes()) if index_path.exists() else None,
                'animationApproval': 'pending' if len(selected) == 196 else 'incomplete_not_reviewable',
                'clientIntegration': 'not_integrated', 'clientRuntimeAcceptance': 'not_tested',
                'note': '逐帧选择只证明已审阅该帧；文件齐全、播放和SHA不同均不证明动作美术通过。'}
    return manifest, pending


def encode_json(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>15 水龙书生 · 四动作进度预览</title><style>[hidden]{display:none!important}
*{box-sizing:border-box}body{background:#101c28;color:#e8f1f8;font:16px/1.55 system-ui,"Microsoft YaHei",sans-serif;margin:24px}main{max-width:1160px;margin:auto}h1{font-size:26px}button,select{font:inherit;padding:7px;margin:3px;background:#e5eef5;border:0;border-radius:5px}input{width:100%}.layout{display:grid;grid-template-columns:minmax(300px,650px) 1fr;gap:24px}.stage{aspect-ratio:1;position:relative;background:repeating-conic-gradient(#dce6ee 0 25%,#edf3f7 0 50%) 50%/32px 32px;border:1px solid #75899b}.stage.dark{background:#0a0f15}.stage.white{background:#fff}.stage #sprite{width:100%;height:100%;object-fit:contain}.empty{position:absolute;inset:0;display:grid;place-content:center;text-align:center;color:#32465a;background:#d9e2eacc;font-size:24px}.tag{background:#3c3020;border-left:4px solid #dcaf68;padding:12px}.slots{display:flex;gap:5px;flex-wrap:wrap}.slots button{font-size:13px;background:#576374;color:#fff}.slots button.ok{background:#246e5a}.slots button.current{outline:3px solid #ffd170}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;max-height:320px;overflow:auto}.meta{color:#bccede}.root{position:absolute;width:16px;height:16px;border:1px solid #f05b5b;border-radius:100%;transform:translate(-50%,-50%);pointer-events:none}.root:after{content:"";position:absolute;inset:7px -7px;border-top:1px solid #f05b5b}@media(max-width:860px){.layout{grid-template-columns:1fr}}</style>
<main><h1>15 水龙书生 · 四动作本地预览</h1><p id="summary"></p><p><a href="all-directions.html" style="color:#b6dfff">打开八方向跑步与六组战斗同播</a></p><p class="tag">__REVIEW_NOTICE__ 缺帧保持空槽，播放会真实显示缺口。</p><div class="layout"><section><div id="stage" class="stage"><canvas id="sprite" width="1024" height="1024" hidden></canvas><div id="empty" class="empty"></div><div id="root" class="root" hidden></div></div><p id="counter"></p><button id="play">播放</button><button id="pause">暂停</button><button id="previous">上一帧</button><button id="next">下一帧</button><input id="scrub" type="range" min="1" max="16" value="1"><div id="slots" class="slots"></div></section><aside><label>动作与方向 <select id="group"></select></label><p><label>速度 <select id="speed"><option value="1">1× 当前节奏</option><option value="0.25">0.25× 慢速</option></select></label></p><p><label>跑步试播 <select id="runCycle"></select></label></p><p><label>画布显示 <select id="displaySize"><option value="240">240px 游戏尺寸参考</option><option value="384">384px 放大复核</option><option value="520">520px 细节</option></select></label></p><button id="background">切换背景</button><label><input id="anchor" type="checkbox" style="width:auto">显示全局虚拟根</label><p id="timing"></p><p id="status" class="tag"></p><p class="meta">逐帧检查：两手两脚、扇子握持、玉佩侧别、膝踝与远近腿、支撑与腾空、比例与首尾接续。红色根标记来自人工统一坐标；不会按每张图的脚底调整。</p><details><summary>本槽来源与验收记录</summary><pre id="details"></pre></details></aside></div></main>
<script id="data" type="application/json">__DATA__</script><script id="timingData" type="application/json">__TIMING__</script><script>
'use strict';
__TIMELINE_JS__
const timing=JSON.parse(document.getElementById('timingData').textContent);const m=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id),names={run:'跑步',hit:'受击',attack:'普攻',cast:'施法'};let gi=0,fi=0,playing=false,raf=0,start=0,bg=0;const loaded=new Map();
const groups=m.groups.map(g=>({...g,frames:m.frames.filter(f=>f.action===g.action&&f.direction===g.direction).sort((a,b)=>a.frame-b.frame)}));
for(const profile of timing.profiles){const option=document.createElement('option');option.value=profile.id;option.textContent=profileLabel(profile);$('runCycle').append(option)}$('runCycle').value=timing.defaultProfile;
$('summary').textContent=`已导出 ${m.exported}/196；本地动态已审 ${groups.filter(offlineGroup).length}/14组；${m.animationApproval==='offline_reviewed'?'本聊天主审离线复核完成；用户尚未验收，未接入客户端':m.animationApproval==='incomplete_not_reviewable'?'缺帧，尚不具备整组验收条件':m.staticReview?'静态逐帧已审；正常/慢速动态待复核':'待完整主审离线复核'}`;
groups.forEach((g,i)=>{let o=document.createElement('option');o.value=i;o.textContent=`${names[g.action]} ${g.direction} · ${g.accepted}/${g.expected}`;$('group').append(o)});
function durations(g){return groupDurations(g,timing,$('runCycle').value)}
function stop(){playing=false;cancelAnimationFrame(raf)}
function show(){const g=groups[gi],f=g.frames[fi];$('counter').textContent=`${names[g.action]} ${g.direction} · ${fi+1}/${g.expected} · ${f.output?'已导出':'缺帧'}`;$('scrub').max=g.expected;$('scrub').value=fi+1;$('sprite').hidden=true;$('sprite').getContext('2d').clearRect(0,0,1024,1024);$('empty').hidden=false;$('empty').textContent=f.output?'读取图片…':`缺帧 ${f.slot}\n当前槽位为空`;if(f.output){const url='../'+f.output;const image=loaded.get(url);if(image&&image.complete&&image.naturalWidth===1024){$('sprite').getContext('2d').drawImage(image,0,0,1024,1024);$('sprite').hidden=false;$('empty').hidden=true}else if(image&&image.complete){$('empty').textContent='图片读取失败：'+f.slot;}}
 const values=durations(g),speed=Number($('speed').value);$('runCycle').disabled=g.action!=='run';$('timing').textContent=`${g.action==='run'?profileLabel(runProfile(timing,$('runCycle').value)):'原战斗方案'} · 本帧 ${values[fi]}ms；原始周期 ${durationTotal(values)}ms；${speed}× 播放周期 ${durationTotal(values)/speed}ms${g.action==='run'?' · '+timingReviewLabel(runProfile(timing,$('runCycle').value)):''}`;$('status').textContent=g.accepted<g.expected?`缺 ${g.expected-g.accepted} 帧；目前只可看单帧及时间线缺口，不能判定整段动画通过。`:offlineGroup(g)?'本段已由本聊天主审完成离线静态、正常/慢速动态复核；用户尚未验收，未接入客户端。':m.staticReview?'本段帧已齐，静态逐帧已审；正常/慢速动态观感待复核，客户端未接入。':'本段帧已齐；正常/慢速播放及逐帧美术验收仍待主审离线复核。';$('details').textContent=JSON.stringify(f,null,2);$('slots').replaceChildren();g.frames.forEach((x,i)=>{const b=document.createElement('button');b.textContent=String(i+1).padStart(2,'0');b.className=(x.output?'ok ':'')+(i===fi?'current':'');b.onclick=()=>{stop();fi=i;show()};$('slots').append(b)});const root=m.coordinateSystem?.root;$('root').hidden=!root||!$('anchor').checked;if(root){$('root').style.left=(root[0]/1024*100)+'%';$('root').style.top=(root[1]/1024*100)+'%';}}
function tick(now){if(!playing)return;const g=groups[gi];const next=frameAt(durations(g),(now-start)*Number($('speed').value));if(next!==fi){fi=next;show()}raf=requestAnimationFrame(tick)}
$('play').onclick=()=>{stop();playing=true;start=performance.now()-frameStart(durations(groups[gi]),fi)/Number($('speed').value);raf=requestAnimationFrame(tick)};$('pause').onclick=stop;$('previous').onclick=()=>{stop();fi=(fi-1+groups[gi].expected)%groups[gi].expected;show()};$('next').onclick=()=>{stop();fi=(fi+1)%groups[gi].expected;show()};$('scrub').oninput=()=>{stop();fi=Number($('scrub').value)-1;show()};$('group').onchange=()=>{stop();gi=Number($('group').value);fi=0;show()};$('speed').onchange=()=>{stop();show()};$('runCycle').onchange=()=>{stop();show()};$('displaySize').onchange=()=>{$('stage').style.width=$('displaySize').value+'px';show()};$('stage').style.width='240px';$('background').onclick=()=>{$('stage').className='stage '+['','dark','white'][++bg%3]};$('anchor').onchange=show;document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
for(const f of m.frames){if(!f.output)continue;const url='../'+f.output,im=new Image();loaded.set(url,im);im.onload=show;im.onerror=show;im.src=url}show();
</script></html>'''


def render_main_preview(manifest: dict, timing: dict) -> str:
    return (HTML.replace('__DATA__', json_for_html(manifest))
            .replace('__TIMING__', json_for_html(timing)).replace('__TIMELINE_JS__', TIMELINE_JS)
            .replace('__REVIEW_NOTICE__', review_notice(manifest, timing)))


def write_file(path: Path, content: bytes) -> None:
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true', help='写出本角色成品、派生记录、196 槽清单及离线预览')
    parser.add_argument('--replace', action='store_true', help='只配合 --write，允许替换已有但内容不同的已选成品')
    parser.add_argument('--example', action='store_true', help='打印 sources-index.json 示例，不写文件')
    args = parser.parse_args()
    if args.example:
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=2))
        return 0
    if args.replace and not args.write:
        parser.error('--replace 必须配合 --write')
    timing = load_run_timing()
    manifest, pending = prepare()
    if args.write:
        for path, content in pending:
            if path.suffix == '.png' and path.exists() and path.read_bytes() != content and not args.replace:
                raise ValueError(f'成品已有不同内容，需主审离线复核后 --replace: {relative(path)}')
        # Preflight completed before any write. Source and selection remain read-only.
        for path, content in pending:
            write_file(path, content)
        for row in manifest['frames']:
            if row['output']:
                row['status'] = 'exported'
        manifest['exported'] = manifest['accepted']
        write_file(safe_path('manifest.json'), encode_json(manifest))
        write_file(safe_path('preview/index.html'), render_main_preview(manifest, timing).encode('utf-8'))
        write_file(safe_path('preview/all-directions.html'), render_review_board(manifest, timing).encode('utf-8'))
    print(json.dumps({k: manifest[k] for k in ('character', 'expected', 'accepted', 'exported', 'missing', 'animationApproval', 'clientIntegration')}, ensure_ascii=False, indent=2))
    print('已写出 runtime/、provenance/derived/、manifest.json、preview/index.html 与 all-directions.html' if args.write else '只读预检完成；未写出。用 --write 生成当前真实进度预览。')
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f'build_delivery: {error}', file=sys.stderr)
        raise SystemExit(2)
