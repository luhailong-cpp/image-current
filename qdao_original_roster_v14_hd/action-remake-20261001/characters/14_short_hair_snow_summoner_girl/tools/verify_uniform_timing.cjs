const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const R=path.resolve(__dirname,'..'),manifest=JSON.parse(fs.readFileSync(path.join(R,'manifest.json'),'utf8'));
const source=fs.readFileSync(path.join(R,'tools/preview_template.html'),'utf8');
const body=source.slice(source.indexOf('function frameAt(t)'),source.indexOf('function show()'));
const results=[];
for(const d of ['N','NE','E','SE','S','SW','W','NW']){
 const group=manifest.frames.filter(f=>f.action==='run'&&f.direction===d);assert.equal(group.length,16);assert(group.every(f=>f.durationMs===60));
 const ctx=vm.createContext({group,starts:group.map((_,i)=>i*60),cycleMs:960});vm.runInContext(body,ctx);
 for(let i=0;i<16;i++){assert.equal(vm.runInContext('frameAt('+i*60+')',ctx),i);assert.equal(vm.runInContext('frameAt('+(i*60+59.999)+')',ctx),i);}
 assert.equal(vm.runInContext('frameAt(960)',ctx),0);assert.equal(vm.runInContext('frameAt(1920)',ctx),0);assert.equal(vm.runInContext('frameAt(959.999)',ctx),15);
 results.push({direction:d,cycleMs:960,durationMs:60,frameCount:16,boundaryChecks:35,status:'passed'});
}
for(const [action,ms,count] of [['hit',40,6],['attack',30,12],['cast',45,16]])for(const d of ['E','W']){const g=manifest.frames.filter(f=>f.action===action&&f.direction===d);assert.equal(g.length,count);assert(g.every(f=>f.durationMs===ms));}
for(const name of ['tools/timing_template.html','timing-grounding.html','bamboo-reference.html','all-directions.html','index.html']){
 const html=fs.readFileSync(path.join(R,name),'utf8'),js=html.match(/<script>([\s\S]*?)<\/script>/)[1];new vm.Script(js);assert(!/cycles=\[480,640,720,800\]|value="(?:480|640|720|800)"/.test(html));
}
const report={recordedAt:new Date().toISOString(),status:'passed',scope:'Controlled source-function boundary tests, syntax and configured timing; not browser hardware FPS measurement',directions:results,combatTimingUnchanged:true,oldFastOptionsRemoved:true,clientValidated:false};
fs.writeFileSync(path.join(R,'audit/uniform-timing-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
