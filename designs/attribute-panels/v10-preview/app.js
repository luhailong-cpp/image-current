(function () {
  'use strict';
  const M = window.AttributeModel;
  const $ = (s) => document.querySelector(s);
  const statLabels = {hp:'气血',mp:'法力',patk:'物伤',matk:'法伤',speed:'速度',def:'防御'};
  const attrNotes = ['提升气血与防御','提升法力与法伤','提升物理伤害','提升出手速度'];
  const modes = {hero:'人物',pet:'宝宝'};
  let selectedPet = 'lingyue';
  let mode = new URLSearchParams(location.search).get('panel') === 'pet' ? 'pet' : 'hero';
  let battlePet = 'lingyue';
  let toastTimer;
  let dialogAction;
  const schemes = {hero:'strength',lingyue:'spirit',hutuantuan:'balanced',fuxiaohu:'strength',yunjiujiu:'speed'};
  const currentId = () => mode === 'hero' ? 'hero' : selectedPet;

  function fit() {
    const portrait = matchMedia('(max-width:950px)').matches;
    $('#stage').style.transform = portrait ? 'none' : `translate(-50%, -50%) scale(${Math.min(innerWidth/1600,innerHeight/675)})`;
  }
  addEventListener('resize', fit);
  function toast(message) {
    clearTimeout(toastTimer); $('#toast').textContent = message; $('#toast').classList.add('visible');
    toastTimer = setTimeout(() => $('#toast').classList.remove('visible'),2600);
  }
  function dialog(title, body, action) {
    $('#dialogTitle').textContent = title;
    $('#dialogBody').innerHTML = body;
    dialogAction = action || null;
    if (action) $('#dialogBody').insertAdjacentHTML('beforeend','<button type="button" class="button primary" id="dialogAction">确认返还</button>');
    $('#infoDialog').showModal();
    $('#dialogAction')?.addEventListener('click',() => { dialogAction(); $('#infoDialog').close(); $('#battle')?.focus(); });
  }
  function renderIdentity() {
    if(mode === 'hero') {
      const e=M.get('hero').entity;
      $('#identity').innerHTML=`<div class="identity-name"><h2>${e.name}</h2><p><span class="role-tag">道童</span>${e.level}级</p></div>`;
    } else {
      $('#identity').innerHTML=`<div class="pet-list-heading"><h2>我的宝宝</h2><span>携带 <b>4</b> / 8</span></div><div class="pet-list" aria-label="选择宝宝">${M.entities.filter(e=>e.kind==='pet').map(e=>`<button type="button" class="pet-card ${e.id===selectedPet?'active':''}" data-pet="${e.id}" aria-pressed="${e.id===selectedPet}"><div class="pet-avatar"><img src="assets/portrait_${e.id}.png" alt=""><small>${e.level}</small></div><div><strong>${e.name}</strong><p>${e.subtitle} · ${e.element}</p></div><span class="pet-status">${e.id===battlePet?'参<br>战':e.id===selectedPet?'已<br>选':'休<br>息'}</span></button>`).join('')}</div><div class="pet-list-foot"><span>与灵同行，山海不远</span><span>4 只灵宠</span></div>`;
    }
  }
  function renderExtra(e) {
    if(mode==='hero') {
      $('#entityExtra').innerHTML='<div class="meta-row"><span>五行属性</span><strong>金</strong></div><div class="meta-row"><span>修行方向</span><strong>物理输出</strong></div><p class="extra-note">炼体凝神，修己问道</p>';
    } else {
      $('#entityExtra').innerHTML=`<div class="meta-row"><span>培养方向</span><strong>${e.role}</strong></div><div class="pet-actions"><button type="button" class="small-action" id="wash">返还加点</button><button type="button" class="small-action" id="battle">${e.id===battlePet?'休息':'参战'}</button></div>`;
      $('#battle').addEventListener('click',()=>{battlePet=battlePet===e.id?null:e.id;renderIdentity();renderExtra(e);$('#battle').focus();toast(battlePet?`${e.name}已出战`:`${e.name}已休息`);});
      $('#wash').disabled=!M.get(e.id).saved.some(n=>n>0);
      $('#wash').addEventListener('click',()=>dialog('返还已加点数','<p>返还本次预览中已确认的属性点，同时撤销待确认的分配。</p><p>宝宝原有的基础属性保持不变。</p>',()=>{M.wash(e.id);renderNumbers();renderExtra(e);toast('已返还本次预览中确认的点数');}));
    }
  }
  function renderNumbers() {
    const s=M.get(currentId());
    $('#remaining').textContent=s.remaining;
    $('#pending').textContent=s.dirty?`待确认 ${s.draft.reduce((a,b)=>a+b,0)}`:s.remaining?'待分配':'已分配';
    $('#stats').innerHTML=M.statKeys.map(key=>`<div class="stat"><div class="stat-label">${statLabels[key]}</div><div class="stat-number"><span class="stat-value">${(s.stats[key]-s.delta[key]).toLocaleString('en-US')}</span>${s.delta[key]?`<span class="stat-delta">+${s.delta[key]}</span>`:''}</div></div>`).join('');
    M.attributes.forEach((label,i)=>{
      const value=$(`#attributeValue${i}`),range=$(`#range${i}`);
      value.textContent=s.values[i];
      range.min=s.entity.base[i]+s.saved[i];
      const rowAvailable=s.draft[i]+s.remaining;
      range.max=s.entity.base[i]+s.saved[i]+rowAvailable;
      range.value=s.values[i];
      range.setAttribute('aria-valuetext',`${label} ${s.values[i]}，本次增加 ${s.draft[i]}`);
      range.style.setProperty('--fill',`${rowAvailable ? s.draft[i]/rowAvailable*100 : 0}%`);
      range.disabled=rowAvailable===0;
      $(`[data-minus="${i}"]`).disabled=s.draft[i]===0;
      $(`[data-plus="${i}"]`).disabled=s.remaining===0;
    });
    $('#reset').disabled=!s.dirty;
    $('#confirm').disabled=!s.dirty;
    $('#auto').disabled=s.remaining===0;
    $('#allocationTip').textContent=s.dirty?'绿色数字为本次加点收益，确认后生效':s.remaining?'分配后点击确认，才会保存本次加点':'属性点已分配完毕，可继续查看其他属性';
  }
  function render() {
    const e=M.get(currentId()).entity;
    $('#panel').classList.toggle('is-pet',mode==='pet');
    $('#panelTitle').textContent=`${modes[mode]}属性`;
    $('#stage').dataset.screenLabel=`${modes[mode]}属性面板`;
    $('#entitySummary').textContent=mode==='hero'?`${e.level}级 · ${e.subtitle}`:`${e.level}级 · ${e.element}系`;
    document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode);});
    renderIdentity();
    $('.pet-detail-head')?.remove();
    if(mode==='pet') $('#stats').insertAdjacentHTML('beforebegin',`<div class="pet-detail-head"><img class="pet-detail-art" src="assets/portrait_${e.id}.png" alt="${e.subtitle}${e.name}"><div class="pet-detail-title"><h3>${e.name}</h3><span class="pet-chip">${e.subtitle}</span><p>${e.level}级 · ${e.element}系灵宠</p></div></div>`);
    renderExtra(e);
    $('#scheme').value=schemes[e.id];
    $('#footerText').textContent=mode==='hero'?'一念入道，五行随心':'山海相伴，灵契同心';
    $('#allocations').innerHTML=M.attributes.map((label,i)=>`<div class="attribute-row"><div class="attribute-label"><label for="range${i}" title="${attrNotes[i]}">${label}</label><span id="attributeValue${i}" class="attribute-value"></span></div><button type="button" class="stepper" data-minus="${i}" aria-label="减少${label}"><span>−</span></button><div class="slider-box"><input type="range" id="range${i}" step="1" data-range="${i}" aria-label="分配${label}属性点"></div><button type="button" class="stepper" data-plus="${i}" aria-label="增加${label}"><span>+</span></button></div>`).join('');
    renderNumbers();
  }
  function switchMode(next) {
    mode=next; const url=new URL(location.href);url.searchParams.set('panel',mode);history.replaceState({},'',url);render();
  }
  document.addEventListener('click',event=>{
    const target=event.target.closest('button');if(!target)return;
    if(target.dataset.mode) switchMode(target.dataset.mode);
    if(target.dataset.pet){selectedPet=target.dataset.pet;render();$(`[data-pet="${selectedPet}"]`).focus();}
    if(target.dataset.minus!==undefined){M.adjust(currentId(),Number(target.dataset.minus),-1);renderNumbers();}
    if(target.dataset.plus!==undefined){M.adjust(currentId(),Number(target.dataset.plus),1);renderNumbers();}
    if(target.dataset.open){$('#panel').hidden=false;$('#reopen').hidden=true;switchMode(target.dataset.open);$('#closePanel').focus();}
  });
  $('#allocations').addEventListener('input',event=>{if(event.target.dataset.range!==undefined){const i=Number(event.target.dataset.range),s=M.get(currentId());M.setDraft(currentId(),i,Number(event.target.value)-s.entity.base[i]-s.saved[i]);renderNumbers();}});
  $('#scheme').addEventListener('change',event=>{schemes[currentId()]=event.target.value;toast('已切换方案，点击自动加点分配剩余点数');});
  $('#reset').addEventListener('click',()=>{M.reset(currentId());renderNumbers();toast('已撤销本次分配');});
  $('#auto').addEventListener('click',()=>{M.auto(currentId(),schemes[currentId()]);renderNumbers();toast('已按当前方案分配，请确认加点');});
  $('#confirm').addEventListener('click',()=>{M.confirm(currentId());renderNumbers();renderExtra(M.get(currentId()).entity);toast('加点已确认');});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!$('#infoDialog').open&&!$('#panel').hidden){$('#closePanel').click();}});
  $('#closePanel').addEventListener('click',()=>{$('#panel').hidden=true;$('#reopen').hidden=false;$('[data-open="hero"]').focus();});
  $('#help').addEventListener('click',()=>dialog('加点说明','<ul><li>体质：提升气血与防御。</li><li>灵力：提升法力与法术伤害。</li><li>力量：提升物理伤害。</li><li>敏捷：提升速度，影响出手顺序。</li></ul><p>拖动滑杆或点击加减号进行分配。重置仅撤销本次改动；确认后保存加点。切换人物和宝宝会保留各自待确认的分配。</p><p class="demo-note">此页面为美术与交互预览，示例数据和收益系数用于展示。操作仅保存在当前页面，刷新后恢复初始值。正式加点规则由游戏客户端和服务端提供。</p>'));
  // Start on a reviewable pending allocation to show the preview state clearly.
  if(new URLSearchParams(location.search).get('state')!=='clean') {M.adjust('hero',0,2);M.adjust('hero',2,8);M.adjust('lingyue',1,6);}
  fit();render();
})();
