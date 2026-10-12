'use strict';
(() => {
const $ = id => document.getElementById(id);
const names = {run:'跑步',hit:'受击',attack:'普通攻击',cast:'释放技能'};
const ui = Object.fromEntries(['action','direction','play','prev','next','restart','rate','timing','size','ground','stage','title','seek','seek-label','phase','issues','load-status','frame-status','timing-status','root-status','source','overview-status','groups','reload'].map(id=>[id,$(id)]));
let overview, group, images=new Map(), failed=new Set(), generation=0, index=0, elapsed=0, playing=true, last=0;
const ctx=ui.stage.getContext('2d');
function durations(){
  if(!group) return [];
  return ActionTiming.durations(group.action,group.frames);
}
function validTiming(){const d=durations(); return d.length===group?.expected && d.every(v=>Number.isFinite(v)&&v>0);}
function cycle(){return validTiming()?durations().reduce((a,b)=>a+b,0):0;}
function reset(){index=0;elapsed=0;last=0;render();}
function selectAction(){
  const running=ui.action.value==='run';
  for(const o of ui.direction.options) o.disabled=!running&&!['E','W'].includes(o.value);
  if(!running&&!['E','W'].includes(ui.direction.value)) ui.direction.value='E';
  ui.timing.disabled=true;
  loadGroup();
}
async function loadGroup(){
  if(!overview)return;
  const token=++generation;
  group=overview.groups.find(g=>g.action===ui.action.value&&g.direction===ui.direction.value);
  images=new Map();failed=new Set();
  ui.seek.max=group.expected;reset();renderGroups();
  await Promise.allSettled(group.frames.filter(f=>f.file).map(async f=>{
    const img=new Image();
    img.src=new URL('../'+f.file,location.href).href+'?v='+f.sha256;
    try{await img.decode();if(token===generation)images.set(f.frame,img);}catch{if(token===generation)failed.add(f.frame);}
    if(token===generation)render();
  }));
}
function render(){
  if(!group)return;
  const f=group.frames[index], size=Number(ui.size.value), img=images.get(f.frame);
  if(ui.stage.width!==size){ui.stage.width=size;ui.stage.height=size;}
  ctx.clearRect(0,0,size,size);
  if(img)ctx.drawImage(img,0,0,size,size);
  else{ctx.fillStyle='#7b5546';ctx.textAlign='center';ctx.font='14px system-ui';ctx.fillText(f.file?(failed.has(f.frame)?'图片读取失败':'图片加载中'):'此帧尚未选入',size/2,size/2);}
  if(ui.ground.checked&&group.exportRoot&&group.exportCanvas){
    const [x,y]=group.exportRoot.map(v=>v*size/group.exportCanvas);
    ctx.save();ctx.strokeStyle='#9b6653';ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(size,y);ctx.stroke();ctx.setLineDash([]);ctx.beginPath();ctx.moveTo(x-4,y);ctx.lineTo(x+4,y);ctx.moveTo(x,y-4);ctx.lineTo(x,y+4);ctx.stroke();ctx.restore();
  }
  ui.title.textContent=names[group.action]+' · '+group.direction;
  ui.stage.setAttribute('aria-label',names[group.action]+' '+group.direction+' 第'+f.frame+'帧');
  ui.seek.value=f.frame;ui['seek-label'].textContent=String(f.frame).padStart(2,'0');
  ui['frame-status'].textContent=`${group.direction}${String(f.frame).padStart(2,'0')} / ${group.expected} · ${img?'已显示':f.file?'载入中':'缺帧'}`;
  ui.phase.textContent=f.observedPhase||'尚无本帧姿势记录。';
  ui.issues.replaceChildren();
  for(const issue of f.issues||[]){const p=document.createElement('p');p.textContent=issue;ui.issues.append(p);}
  if(!(f.issues||[]).length)ui.issues.textContent=f.file?'本帧暂无单独问题记录；仍需连播检查。':'等待实际图片和选帧记录。';
  ui['load-status'].textContent=`已解码 ${images.size}/${group.expected} · 已选图片 ${group.present}/${group.expected}`+(failed.size?` · 读取失败 ${failed.size}`:'');
  const ms=durations()[index], total=cycle(), rate=Number(ui.rate.value);
  ui['timing-status'].textContent=total?`${rate}× · 一圈 ${(total/rate).toFixed(0)}ms · 当前帧 ${(ms/rate).toFixed(1)}ms${group.action==='run'?' · 跑步试播值':' · 独立动作时长'}`:'此组时长记录尚未齐全，自动播放待补；可逐帧检查。';
  ui['root-status'].textContent=group.exportRoot?`统一画布 ${group.exportCanvas}px；固定参考点 [${group.exportRoot.map(v=>v.toFixed(2)).join(', ')}]。客户端尚未标定。`:'尚无该组固定画布参考。';
  ui.source.textContent=f.file?`${f.file} ← ${f.source}`:'尚无来源。';
  ui.play.textContent=playing?'暂停':'播放';
}
function renderGroups(){
  ui.groups.replaceChildren();
  for(const g of overview.groups){const b=document.createElement('button');b.className='group';b.type='button';b.setAttribute('aria-pressed',String(g===group));b.append(`${names[g.action]} · ${g.direction}`);const s=document.createElement('span');s.textContent=`${g.present}/${g.expected} 帧 · ${g.present?'待审':'待补'}`;b.append(s);b.onclick=()=>{ui.action.value=g.action;ui.direction.value=g.direction;selectAction();};ui.groups.append(b);}
}
async function reload(){
  ui.reload.disabled=true;
  try{const response=await fetch('../review/all-actions-selection.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);overview=await response.json();ui['overview-status'].textContent=`当前已导出 ${overview.selectedExported}/${overview.target} 帧。按竹弓少女及新增动作视频继续校正脚向、侧翻与前后帧衔接；跑步正常1×为960ms一圈。当前为素材预览，客户端尚未接入。`;await loadGroup();}
  catch(error){ui['overview-status'].textContent='无法读取动作清单：'+error.message;}
  finally{ui.reload.disabled=false;}
}
function step(delta){if(!group)return;playing=false;index=(index+delta+group.expected)%group.expected;elapsed=durations().slice(0,index).reduce((a,b)=>a+(b||0),0);last=0;render();}
ui.action.onchange=selectAction;ui.direction.onchange=loadGroup;
ui.play.onclick=()=>{playing=!playing;last=0;render();};ui.prev.onclick=()=>step(-1);ui.next.onclick=()=>step(1);
ui.restart.onclick=()=>{playing=true;reset();};ui.rate.onchange=()=>{last=0;render();};ui.timing.onchange=reset;
ui.size.onchange=render;ui.ground.onchange=render;ui.reload.onclick=reload;
ui.seek.oninput=()=>{const next=Number(ui.seek.value)-1;step(next-index);};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(document.activeElement?.tagName))return;if(e.code==='Space'){e.preventDefault();ui.play.click();}if(e.key==='ArrowLeft')step(-1);if(e.key==='ArrowRight')step(1);});
function tick(now){
  if(playing&&group&&validTiming()){
    if(last){elapsed=(elapsed+Math.min(now-last,250)*Number(ui.rate.value))%cycle();const next=ActionTiming.frameAt(elapsed,durations());if(index!==next){index=next;render();}}
  }
  last=now;requestAnimationFrame(tick);
}
reload();requestAnimationFrame(tick);
})();
