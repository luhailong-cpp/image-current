"""从当前 manifest 的 1024 runtime 生成离线同播页；不改清单或验收状态。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_run_timing() -> dict:
    timing = json.loads((ROOT / 'audit/run-timing.json').read_text(encoding='utf-8-sig'))
    if timing.get('frameCount') != 16:
        raise ValueError('跑步候选时序必须对应 16 个真实槽位')
    profiles = timing.get('profiles', [])
    ids = [p['id'] for p in profiles]
    if len(ids) != len(set(ids)) or timing.get('defaultProfile') not in ids:
        raise ValueError('跑步时序 ID 重复或默认候选不存在')
    for profile in profiles:
        values = profile.get('frameDurationsMs', [])
        if len(values) != 16 or any(type(v) not in (int, float) or v <= 0 for v in values):
            raise ValueError(f"无效逐帧时长: {profile['id']}")
        if sum(values) != profile.get('cycleMs'):
            raise ValueError(f"逐帧累计周期不符: {profile['id']}")
    return timing


def frame_durations(group: dict, rows: list[dict], timing: dict, profile_id: str | None = None) -> list[float]:
    if group['action'] == 'run':
        profile_id = profile_id or timing['defaultProfile']
        profile = next(p for p in timing['profiles'] if p['id'] == profile_id)
        return [profile['frameDurationsMs'][row['frame'] - 1] for row in rows]
    return [row.get('durationMs', group['durationMs']) for row in rows]


def gif_durations(values: list[float], *, legacy_combat: bool = False) -> list[int]:
    """累计边界取整到 10ms，避免独立四舍五入改变总周期；不增删帧。"""
    result, cumulative, previous = [], 0.0, 0
    for value in values:
        cumulative += value
        boundary = round(cumulative / 10) * 10 if legacy_combat else int((cumulative + 5) // 10) * 10
        result.append(boundary - previous)
        previous = boundary
    if any(v <= 0 for v in result):
        raise ValueError('GIF 时长量化产生零时长帧')
    return result


def json_for_html(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')


def offline_reviewed(manifest: dict, timing: dict) -> bool:
    return (manifest.get('animationApproval') == 'offline_reviewed'
            and timing.get('status') == 'offline_selected_not_client'
            and len(manifest.get('frames', [])) == 196
            and all(row.get('animationApproval') == 'offline_reviewed' for row in manifest['frames'])
            and len(manifest.get('groups', [])) == 14
            and all(group.get('animationApproval') == 'offline_reviewed' for group in manifest['groups']))


def review_notice(manifest: dict, timing: dict) -> str:
    if offline_reviewed(manifest, timing):
        return '本聊天主审已按所引复核记录完成196帧、14组动作的离线静态与动态复核。用户尚未验收。跑步采用960ms/圈、每帧60ms（本地）。客户端未接入、未运行验收。'
    if manifest.get('staticReview') and all(r.get('visualApproval') == 'static_sequence_reviewed' for r in manifest['frames']):
        return '修复版196帧已导出并完成静态逐帧检查；跑步每圈960ms、每帧60ms。最新正常/慢速动态观感待验收；客户端未接入。'
    return '用户指出其他方向仍有问题，现参照竹弓少女重修；文件齐全不代表通过。跑步已按最新要求改为960ms/圈、每帧60ms。客户端未接入、未运行验收。'


# Shared elapsed-time lookup: each real cel owns one interval, no duplicate images.
TIMELINE_JS = r'''
function durationTotal(values){return values.reduce((sum,value)=>sum+value,0)}
function frameStart(values,index){return durationTotal(values.slice(0,index))}
function frameAt(values,elapsed){
 const total=durationTotal(values);let position=((elapsed%total)+total)%total;
 for(let index=0;index<values.length;index++){if(position<values[index])return index;position-=values[index]}
 return values.length-1;
}
function runProfile(timing,id){return timing.profiles.find(profile=>profile.id===id)}
function groupDurations(group,timing,profileId){
 return group.action==='run'?runProfile(timing,profileId).frameDurationsMs:
 group.frames.map(frame=>frame.durationMs??group.durationMs);
}
function offlineGroup(group){return m.animationApproval==='offline_reviewed'&&group.animationApproval==='offline_reviewed'}
function offlineSelected(){return m.animationApproval==='offline_reviewed'&&timing.status==='offline_selected_not_client'&&m.groups.length===14&&m.groups.every(offlineGroup)}
function profileLabel(profile){return profile.status==='offline_selected_not_client'&&!offlineSelected()?'960ms 正常节奏（姿态待复核）':profile.label}
function timingReviewLabel(profile){return offlineSelected()&&profile.id===timing.defaultProfile?'本地已选正常节奏；未入客户端':profile.status==='legacy_baseline_not_approved_normal'?'仅旧基线；未入客户端':profile.status==='comparison_only'?'仅对比节奏；未入客户端':'待最终评审；未入客户端'}
'''

BOARD_HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>15 水龙书生 · 全方向同播复核</title><style>
*{box-sizing:border-box}body{margin:20px;background:#111f2b;color:#edf4fa;font:15px/1.5 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1060px;margin:auto}h1{font-size:25px}h2{font-size:21px;margin-top:28px}a{color:#b6dfff}button,select{font:inherit;padding:7px;border:0;border-radius:5px;margin:4px;background:#e2edf3;color:#172c3a}.notice{padding:12px;border-left:4px solid #edb858;background:#3e3425}.toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}.scroll{overflow-x:auto;padding-bottom:5px}.run-grid{display:grid;grid-template-columns:repeat(4,240px);gap:20px;width:max-content}.combat-grid{display:grid;grid-template-columns:repeat(2,500px);gap:20px;width:max-content}.card{margin:0;padding:0}.title{font-size:16px;font-weight:600;margin:0 0 5px}.pair{display:grid;grid-template-columns:repeat(2,240px);gap:20px}.cell canvas{display:block;width:240px;height:240px;background:repeating-conic-gradient(#dce6ee 0 25%,#edf3f7 0 50%) 50%/24px 24px}.caption{font-size:12px;color:#bcd0df;min-height:36px;margin-top:5px;max-width:240px}.mode{font-size:13px;margin:0 0 5px}.meta{color:#bcd0df}#runInfo{min-height:48px}
</style><main><h1>15 水龙书生 · 八方向与战斗同播</h1><p><a href="index.html">打开单动作、逐帧与来源详情</a></p>
<p class="notice">__REVIEW_NOTICE__ 这里只读取当前清单的1024 PNG，以240px显示。</p>
<div class="toolbar"><button id="play">播放全部</button><button id="pause">暂停全部</button><button id="reset">从首帧同步</button><span id="loadState">正在预载当前成品…</span></div>
<h2>跑步 · 8 方向 4×2 同播</h2><div class="toolbar"><label>跑步周期 <select id="profile"></select></label><label>跑步速度 <select id="speed"><option value="1">1× 当前节奏</option><option value="0.25">0.25× 慢速</option></select></label></div><p id="runInfo" class="meta"></p><div class="scroll"><section id="runs" class="run-grid"></section></div>
<h2>战斗 · 6 组正常 / 慢速并列</h2><p class="meta">受击 240ms、普攻 360ms、施法 720ms 保留原方案；每组右侧固定 0.25×。跑步节奏选择不改变战斗计时。</p><div class="scroll"><section id="combats" class="combat-grid"></section></div><p class="meta">没有复制、镜像、插值或逐帧贴地。暂停后点击“从首帧同步”可检查共同起点；逐帧操作请使用单动作预览。</p></main>
<script id="manifest" type="application/json">__MANIFEST__</script><script id="timingData" type="application/json">__TIMING__</script><script>
'use strict';
__TIMELINE_JS__
const $=id=>document.getElementById(id),m=JSON.parse($('manifest').textContent),timing=JSON.parse($('timingData').textContent),names={run:'跑步',hit:'受击',attack:'普攻',cast:'施法'},views=[],images=new Map();
let elapsed=0,runElapsed=0,last=null,playing=false,ready=false,failures=0;
const groups=m.groups.map(group=>({...group,frames:m.frames.filter(frame=>frame.action===group.action&&frame.direction===group.direction).sort((a,b)=>a.frame-b.frame)}));
for(const profile of timing.profiles){const option=document.createElement('option');option.value=profile.id;option.textContent=profileLabel(profile);$('profile').append(option)}$('profile').value=timing.defaultProfile;
function cell(group,speed,parent){const box=document.createElement('div');box.className='cell';if(group.action!=='run'){const mode=document.createElement('p');mode.className='mode';mode.textContent=speed===1?'1× 原方案':'0.25× 慢速';box.append(mode)}const canvas=document.createElement('canvas');canvas.width=canvas.height=240;const caption=document.createElement('div');caption.className='caption';box.append(canvas,caption);parent.append(box);views.push({group,speed,canvas,caption,index:-1})}
for(const direction of ['N','NE','E','SE','S','SW','W','NW']){const group=groups.find(g=>g.action==='run'&&g.direction===direction);if(!group)continue;const card=document.createElement('section');card.className='card';const title=document.createElement('p');title.className='title';title.textContent=`跑步 ${direction}`;card.append(title);cell(group,1,card);$('runs').append(card)}
for(const action of ['hit','attack','cast'])for(const direction of ['E','W']){const group=groups.find(g=>g.action===action&&g.direction===direction);if(!group)continue;const card=document.createElement('section');card.className='card';const title=document.createElement('p');title.className='title';title.textContent=`${names[action]} ${direction}`;card.append(title);const pair=document.createElement('div');pair.className='pair';cell(group,1,pair);cell(group,0.25,pair);card.append(pair);$('combats').append(card)}
function draw(force=false){for(const view of views){const durations=groupDurations(view.group,timing,$('profile').value),speed=view.group.action==='run'?Number($('speed').value):view.speed,index=frameAt(durations,(view.group.action==='run'?runElapsed:elapsed)*speed);if(!force&&index===view.index)continue;view.index=index;const frame=view.group.frames[index],image=frame.output?images.get(frame.output):null,ctx=view.canvas.getContext('2d');ctx.clearRect(0,0,240,240);if(image?.complete&&image.naturalWidth===1024)ctx.drawImage(image,0,0,240,240);view.caption.textContent=`${index+1}/${view.group.expected} · 本帧 ${durations[index]}ms · ${speed}×${frame.output?(image?.naturalWidth===1024?'':' · 图片未读取'):' · 缺帧'}`}}
function info(){const profile=runProfile(timing,$('profile').value),speed=Number($('speed').value);$('runInfo').textContent=`${profileLabel(profile)}；原始逐帧 ${profile.frameDurationsMs.join(' / ')} ms；当前一圈 ${profile.cycleMs/speed} ms。${timingReviewLabel(profile)}。`}
function tick(now){if(last!==null&&playing){elapsed+=now-last;runElapsed+=now-last}last=now;draw();requestAnimationFrame(tick)}
$('play').onclick=()=>{if(ready){playing=true;last=null}};$('pause').onclick=()=>{playing=false;last=null};$('reset').onclick=()=>{elapsed=0;runElapsed=0;last=null;draw(true)};$('profile').onchange=$('speed').onchange=()=>{runElapsed=0;info();draw(true)};document.addEventListener('visibilitychange',()=>{if(document.hidden){playing=false;last=null}});
const loads=[];for(const frame of m.frames){if(!frame.output||images.has(frame.output))continue;const image=new Image();images.set(frame.output,image);loads.push(new Promise(resolve=>{image.onload=()=>{if(image.naturalWidth!==1024||image.naturalHeight!==1024)failures++;resolve()};image.onerror=()=>{failures++;resolve()};image.src='../'+frame.output}))}
info();draw();requestAnimationFrame(tick);Promise.all(loads).then(()=>{ready=true;elapsed=0;runElapsed=0;last=null;playing=true;$('loadState').textContent=`已读取 ${loads.length-failures}/${loads.length} 张${failures?' · 存在读取失败':' · 同步播放'}`;draw(true)});
</script></html>'''


def render_review_board(manifest: dict, timing: dict | None = None) -> str:
    timing = timing or load_run_timing()
    return (BOARD_HTML.replace('__MANIFEST__', json_for_html(manifest))
            .replace('__TIMING__', json_for_html(timing)).replace('__TIMELINE_JS__', TIMELINE_JS)
            .replace('__REVIEW_NOTICE__', review_notice(manifest, timing)))


def main() -> None:
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8-sig'))
    output = ROOT / 'preview/all-directions.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_review_board(manifest), encoding='utf-8')
    print('preview/all-directions.html')


if __name__ == '__main__':
    main()
