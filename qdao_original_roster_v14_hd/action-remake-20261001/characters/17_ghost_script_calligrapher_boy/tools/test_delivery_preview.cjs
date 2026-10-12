// Execute the real delivery viewer JS against the current 196-slot preview fixture.
// No runtime export, source PNG changes, browser, or network is required.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const base=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(__dirname,'build_delivery_preview.py'),'utf8');
const html=source.match(/HTML=r"""([\s\S]*?)"""/)[1];
const code=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)]
  .filter(m=>!m[1].includes('application/json')).map(m=>m[2]).join('\n');
const manifest=JSON.parse(fs.readFileSync(path.join(base,'preview/manifest-preview.json'),'utf8'));
const sequences=[];
for(const [action,settings] of Object.entries(manifest.actions)){
  for(const direction of settings.directions){
    const slots=manifest.slots.filter(s=>s.action===action&&s.direction===direction).sort((a,b)=>a.frame-b.frame);
    assert.strictEqual(slots.length,settings.count);
    assert(slots.every(s=>s.selected));
    const frames=slots.map(s=>({src:'../runtime/'+action+'/'+direction+'/'+String(s.frame).padStart(2,'0')+'.png',
      frame:s.frame,duration:s.duration_ms,sha256:s.selected.sha256}));
    sequences.push({action,direction,frames,ms:settings.duration_ms,cycle:frames.length*settings.duration_ms});
  }
}
assert.strictEqual(sequences.reduce((n,s)=>n+s.frames.length,0),196);
const ids=new Map(),listeners=new Map(),pending=[];
let now=5000,held=false,rafId=0;
const rafs=new Map();
class Element{
  constructor(tag='DIV'){this.tagName=tag;this.value='';this.textContent='';this.children=[];this.disabled=false;
    const classes=new Set();this.classList={toggle(name,on){if(on)classes.add(name);else classes.delete(name);},contains:name=>classes.has(name)};}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  removeAttribute(name){delete this[name];}
  click(){if(!this.disabled&&this.onclick)this.onclick();}
}
class FakeImage extends Element{
  constructor(){super('IMG');}
  decode(){if(!held)return Promise.resolve();return new Promise((resolve,reject)=>pending.push({src:this.src,resolve,reject}));}
  cloneNode(){const copy=new FakeImage();copy.src=this.src;return copy;}
}
const get=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
get('data').textContent=JSON.stringify({character:manifest.character,status:'candidate',sequences});
get('action').value='run';get('speed').value='1';get('direction').value='';
const context=vm.createContext({
  document:{getElementById:get,createElement:tag=>new Element(tag.toUpperCase()),createTextNode:text=>({textContent:text}),
    addEventListener:(name,fn)=>listeners.set(name,fn),hidden:false},
  Image:FakeImage,Option:function(text,value){this.text=text;this.value=value;},
  performance:{now:()=>now},requestAnimationFrame:fn=>{rafs.set(++rafId,fn);return rafId;},
  cancelAnimationFrame:id=>rafs.delete(id),console
});
new vm.Script(code,{filename:'delivery-inline.js'}).runInContext(context);
const evaluate=expression=>vm.runInContext(expression,context);
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
const advance=(time,rafTimestamp=time)=>{now=time;const work=[...rafs.values()];rafs.clear();for(const fn of work)fn(rafTimestamp);};
const select=async(action,direction)=>{
  get('action').value=action;get('action').onchange();
  if(get('direction').value!==direction){get('direction').value=direction;get('direction').onchange();}
  await flush();
};
const settle=(suffix,error)=>{
  for(let i=pending.length-1;i>=0;i--)if(pending[i].src.includes(suffix)){
    const job=pending.splice(i,1)[0];error?job.reject(new Error(error)):job.resolve();
  }
};
const assertFrame=(n,seq)=>{
  assert.strictEqual(evaluate('index'),n);
  assert.strictEqual(get('sprite').src,seq.frames[n].src);
  assert.strictEqual(Number(get('seek').value),n+1);
  assert(get('film').children[n].classList.contains('active'));
};
const checks=[];
(async()=>{
  await flush();
  for(const seq of sequences){
    await select(seq.action,seq.direction);
    get('speed').value='1';get('speed').onchange();
    assert.strictEqual(get('film').children.length,seq.frames.length);
    const start=now;
    get('play').click();
    // RAF timestamps can precede the performance.now() value recorded by play().
    advance(start,0);assertFrame(0,seq);
    advance(start+seq.ms-0.001,-100);assertFrame(0,seq);
    for(let i=1;i<=seq.frames.length;i++){
      advance(start+i*seq.ms,0);assertFrame(i%seq.frames.length,seq);
    }
    get('play').click();
    assert.strictEqual(evaluate('playing'),false);
    checks.push({action:seq.action,direction:seq.direction,frameMs:seq.ms,cycleMs:seq.cycle});
  }
  assert(sequences.filter(s=>s.action==='run').every(s=>s.ms===75&&s.cycle===1200));
  assert(sequences.filter(s=>s.action!=='run').every(s=>s.ms==={hit:40,attack:30,cast:45}[s.action]));
  await select('run','E');const run=sequences.find(s=>s.action==='run'&&s.direction==='E');
  evaluate('step(0)');get('play').click();const pauseStart=now;
  advance(pauseStart+125);assertFrame(1,run);get('play').click();
  now+=1000;assertFrame(1,run);
  get('play').click();advance(now+50);assertFrame(2,run);get('play').click();
  checks.push({check:'pause/resume preserves fractional frame offset',passed:true});
  evaluate('step(0)');get('play').click();const speedStart=now;
  advance(speedStart+125);assertFrame(1,run);
  get('speed').value='0.25';get('speed').onchange();
  advance(speedStart+325);assertFrame(2,run);get('play').click();
  assert.strictEqual(evaluate('baseMs'),175);
  checks.push({check:'1x to 0.25x preserves exact offset using previous rate',passed:true});
  get('prev').click();assertFrame(1,run);evaluate('step(0)');
  get('prev').click();assertFrame(15,run);get('next').click();assertFrame(0,run);
  get('seek').value='16';get('seek').oninput();assertFrame(15,run);
  get('film').children[8].click();assertFrame(8,run);
  get('restart').click();assertFrame(0,run);get('play').click();
  checks.push({check:'prev/next wrap, seek, filmstrip and restart are immediately consistent',passed:true});
  await select('attack','W');evaluate('step(5)');assert.strictEqual(get('phase').textContent,'普攻接触帧');
  await select('cast','W');evaluate('step(9)');assert.strictEqual(get('phase').textContent,'施法释放帧');
  checks.push({check:'combat event frame labels 06 and 10',passed:true});
  held=true;
  get('direction').value='E';get('direction').onchange();
  assert(get('prev').disabled&&get('next').disabled&&get('seek').disabled&&get('restart').disabled);
  assert.strictEqual(get('sprite').src,undefined);
  assert.doesNotThrow(()=>evaluate('step(0);step(-1);play()'));
  get('action').value='run';get('action').onchange();
  get('direction').value='NE';get('direction').onchange();
  settle('/run/NE/');await flush();
  const ne=sequences.find(s=>s.action==='run'&&s.direction==='NE');
  assertFrame(0,ne);assert.strictEqual(get('title').textContent,'跑步 · NE');
  settle('/cast/E/','old request failed');settle('/run/E/');
  await flush();assertFrame(0,ne);assert.strictEqual(get('status').textContent,'16张素材已加载');
  checks.push({check:'fast action/direction switches ignore stale success and stale failure',passed:true});
  get('direction').value='W';get('direction').onchange();settle('/run/W/','current request failed');await flush();
  assert.strictEqual(get('status').textContent,'加载失败：current request failed');
  assert(get('play').disabled&&get('next').disabled);
  held=false;get('direction').onchange();await flush();
  assertFrame(0,sequences.find(s=>s.action==='run'&&s.direction==='W'));
  get('play').click();context.document.hidden=true;listeners.get('visibilitychange')();
  assert.strictEqual(evaluate('playing'),false);
  checks.push({check:'current load failure remains safe, retry works, hidden page pauses',passed:true});
  get('direction').value='INVALID';get('direction').onchange();await flush();
  assert.strictEqual(get('status').textContent,'未找到动作方向');
  assert.doesNotThrow(()=>evaluate('step(1);play();stop()'));
  const report={checkedAt:new Date().toISOString(),scope:'actual delivery inline JavaScript + current preview in-memory fixture',
    fixtureFrames:196,checks,firstRafTimestampSafe:true,formalBrowserAcceptance:false,sourceImagesChanged:false};
  fs.writeFileSync(path.join(base,'review/delivery-preview-code-verification.json'),JSON.stringify(report,null,2)+'\n');
  console.log('PASS: 14 sequences / 196 slots; 75ms run and 1200ms wrap; RAF epoch; pause/resume; speed; stepping; async switches and errors.');
})().catch(error=>{console.error(error);process.exitCode=1;});

