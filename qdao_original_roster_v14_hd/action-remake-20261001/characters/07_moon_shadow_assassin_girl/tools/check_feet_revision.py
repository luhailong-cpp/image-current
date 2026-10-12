"""Validate revision scope, rendered data, and all preview frame durations."""
import hashlib, json, re, subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
load=lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m=load(R/'manifest.json'); before=load(R/'review/feet-direction-20261003/before-manifest.json')
old={f['id']:f for f in before['frames']}
targets={f'attack_E_{i:02}' for i in range(1,9)}|{f'run_SW_{i:02}' for i in (5,7,13)}
assert m['timing']['runCycleMs']==800, 'Run cycle must be800ms in current revision'
changed={f['id'] for f in m['frames'] if f['sha256']!=old[f['id']]['sha256']}
assert changed==targets, ('Unexpected changed frames',changed^targets)
assert len(m['frames'])==196 and len({f['sha256'] for f in m['frames']})==196
for f in m['frames']:
    assert sha(R/f['path'])==f['sha256']
    if f['action']!='run': assert f['durationMs']==old[f['id']]['durationMs']
    im=Image.open(R/f['path']); im.load(); assert im.size==(1024,1024) and im.mode=='RGBA'
    alpha=im.getchannel('A')
    for edge in ((0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)):
        assert alpha.crop(edge).getextrema()[1]<=8, f['id']
html=(R/'preview/index.html').read_text(encoding='utf-8')
embedded=json.loads(re.search(r'<script id="manifest" type="application/json">(.*?)</script>',html,re.S)[1])
assert embedded=={**m,'previewSkipped':[]}, 'Browser embedded manifest is stale'
for a in load(R/'preview/derivations.json')['artifacts']:
    assert sha(R/a['path'])==a['sha256']
    assert all(sha(R/s['path'])==s['sha256'] for s in a['sources'])
    if 'durationsMs' in a:
        im=Image.open(R/a['path']); assert im.n_frames==len(a['durationsMs'])
        for i,expected in enumerate(a['durationsMs']):
            im.seek(i); assert abs(im.info['duration']-expected)<.01
function=re.search(r'(function frameDuration\(f\).*?)\nfunction tick',html,re.S)[1]
js="""const m=DATA; const source=SOURCE;
const run=new Function('m','specs','$','frames','at','f','return ('+source+')(f)');
const specs={run:{ms:30},hit:{ms:40},attack:{ms:30},cast:{ms:45}};
const groups=Object.groupBy(m.frames,f=>f.action+'/'+f.direction);
for(const frames of Object.values(groups)){
 frames.sort((a,b)=>a.index-b.index);
 for(const mode of ['manifest','previous720','640','720','800','480']){
  for(const weighted of [false,true]){
   const $=id=>id==='runTiming'?{value:mode}:{checked:weighted};
   const durations=frames.map((f,i)=>run(m,specs,$,frames,i,f));
   const isRun=frames[0].action==='run';
   const sum=durations.reduce((a,b)=>a+b,0);
   const expected=!isRun?frames.reduce((s,f)=>s+f.durationMs,0):mode==='manifest'?800:mode==='previous720'?720:Number(mode);
   if(Math.abs(sum-expected)>.001||durations.some(x=>!Number.isFinite(x)||x<=0))throw Error('Wrong control timing '+mode);
  }
 }
}
console.log('Browser timing function: all14 groups and6 modes checked');
""".replace('DATA',json.dumps(m)).replace('SOURCE',json.dumps(function))
path=R/'review/feet-direction-20261003/check-preview-timing.cjs'; path.write_text(js,encoding='utf-8')
subprocess.run(['node',str(path)],check=True)
print(json.dumps({'frames':196,'replaced':len(changed),'unchanged':196-len(changed),'runCycleMs':800,'htmlManifestCurrent':True,'allPreviewHashesAndDurations':True}))
