"""Check current960ms delivery, real APNG delays and actual player loop boundaries."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

R = Path(__file__).resolve().parents[1]
REV = R / 'review/direction-alignment-20261004'
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--allow-pending', action='store_true')
parser.add_argument('--revision', default='review/direction-alignment-20261004')
args = parser.parse_args()
REV = (R / args.revision).resolve()
assert REV.is_relative_to(R.resolve())
m = load(R / 'manifest.json')
before = load(REV / 'before-manifest.json')
old = {f['id']: f for f in before['frames']}
targets = set(load(REV / 'selection.json')['selected'])
changed = {f['id'] for f in m['frames'] if f['sha256'] != old[f['id']]['sha256']}
assert changed <= targets, changed - targets
if not args.allow_pending:
    assert m['formalAccepted'] and all(f['visualApproved'] for f in m['frames'])
    assert changed == targets
assert len(m['frames']) == 196 and len({f['sha256'] for f in m['frames']}) == 196
assert m['timing']['runCycleMs'] == 960 and m['timing']['runFrameMs'] == 60
assert m['timing']['E'] == [60] * 16 and m['timing']['otherRunDirections'] == [60] * 16
for f in m['frames']:
    assert sha(R / f['path']) == f['sha256'], f['id']
    assert f['durationMs'] == (60 if f['action'] == 'run' else old[f['id']]['durationMs'])
    with Image.open(R / f['path']) as im:
        assert im.size == (1024, 1024) and im.mode == 'RGBA'
        alpha = im.getchannel('A')
        assert all(alpha.crop(edge).getextrema()[1] <= 8 for edge in
                   ((0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)))
html = (R / 'preview/index.html').read_text(encoding='utf-8')
template = (R / 'tools/preview-template.html').read_text(encoding='utf-8')
embedded = json.loads(re.search(r'<script id="manifest" type="application/json">(.*?)</script>', html, re.S)[1])
assert embedded == {**m, 'previewSkipped': []}, 'Stale embedded manifest'
for content in (html, template):
    assert "url.searchParams.set('v',f.sha256)" in content, 'Frame cache version missing'
    assert 'id="weighted"' not in content
    assert '<select id="runTiming"' not in content
    assert all(f'value="{n}"' not in content for n in ('480','640','720','800','previous720'))
artifacts = load(R / 'preview/derivations.json')['artifacts']
assert len(artifacts) == 42
frame_by_path = {f['path']: f for f in m['frames']}
for a in artifacts:
    assert sha(R / a['path']) == a['sha256']
    assert all(sha(R / s['path']) == s['sha256'] for s in a['sources'])
    if 'durationsMs' in a:
        mult = 4 if a['path'].endswith('-slow.png') else 1
        expected = [frame_by_path[s['path']]['durationMs'] * mult for s in a['sources']]
        assert a['durationsMs'] == expected
        with Image.open(R / a['path']) as im:
            assert im.n_frames == len(expected)
            for i, duration in enumerate(expected):
                im.seek(i)
                assert abs(im.info['duration'] - duration) < .01

definitions = '\n'.join(re.search(pattern, html, re.S)[1] for pattern in (
    r'(function pause\(\).*?)\nfunction render',
    r'(function frameDuration\(f\).*?)\nfunction tick',
    r'(function tick\(\).*?)\nfunction startPlayback',
    r'(function startPlayback\(\).*?)\nfunction selectGroup',
))
script = re.search(r'<script>\s*(.*?)</script>', html, re.S)[1]
js = r"""const vm=require('node:vm');
const m=MANIFEST, definitions=DEFINITIONS;
new vm.Script(SCRIPT);
let cases=0;
for(const frames of Object.values(Object.groupBy(m.frames,f=>f.action+'/'+f.direction))){
 frames.sort((a,b)=>a.index-b.index);
 for(const speed of [1,.25])for(const loop of [false,true]){
  const seen=[],queue=[];let elapsed=0,nextId=1;
  const controls={loop:{checked:loop},speed:{value:String(speed)},play:{textContent:'播放',classList:{add(){},remove(){}}}};
  const ctx={frames,at:loop?0:7,playing:false,timer:null,specs:{run:{ms:60},hit:{ms:40},attack:{ms:30},cast:{ms:45}},
   $:id=>controls[id],setTimeout(fn,delay){const id=nextId++;queue.push({id,fn,delay});return id},
   clearTimeout(id){const i=queue.findIndex(t=>t.id===id);if(i>=0)queue.splice(i,1)},
   render(){seen.push({index:ctx.at,elapsed})}};
  vm.createContext(ctx);vm.runInContext(definitions,ctx);ctx.startPlayback();
  const n=frames.length*(loop?2:1);
  for(let i=0;i<n;i++){
   if(queue.length!==1)throw Error('Missing or duplicate timer');
   const t=queue.shift(),expected=frames[i%frames.length].durationMs/speed;
   if(t.delay!==expected)throw Error('Wrong frame delay');
   elapsed+=t.delay;t.fn();
  }
  const total=frames.reduce((s,f)=>s+f.durationMs,0)/speed*(loop?2:1);
  if(elapsed!==total)throw Error('Cycle duration mismatch');
  if(!loop&&(ctx.playing||queue.length||seen.length!==frames.length||ctx.at!==frames.length-1))throw Error('Single play skipped or held extra frame');
  if(loop&&(!ctx.playing||queue.length!==1||seen.length!==frames.length*2+1||ctx.at!==0))throw Error('Loop boundary failed');
  seen.forEach((s,i)=>{if(s.index!==i%frames.length)throw Error('Frame order or restart failed')});
  if(ctx.frameDuration({action:'run'})!==60)throw Error('Wrong run fallback');
  cases++;
 }
}
console.log(JSON.stringify({groups:14,cases,speeds:[1,.25],singleStartsAtZero:true,completeFrames:true,loopHasNoExtraWait:true,runCycleMs:960,runFrameMs:60}));
""".replace('MANIFEST', json.dumps(m)).replace('DEFINITIONS', json.dumps(definitions)).replace('SCRIPT', json.dumps(script))
js_path = REV / 'check-current-playback.cjs'
js_path.write_text(js, encoding='utf-8')
result = subprocess.run(['node', str(js_path)], check=True, capture_output=True, text=True)
playback = json.loads(result.stdout)
report = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'passed': True,
          'currentFrameCount': 196, 'pngChangedThisRevision': sorted(changed),
          'htmlCurrent': True, 'previewArtifactCount': 42, 'actualAPNGDurationsMatch': True,
          'fastOptionsRemoved': True, 'combatTimingUnchanged': True,
          'playback': playback, 'visualAcceptancePending': not m['formalAccepted'],
          'clientTested': False}
(REV / 'timing-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
