(()=>{
'use strict';
const data=window.ALL_SEQUENCES, $=id=>document.getElementById(id);
const ctx=$('canvas').getContext('2d'), names={run:'跑步',hit:'受击',attack:'普攻',cast:'施法'},directions={S:'南',SE:'东南',E:'东',NE:'东北',N:'北',NW:'西北',W:'西',SW:'西南'};
let sequence,images=[],index=0,elapsed=0,playing=true,last=0,request=0;
$('summary').textContent='已落盘 '+data.presentFrameCount+' / '+data.targetFrameCount+' 帧；完整序列 '+data.completeSequences+' / '+data.sequenceCount+'。';
function draw(){
 const size=Number($('size').value),canvas=$('canvas');
 if(canvas.width!==size){canvas.width=size;canvas.height=size}
 ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,size,size);ctx.setTransform(size/1024,0,0,size/1024,0,0);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';if(images[index])ctx.drawImage(images[index],0,0,1024,1024);
 if(!sequence)return;
 $('info').textContent=(index+1)+' / '+sequence.expectedFrames+' · '+sequence.frameMs+' ms/帧 · '+sequence.cycleMs+' ms/圈';
 const f=sequence.frames[index];$('source').textContent=f?f.path:'';
}
function pause(){playing=false;$('play').textContent='播放'}
async function select(s){
 const own=++request;sequence=s;for(const old of images)old?.close?.();images=[];index=0;elapsed=0;pause();draw();
 $('play').disabled=true;$('prev').disabled=true;$('next').disabled=true;
 document.querySelectorAll('#sequences button').forEach(b=>b.classList.toggle('active',b.dataset.key===s.action+'/'+s.direction));
 $('status').textContent=names[s.action]+' · '+directions[s.direction]+'：正在加载';
 $('record').textContent=JSON.stringify(s,null,2);
 const loaded=await Promise.all(s.frames.map(f=>new Promise(resolve=>{const im=new Image;im.onload=async()=>{try{await im.decode();resolve(await createImageBitmap(im,{resizeWidth:512,resizeHeight:512,resizeQuality:'high'}))}catch{resolve(null)}};im.onerror=()=>resolve(null);im.src='../'+f.path+'?sha='+f.sha256})));
 if(own!==request){for(const item of loaded)item?.close?.();return}images=loaded;
 const ok=s.complete&&loaded.every(Boolean);
 $('play').disabled=!ok;$('prev').disabled=!ok;$('next').disabled=!ok;
 $('status').textContent=ok?'完整序列已加载。画面与接地以播放检查为准。':'序列尚未齐全，暂不播放缺帧动作。';
 if(ok){playing=true;$('play').textContent='暂停'}draw();
}
for(const s of data.sequences){const b=document.createElement('button');b.textContent=names[s.action]+' '+directions[s.direction]+' '+s.presentFrames+'/'+s.expectedFrames;b.dataset.key=s.action+'/'+s.direction;b.disabled=s.presentFrames===0;b.onclick=()=>select(s);$('sequences').appendChild(b)}
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'暂停':'播放';elapsed=0};
function step(delta){if(!sequence?.complete||!images.length||!images.every(Boolean))return;pause();index=(index+delta+images.length)%images.length;elapsed=0;draw()}
$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);
$('size').onchange=()=>{$('canvas').style.width=$('size').value+'px';$('canvas').style.height=$('size').value+'px';draw()};
 $('rate').onchange=()=>{elapsed=0};
function tick(now){const dt=last?Math.min(now-last,250):0;last=now;if(playing&&sequence?.complete&&images.length){elapsed+=dt*Number($('rate').value);let changed=false;while(elapsed>=sequence.frameMs){elapsed-=sequence.frameMs;index=(index+1)%images.length;changed=true}if(changed)draw()}requestAnimationFrame(tick)}
const first=data.sequences.find(s=>s.complete)||data.sequences.find(s=>s.presentFrames);if(first)select(first);
window.animationReview={getState:()=>({action:sequence?.action,direction:sequence?.direction,index,playing,loaded:images.filter(Boolean).length,rate:Number($('rate').value)}),select:(action,direction)=>select(data.sequences.find(s=>s.action===action&&s.direction===direction)),step};
requestAnimationFrame(tick);
})();
