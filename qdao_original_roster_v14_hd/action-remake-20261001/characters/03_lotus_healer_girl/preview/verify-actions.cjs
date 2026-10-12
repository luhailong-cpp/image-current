'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const B=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(B,p),'utf8').replace(/^\uFEFF/,'')),T=require('./timing.js');
let checks=0;function check(ok,label){checks++;if(!ok)throw Error(label);}
const overview=read('review/all-actions-selection.json');
for(const g of overview.groups){
 const ds=T.durations(g.action,g.frames);
 if(g.action==='run'){
  check(g.expected===16&&ds.length===16,'run16 '+g.direction);check(ds.every(n=>n===60)&&T.total(ds)===960,'run960 '+g.direction);
  for(let i=0;i<16;i++){check(T.frameAt(i*60,ds)===i,'frame start');check(T.frameAt((i+1)*60-.001,ds)===i,'frame end');}
  check(T.frameAt(960,ds)===0,'wrap no pause');check(T.frameAt(959.999,ds)===15,'last frame retained');
  for(const f of g.frames.filter(f=>f.file))check(f.durationMs===60,'manifest frame60');
 }else if(g.present===g.expected){check(T.total(ds)==={hit:240,attack:360,cast:720}[g.action],'combat duration preserved');}
}
for(const name of ['actions.js','timing.js'])new vm.Script(fs.readFileSync(path.join(__dirname,name),'utf8'));
const html=fs.readFileSync(path.join(__dirname,'actions.html'),'utf8');
check(!/<option[^>]+value="(?:480|640|720|800)"/.test(html),'old fast options removed');
check(html.includes('960ms')&&html.includes('60ms'),'visible normal timing');
for(const name of ['index.html','new-run.html'])check(fs.readFileSync(path.join(__dirname,name),'utf8').includes('url=actions.html'),'current entry '+name);
const report={checkedAt:new Date().toISOString(),result:'pass',checks,run:{cycleMs:960,frameMs:60,count:16,uniform:true},combatCyclesMs:{hit:240,attack:360,cast:720},tested:['all14group timings','every run frame boundary','16-to-01 wrap without extra hold','old entry redirects','source syntax'],visualAcceptance:false,clientAcceptance:false,overviewSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(B,'review/all-actions-selection.json'))).digest('hex')};
fs.writeFileSync(path.join(B,'review/preview-technical-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
