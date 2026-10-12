"""Read current manifest-bound reference assets without altering either character."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT.parent / '09_bamboo_archer_girl'
OUT = ROOT / 'review/bamboo-reference'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    boy = read(ROOT / 'manifest.json')
    bamboo = read(REFERENCE / 'manifest.json')
    reference_timing = read(REFERENCE / 'animation-timing.json')
    current_timing = read(ROOT / 'run-timing.json')
    mismatches = []
    for seq in bamboo['sequences']:
        for row in seq['frames']:
            path = REFERENCE / row['file']
            actual = sha(path) if path.is_file() else None
            if actual != row['sha256']:
                mismatches.append({'file': row['file'], 'manifestSha256': row['sha256'], 'actualSha256': actual})
    if mismatches:
        context = {'atUtc': datetime.now(timezone.utc).isoformat(),
                   'status': 'reference_snapshot_changed_comparison_unavailable',
                   'reference': REFERENCE.as_posix(), 'referenceModifiedByThisTask': False,
                   'manifestSha256': {'boy': sha(ROOT / 'manifest.json'), 'bamboo': sha(REFERENCE / 'manifest.json')},
                   'mismatches': mismatches, 'hashesVerified': False, 'dynamicVisualPlaybackVerified': False,
                   'currentBoyPreview': '../index.html'}
        (OUT / 'context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (OUT / 'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>参照文件已更新</title><h1>参照文件已更新</h1><p>只读参照角色的图片与其清单暂不一致，对照页暂停展示旧记录。道童当前素材不受影响。</p><p><a href="../index.html">打开道童当前全部动作预览</a></p></html>', encoding='utf-8')
        print(json.dumps({'comparisonAvailable': False, 'referenceMismatches': len(mismatches), 'boyDeliveryChanged': False}))
        return
    groups = {}
    for row in boy['frames']:
        _, action, direction, name = row['file'].split('/')
        key = f'{action}/{direction}'
        assert sha(ROOT / row['file']) == row['sha256'], row['file']
        groups.setdefault(key, {'boy': [], 'bamboo': []})['boy'].append({
            'frame': int(name[:2]), 'url': '../../' + row['file'],
            'file': row['file'], 'sha256': row['sha256'], 'ms': row['frameDurationMs']})
    for seq in bamboo['sequences']:
        key = f"{seq['action']}/{seq['direction']}"
        if key not in groups:
            continue
        for row in seq['frames']:
            assert sha(REFERENCE / row['file']) == row['sha256'], row['file']
            groups[key]['bamboo'].append({
                'frame': row['frame'], 'url': '../../../09_bamboo_archer_girl/' + row['file'],
                'file': row['file'], 'sha256': row['sha256'], 'sourceMs': seq['ms'],
                'ms': current_timing['frameDurationMs'] if seq['action'] == 'run' else seq['ms']})
    for key, value in groups.items():
        for actor in ('boy', 'bamboo'):
            value[actor].sort(key=lambda row: row['frame'])
            expected = {'run': 16, 'hit': 6, 'attack': 12, 'cast': 16}[key.split('/')[0]]
            assert [r['frame'] for r in value[actor]] == list(range(1, expected + 1))
            assert all(r['ms'] > 0 for r in value[actor])
        value['cycleMs'] = {actor: sum(r['ms'] for r in value[actor]) for actor in ('boy', 'bamboo')}
    client = Path('D:/work/mmorpg-client')
    client_evidence = []
    for rel in ('Assets/Scripts/World/QdaoCharacterCatalog.cs', 'Assets/Scripts/World/QdaoBoySpriteAnimator.cs'):
        p = client / rel
        if p.exists():
            matched = [{'line': n, 'text': line.strip()} for n, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(), 1)
                       if re.search(r'FrameDurationMs =>|cycle_duration_ms == 480|cycleDurationMs != 480|FramesPerUnit =>|distance \* _frames.FramesPerUnit', line)]
            client_evidence.append({'file': p.as_posix(), 'sha256': sha(p), 'matches': matched})
    context = {
        'atUtc': datetime.now(timezone.utc).isoformat(),
        'reference': REFERENCE.as_posix(),
        'referenceStatus': 'user_confirmed_current_bamboo_girl_reference',
        'authorization': 'User asked other character windows to refer to current bamboo girl; conveyed by task message.',
        'scope': 'Same-direction comparison; different frame numbers can represent different phases. No reference pixels, identities or weapons are copied.',
        'manifestSha256': {'boy': sha(ROOT / 'manifest.json'), 'bamboo': sha(REFERENCE / 'manifest.json')},
        'referenceTiming': reference_timing,
        'referenceRunPlaybackOverride': {'frameMs': current_timing['frameDurationMs'], 'cycleMs': current_timing['cycleDurationMs'], 'reason': 'Latest user asks uniform 60ms x 16; display timing only. Read-only reference files are unchanged; sourceMs preserves their manifest values.'},
        'groups': groups,
        'client': {'pathExists': client.exists(), 'modified': False, 'executed': False, 'evidence': client_evidence},
        'dynamicVisualPlaybackVerified': False,
        'limits': 'Local browser navigation was previously denied. This comparison page and hash checks are not evidence of dynamic playback acceptance.'
    }
    (OUT / 'context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>道童与竹弓少女动作对照</title><style>
body{font:16px system-ui;margin:24px;background:#eeeae0;color:#253d34}main{max-width:1040px;margin:auto}h1{font-size:24px}p{line-height:1.6}button,select{font:inherit;padding:7px;margin:3px}section{display:flex;flex-wrap:wrap;gap:24px}.actor{flex:1;min-width:270px}img{display:block;width:min(100%,400px);background:#f8f6ee;border:1px solid #ccc5b3}small{display:block;color:#57655d}.controls{margin:14px 0}
</style><main><h1>道童与竹弓少女 · 同方向对照</h1>
<p>竹弓少女为用户最新确认的参照。道童保留自身外形、左手葫芦与空右手。本页双方跑步均按960ms一圈、每帧60ms播放；参照文件仅读。同号帧不一定同相位，可暂停后分别逐帧查看。</p>
<div class="controls"><select id="sequence"></select><button id="toggle">暂停</button><select id="speed"><option value="1">正常速度</option><option value="0.25">¼ 慢速</option></select><button id="restart">从头播放</button></div>
<section><div class="actor"><h2>道童</h2><img id="boy" alt="道童当前动作帧"><p id="boyInfo"></p><button data-actor="boy" data-step="-1">上一帧</button><button data-actor="boy" data-step="1">下一帧</button></div>
<div class="actor"><h2>竹弓少女 · 只读参照</h2><img id="bamboo" alt="竹弓少女当前动作帧"><p id="bambooInfo"></p><button data-actor="bamboo" data-step="-1">上一帧</button><button data-actor="bamboo" data-step="1">下一帧</button></div></section>
<p id="duration"></p><small>这是当前文件的对照入口。页面、编码与静态核查不等于已通过动态接地或客户端验收。没有对人物做逐帧缩放、贴地或相位对齐。</small></main>
<script>const groups=DATA;const sequence=document.querySelector('#sequence');
const actors=['boy','bamboo'];let positions={boy:0,bamboo:0},elapsed={boy:0,bamboo:0},playing=true,last=null;
for(const key of Object.keys(groups)){const option=document.createElement('option');option.value=key;option.textContent=key;sequence.append(option)}sequence.value='run/E';
function draw(){const group=groups[sequence.value];for(const actor of actors){const row=group[actor][positions[actor]];document.getElementById(actor).src=row.url;document.getElementById(actor+'Info').textContent=`第 ${row.frame} 帧 / ${group[actor].length} · ${row.ms} ms`;}document.querySelector('#duration').textContent=`道童 ${group.cycleMs.boy} ms / 圈；竹弓少女 ${group.cycleMs.bamboo} ms / 圈`;}
function reset(){positions={boy:0,bamboo:0};elapsed={boy:0,bamboo:0};last=null;draw();}
function pause(){playing=false;document.querySelector('#toggle').textContent='播放';}
sequence.onchange=reset;document.querySelector('#restart').onclick=()=>{reset();playing=true;document.querySelector('#toggle').textContent='暂停'};
document.querySelector('#toggle').onclick=()=>{playing=!playing;last=null;document.querySelector('#toggle').textContent=playing?'暂停':'播放'};
for(const button of document.querySelectorAll('[data-actor]'))button.onclick=()=>{pause();const actor=button.dataset.actor;const rows=groups[sequence.value][actor];positions[actor]=(positions[actor]+Number(button.dataset.step)+rows.length)%rows.length;elapsed[actor]=0;draw()};
function tick(now){if(last!==null&&playing){const delta=(now-last)*Number(document.querySelector('#speed').value);const group=groups[sequence.value];for(const actor of actors){const rows=group[actor];elapsed[actor]+=delta;elapsed[actor]%=group.cycleMs[actor];while(elapsed[actor]>=rows[positions[actor]].ms){elapsed[actor]-=rows[positions[actor]].ms;positions[actor]=(positions[actor]+1)%rows.length;}}draw()}last=now;requestAnimationFrame(tick)}
reset();requestAnimationFrame(tick);</script></html>'''.replace('DATA', json.dumps(groups, ensure_ascii=False))
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    print(json.dumps({'groups': len(groups), 'boyFrames': sum(len(g['boy']) for g in groups.values()), 'referenceFrames': sum(len(g['bamboo']) for g in groups.values()), 'clientExists': client.exists(), 'hashesVerified': True}))


if __name__ == '__main__':
    main()
