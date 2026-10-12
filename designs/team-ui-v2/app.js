"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const portraits = ["hero-headband", "29_he_xiangu", "24_lu_dongbin", "lotus-healer", "27_ink_kite_ranger"];
  const initialMembers = [
    {id:1,name:"青云小道",level:28,school:"道童",online:true,portrait:portraits[0]},
    {id:2,name:"清铃",level:26,school:"灵修",online:true,portrait:portraits[1]},
    {id:3,name:"长风",level:30,school:"剑修",online:false,portrait:portraits[2]}
  ];
  const initialApplications = [
    {id:4,name:"桂枝",level:27,school:"医师",online:true,portrait:portraits[3]},
    {id:5,name:"云游子",level:29,school:"符师",online:true,portrait:portraits[4]}
  ];
  let state, actionTimer;
  function reset(scenario = "leader") {
    clearTimeout(actionTimer);
    state = {members:structuredClone(initialMembers),applications:structuredClone(initialApplications),capacity:5,localId:1,leaderId:1,available:true,busy:false,status:"",memberPage:0,applicationPage:0,scenario};
    if (scenario === "member") state.localId = 2;
    if (scenario === "unavailable") state.available = false;
    if (scenario === "full") state.members.push(...initialApplications.map((r,i)=>({...r,id:20+i,name:["望舒","松风"][i]})));
    if (scenario === "pagination") {
      state.capacity = 8;
      state.members.push(...Array.from({length:3},(_,i)=>({...initialApplications[i%2],id:20+i,name:["望舒","松风","听雨"][i]})));
      state.applications.push(...Array.from({length:5},(_,i)=>({...initialApplications[i%2],id:30+i,name:["玄青","疏影","云归","竹隐","半夏"][i]})));
    }
    render();
  }
  const isLeader = () => state.localId === state.leaderId;
  const isFull = () => state.members.length >= state.capacity;
  const canAct = () => state.available && !state.busy;
  const esc = value => String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const avatar = role => `<div class="avatar"><img src="assets/${esc(role.portrait)}.png" alt="" draggable="false"></div>`;
  function reason() {
    if (!state.available) return "组队服务尚未连接，连接后可刷新与处理申请。";
    if (state.busy) return state.status;
    if (isFull()) return "队伍已满，可拒绝剩余申请。";
    if (!isLeader()) return "你是队员，入队申请由队长处理。";
    return state.status || "同意申请后，道友将加入你的队伍。";
  }
  function renderPagination(target,total,page,onChange) {
    target.hidden = total <= 1;
    if (total <= 1) {target.innerHTML="";return;}
    target.innerHTML=`<button type="button" aria-label="上一页" ${page===0?"disabled":""}>上一页</button><span>${page+1} / ${total}</span><button type="button" aria-label="下一页" ${page===total-1?"disabled":""}>下一页</button>`;
    const buttons=target.querySelectorAll("button");buttons[0].onclick=()=>onChange(page-1);buttons[1].onclick=()=>onChange(page+1);
  }
  function render() {
    const focused = document.activeElement?.id;
    $("summaryCount").innerHTML=`${state.members.length}<span> / ${state.capacity}</span>`;
    $("memberHeadingCount").textContent=`${state.members.length} / ${state.capacity}`;
    $("applicationCount").textContent=state.applications.length;
    $("identityBadge").textContent=isLeader()?"你是队长":"你是队员";
    const memberPages=Math.ceil(Math.max(state.capacity,state.members.length)/5);
    state.memberPage=Math.min(state.memberPage,memberPages-1);
    document.querySelector(".members-section").classList.toggle("has-pagination",memberPages>1);
    const start=state.memberPage*5;
    $("members").innerHTML=Array.from({length:Math.min(5,state.capacity-start)},(_,i)=>{
      const r=state.members[start+i];
      if (!r) return `<li class="member-row empty"><span class="empty-icon" aria-hidden="true">＋</span><span class="empty-name">空余席位</span><span class="empty-detail">席位 ${String(start+i+1).padStart(2,"0")}</span></li>`;
      const leader=r.id===state.leaderId,self=r.id===state.localId;
      return `<li class="member-row ${self?"is-self":""}">${avatar(r)}<div class="member-identity"><div class="name-line"><strong class="member-name">${esc(r.name)}</strong>${self?'<span class="self-tag">自己</span>':""}</div><div class="role-tag ${leader?"leader":""}">${leader?"队长":"队员"}</div></div><span class="member-level">${r.level} 级</span><span class="member-school">${esc(r.school)}</span><span class="online-state ${r.online?"":"offline"}">${r.online?"在线":"离线"}</span></li>`;
    }).join("");
    renderPagination($("memberPagination"),memberPages,state.memberPage,p=>{state.memberPage=p;render()});
    const pages=Math.max(1,Math.ceil(state.applications.length/4));
    state.applicationPage=Math.min(state.applicationPage,pages-1);
    document.querySelector(".applications-section").classList.toggle("has-pagination",state.applications.length>2);
    if (!state.applications.length) {
      $("applications").innerHTML='<div class="empty-applications"><div class="empty-emblem" aria-hidden="true">缘</div><h3>暂无入队申请</h3><p>收到新的申请后<br>道友资料会显示在这里</p></div>';
    } else {
      const allowed=canAct()&&isLeader();
      $("applications").innerHTML=state.applications.slice(state.applicationPage*4,state.applicationPage*4+4).map(r=>`<article class="application-card" aria-label="${esc(r.name)}的入队申请">${avatar(r)}<div><div class="application-name">${esc(r.name)}</div><div class="application-details"><span>${r.level} 级</span><span>${esc(r.school)}</span></div></div><div class="application-actions"><button id="reject-${r.id}" class="button secondary" type="button" data-decision="reject" data-player="${r.id}" aria-label="拒绝${esc(r.name)}的申请" ${allowed?"":"disabled"}>拒绝</button><button id="approve-${r.id}" class="button primary" type="button" data-decision="approve" data-player="${r.id}" aria-label="同意${esc(r.name)}的申请" ${allowed&&!isFull()?"":"disabled"}>同意</button></div></article>`).join("");
    }
    renderPagination($("applicationPagination"),pages,state.applicationPage,p=>{state.applicationPage=p;render()});
    $("applicationFootnote").hidden=!state.applications.length;
    $("statusMessage").textContent=reason();
    $("refresh").disabled=!canAct();$("refresh").textContent=state.busy?"同步中…":"刷新";
    document.querySelectorAll("[data-scenario]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.scenario===state.scenario)));
    if (focused && !document.getElementById(focused) && focused.match(/^(approve|reject)-/)) {
      const target=$("applications").querySelector("button:not(:disabled)")||$("refresh");
      target.focus({preventScroll:true});
    }
  }
  $("applications").addEventListener("click",e=>{
    const button=e.target.closest("[data-decision]");if(!button)return;
    const approve=button.dataset.decision==="approve",id=Number(button.dataset.player);
    if(!canAct()||!isLeader()||(approve&&isFull()))return;
    const role=state.applications.find(r=>r.id===id);if(!role)return;
    state.applications=state.applications.filter(r=>r.id!==id);
    if(approve)state.members.push({...role});
    state.status=approve?`${role.name}已加入队伍。`:`已拒绝${role.name}的申请。`;
    render();
  });
  $("refresh").onclick=()=>{
    if(!canAct())return;state.busy=true;state.status="正在刷新组队信息…";render();
    actionTimer=setTimeout(()=>{state.busy=false;state.status="队伍信息已刷新。";render()},650);
  };
  document.querySelectorAll("[data-scenario]").forEach(b=>b.onclick=()=>reset(b.dataset.scenario));
  $("resetDemo").onclick=()=>reset();
  function showPanel(show){$("teamPanel").hidden=!show;$("reopen").hidden=show;(show?$("closePanel"):$("openPanel")).focus()}
  $("closePanel").onclick=()=>showPanel(false);$("openPanel").onclick=()=>showPanel(true);
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!$("teamPanel").hidden&&!$("demoControls").contains(document.activeElement))showPanel(false)});
  function fit(){if(innerWidth<=900){$("stage").style.transform="none";return;}const scale=Math.min(innerWidth/2560,innerHeight/1080);$("stage").style.transform=`translate(-50%,-50%) scale(${scale})`}
  addEventListener("resize",fit);reset();fit();
})();
