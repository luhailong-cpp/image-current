(function(){
'use strict';
const $=id=>document.getElementById(id), fmt=n=>Number(n).toLocaleString('zh-CN');
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const img=(file,cls='')=>'<img src="assets/'+esc(file)+'" alt="" class="'+cls+'">';
const pages=['overview','members','donation','tasks','events','shop'];
const labels={overview:'帮会总览',members:'帮会成员',donation:'帮会捐献',tasks:'帮会任务',events:'帮会活动',shop:'帮会商店'};
const key='wuxing-guild-demo-v2';
let cached;try{cached=JSON.parse(localStorage.getItem(key)||'null');}catch(_){cached=null;}
const store=GuildModel.createStore({state:cached});
let page=pages.includes(location.hash.slice(1))?location.hash.slice(1):'overview';
let filters={query:'',online:false,sort:'contribution',page:1}, timer, dialogAction, dialogOrigin;
function save(s){try{localStorage.setItem(key,JSON.stringify(s));$('saveStatus').textContent='本地演示 · 自动保存';}catch(_){$('saveStatus').textContent='本地演示 · 仅本次有效';}}
function toast(text){clearTimeout(timer);$('toast').textContent=text;$('toast').hidden=false;timer=setTimeout(()=>$('toast').hidden=true,4200);}
function focusBack(origin){const el=origin?.isConnected?origin:origin?.id?$(origin.id):null;(el&&!el.disabled?el:$('tab-'+page))?.focus({preventScroll:true});}
function modal(title,html,label,action,cancel='取消'){
 if(!$('actionDialog').open)dialogOrigin=document.activeElement;
 dialogAction=action||null;$('dialogTitle').textContent=title;$('dialogBody').innerHTML=html;$('dialogError').hidden=true;
 $('dialogActions').innerHTML=action?'<button class="button" id="dialogCancel">'+esc(cancel)+'</button><button class="button primary" id="dialogConfirm">'+esc(label)+'</button>':'<button class="button primary" id="dialogCancel">知道了</button>';
 if(!$('actionDialog').open)$('actionDialog').showModal();
 ($('dialogBody').querySelector('input,textarea,select')||$('dialogCancel')).focus();
}
function act(action,fromDialog=false){const r=store.dispatch(action);if(!r.ok&&fromDialog){$('dialogError').textContent=r.message;$('dialogError').hidden=false;}else{if(fromDialog)$('actionDialog').close();toast(r.message);}return r;}
function go(next,focus=false){page=pages.includes(next)?next:'overview';if(location.hash.slice(1)!==page)history.pushState(null,'','#'+page);render();$('pageContent').scrollTop=0;if(focus)$('tab-'+page).focus();}
const avatar=m=>'<span class="avatar">'+img(m.avatar)+'</span>';
const online=m=>'<span class="online'+(m.online?'':' offline')+'">'+(m.online?'在线':'离线')+'</span>';
const heading=(title,sub,aside='')=>'<div class="page-heading"><div><h2>'+esc(title)+'</h2><p>'+esc(sub)+'</p></div>'+aside+'</div>';
function summary(s){
 const leader=s.members.find(m=>m.id!=='self'&&m.role==='帮主')||s.members.find(m=>m.role==='帮主');
 $('guildSummary').innerHTML='<div class="guild-identity">'+img('round_badge_taiji.png','guild-emblem')+'<div><h2>'+esc(s.guild.name)+'</h2><span class="level-label">'+s.guild.level+' 级帮会</span></div></div>'
 +'<dl class="guild-details">'+[['帮会编号',s.guild.id],['帮主',leader?.name||'云隐真人'],['成员',s.members.length+' / '+s.guild.memberCapacity],['帮会资金',fmt(s.guild.funds)],['我的职位',s.currentUser.role]].map(([k,v])=>'<div><dt>'+k+'</dt><dd>'+esc(v)+'</dd></div>').join('')+'</dl>'
 +'<div class="construction"><div><span>帮会建设</span><strong>'+fmt(s.guild.construction)+' / '+fmt(s.guild.constructionTarget)+'</strong></div><div class="progress" role="progressbar" aria-label="帮会建设" aria-valuemin="0" aria-valuemax="'+s.guild.constructionTarget+'" aria-valuenow="'+Math.min(s.guild.construction,s.guild.constructionTarget)+'"><span style="width:'+Math.min(100,s.guild.construction/s.guild.constructionTarget*100)+'%"></span></div></div>'
 +'<div class="motto">'+img('lantern.png')+'<p>同修五行<br>共护仙途</p></div><div class="summary-actions"><button id="rulesButton" class="button compact" data-action="rules">查看帮规</button></div>';
}
function overview(s){
 const e=s.events[0];
 return heading('同心共修 · 青云道盟','道友相聚，一起走更远的仙途。','<span>'+s.members.filter(m=>m.online).length+' 位道友在线</span>')
 +'<div class="metric-strip"><div><span>帮会成员</span><strong>'+s.members.length+'<small> / '+s.guild.memberCapacity+'</small></strong></div><div><span>待领取委托</span><strong>'+s.tasks.filter(t=>!t.claimed&&t.progress>=t.target).length+'<small> 份</small></strong></div><div><span>本周贡献</span><strong>'+fmt(s.members[0].weeklyContribution)+'</strong></div></div>'
 +'<div class="overview-columns"><section class="announcement"><div class="mini-heading"><h3>帮会公告</h3><button id="editAnnouncement" class="text-button" data-action="announcement">'+(['帮主','长老'].includes(s.currentUser.role)?'编辑公告':'查看公告')+'</button></div><blockquote>'+esc(s.guild.announcement)+'</blockquote></section>'
 +'<section class="gathering"><div class="mini-heading"><h3>同门邀约</h3></div><div class="gathering-body">'+img(e.icon)+'<div><strong>'+esc(e.name)+'</strong><p>'+esc(e.dateLabel)+'</p><button id="overviewEvent" class="button compact" data-go="events">'+(e.joined?'查看报名':'前往活动')+'</button></div></div></section></div>'
 +'<div class="quick-entries">'+[['donation','furnace','帮会捐献'],['tasks','compass','帮会任务'],['events','sword','帮会活动'],['shop','pagoda','帮会商店']].map(([id,icon,name])=>'<button id="quick-'+id+'" class="quick-entry" data-go="'+id+'">'+img('round_badge_'+icon+'.png')+'<span>'+name+'</span></button>').join('')+'</div>';
}
function memberRows(s){
 const all=s.members.filter(m=>(!filters.online||m.online)&&(!filters.query||m.name.includes(filters.query.trim())));
 const rank={'帮主':0,'长老':1,'精英':2,'帮众':3};
 all.sort((a,b)=>filters.sort==='level'?b.level-a.level:filters.sort==='role'?rank[a.role]-rank[b.role]||b.weeklyContribution-a.weeklyContribution:b.weeklyContribution-a.weeklyContribution);
 const count=Math.max(1,Math.ceil(all.length/5));filters.page=Math.max(1,Math.min(count,filters.page));
 if(!all.length)return '<div class="empty-state"><h3>没有找到这位道友</h3><p>换一个姓名，或取消“仅看在线”后再试。</p><button id="clearMemberFilter" class="button" data-action="clear-filter">清除筛选</button></div>';
 return '<div class="member-table" role="table" aria-label="帮会成员列表"><div class="member-header" role="row">'+['成员','等级','职位','周贡献','状态','资料'].map(x=>'<span role="columnheader">'+x+'</span>').join('')+'</div>'
 +all.slice((filters.page-1)*5,filters.page*5).map(m=>'<div class="member-row'+(m.id===s.currentUser.id?' is-self':'')+'" role="row"><div class="member-name" role="cell">'+avatar(m)+'<div><strong>'+esc(m.name)+(m.id===s.currentUser.id?'<span class="self-label">自己</span>':'')+'</strong><span class="member-mobile-meta">'+m.level+'级 · '+esc(m.role)+'</span></div></div><span class="member-level" role="cell">'+m.level+'</span><span class="member-role" role="cell">'+esc(m.role)+'</span><span class="member-contribution" role="cell">'+fmt(m.weeklyContribution)+'</span><span role="cell">'+online(m)+'</span><span role="cell"><button id="profile-'+m.id+'" class="text-button" data-profile="'+m.id+'" aria-label="查看'+esc(m.name)+'资料">查看</button></span></div>').join('')
 +'</div><div class="pagination"><button id="memberPrev" data-action="member-prev" aria-label="上一页成员"'+(filters.page===1?' disabled':'')+'>‹</button><span>第 '+filters.page+' / '+count+' 页 · 共 '+all.length+' 人</span><button id="memberNext" data-action="member-next" aria-label="下一页成员"'+(filters.page===count?' disabled':'')+'>›</button></div>';
}
function members(s){return heading('帮会成员','同门名录，仙途有你。','<span>'+s.members.filter(m=>m.online).length+' 人在线 / '+s.members.length+' 人</span>')
 +'<div class="filters"><label class="search-label" for="memberSearch">查找道友<input id="memberSearch" type="search" value="'+esc(filters.query)+'" placeholder="输入成员姓名" maxlength="24"></label><label class="filter-check"><input id="onlineOnly" type="checkbox"'+(filters.online?' checked':'')+'>仅看在线</label><select id="memberSort" aria-label="成员排序">'+[['contribution','按周贡献'],['level','按等级'],['role','按职位']].map(([v,l])=>'<option value="'+v+'"'+(filters.sort===v?' selected':'')+'>'+l+'</option>').join('')+'</select></div><div id="memberResults" aria-live="polite">'+memberRows(s)+'</div>';}
function donation(s){return heading('一份心意，共筑山门','捐献铜钱，增加帮会资金、建设与个人贡献。')
 +'<div class="content-cards">'+Object.values(GuildModel.donationTiers).map((t,i)=>{const left=t.limit-s.donationCounts[t.id],poor=s.currentUser.coins<t.coins;return '<article class="content-card"><div class="card-title">'+img(i?'round_badge_taiji.png':'round_badge_furnace.png')+'<div><h3>'+esc(t.label)+'</h3><p>每日最多 '+t.limit+' 次</p></div></div><p class="card-copy">'+(i?'倾囊相助，为同门修行添一份助力。':'滴水汇流，一点心意也能护佑山门。')+'</p><div class="reward-line"><span>贡献 <strong>+'+t.contribution+'</strong></span><span>建设 <strong>+'+t.construction+'</strong></span></div><div class="card-actions"><p>今日剩余 '+left+' 次<br>铜钱 '+fmt(t.coins)+'</p><button id="donate-'+t.id+'" class="button primary" data-donate="'+t.id+'"'+(left<=0||poor?' disabled':'')+'>'+(left<=0?'今日已满':poor?'铜钱不足':'立即捐献')+'</button></div></article>';}).join('')+'</div><p class="tip-box">捐献前会再次确认。每日次数按本地日期重置，演示铜钱与贡献仅保存在当前浏览器。</p>';}
function tasks(s){return heading('同门委托','完成委托，积累帮会贡献。','<span>'+s.tasks.filter(t=>t.claimed).length+' / '+s.tasks.length+' 已领取</span>')
 +'<div class="page-list">'+s.tasks.map(t=>'<article class="list-card">'+img(t.icon)+'<div><h3>'+esc(t.name)+'</h3><p>'+esc(t.description)+'</p><div class="progress" role="progressbar" aria-label="'+esc(t.name)+'进度" aria-valuemin="0" aria-valuemax="'+t.target+'" aria-valuenow="'+t.progress+'"><span style="width:'+Math.min(100,t.progress/t.target*100)+'%"></span></div><div class="reward-small">贡献 +'+t.reward.contribution+' · 铜钱 +'+fmt(t.reward.coins)+'</div></div><div class="list-action"><span class="state-label'+(t.progress<t.target?' unavailable':'')+'">'+(t.claimed?'奖励已领取':t.progress>=t.target?'已完成':t.progress+' / '+t.target+' 进行中')+'</span><button id="claim-'+t.id+'" class="button'+(t.progress>=t.target&&!t.claimed?' primary':'')+'" data-task="'+t.id+'"'+(t.claimed||t.progress<t.target?' disabled':'')+'>'+(t.claimed?'已领取':t.progress<t.target?'尚未完成':'领取奖励')+'</button></div></article>').join('')+'</div><p class="tip-box">任务进度为固定样例，奖励可在“所得道具”查看。尚未完成的委托不可领奖。</p>';}
function events(s){return heading('相约青云，共赴仙途','花灯、试炼、论道，总有同门与你同行。')
 +'<div class="page-list">'+s.events.map(e=>'<article class="list-card">'+img(e.icon)+'<div><h3>'+esc(e.name)+'</h3><p>'+esc(e.description)+'</p><div class="event-meta"><span>'+esc(e.dateLabel)+'</span><span>'+e.participants+' / '+e.capacity+' 人</span></div></div><div class="list-action"><span class="state-label'+(e.status!=='open'?' unavailable':'')+'">'+(e.joined?'✓ 已报名':e.status==='open'?'报名进行中':e.status==='upcoming'?'尚未开放':'本场已结束')+'</span><button id="event-'+e.id+'" class="button'+(e.status==='open'&&!e.joined?' primary':'')+'" data-event="'+e.id+'"'+(!e.joined&&(e.status!=='open'||e.participants>=e.capacity)?' disabled':'')+'>'+(e.joined?'取消报名':e.status==='upcoming'?'敬请期待':e.status==='ended'?'已结束':e.participants>=e.capacity?'报名已满':'立即报名')+'</button></div></article>').join('')+'</div><p class="tip-box">活动时间和人数均为演示场次；报名只更新本地状态，不向真实帮会发送消息。</p>';}
function shop(s){return heading('帮会珍藏，以贡献相赠','兑换所得收入演示背包。','<span>可用贡献 '+fmt(s.currentUser.contribution)+'</span>')
 +'<div class="shop-grid">'+s.shop.map(p=>'<article class="shop-item">'+img(p.icon)+'<h3>'+esc(p.name)+'</h3><p>'+esc(p.description)+'</p><div class="shop-price"><strong>'+fmt(p.cost)+'</strong> 贡献</div><div class="shop-stock">剩余可兑 '+p.stock+' 份</div><button id="buy-'+p.id+'" class="button'+(p.stock>0&&s.currentUser.contribution>=p.cost?' primary':'')+'" data-buy="'+p.id+'"'+(p.stock<=0||s.currentUser.contribution<p.cost?' disabled':'')+'>'+(p.stock<=0?'已兑完':s.currentUser.contribution<p.cost?'贡献不足':'兑换')+'</button></article>').join('')+'</div><p class="tip-box">兑换需确认数量与总贡献。限购为本次演示额度，重置演示后恢复。</p>';}
const renderers={overview,members,donation,tasks,events,shop};
function render(){
 const active=document.activeElement, start=active?.selectionStart, end=active?.selectionEnd, s=store.getState();
 summary(s);$('pageContent').innerHTML=renderers[page](s);$('pageContent').setAttribute('aria-labelledby','tab-'+page);
 document.querySelectorAll('[role="tab"]').forEach(t=>{const on=t.dataset.page===page;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;});
 $('contribution').textContent=fmt(s.currentUser.contribution);$('coins').textContent=fmt(s.currentUser.coins);$('signInButton').disabled=s.signedInDate===s.dailyDate;$('signInButton').textContent=$('signInButton').disabled?'今日已签到':'每日签到';document.title='五行奇谈 · '+labels[page];
 if(active?.id&&!active.isConnected){const el=$(active.id);if(el&&!el.disabled){el.focus({preventScroll:true});if(typeof start==='number'&&el.setSelectionRange)el.setSelectionRange(start,end);}else $('tab-'+page).focus({preventScroll:true});}
}
function rules(){modal('青云道盟 · 帮规','<div class="dialog-copy"><p>同修五行，共护仙途。</p><ul><li>同门相待，以礼为先；互帮互助，不扰他人修行。</li><li>捐献与委托可积累贡献，兑换道具会消耗可用贡献。</li><li>帮主与长老可维护公告，普通成员可查看与参与。</li></ul><p>本页数据为本地演示。签到按本地日期更新，任务奖励与商品额度可通过“重置演示”恢复。</p></div>');}
function announcement(){
 const s=store.getState();
 if(!['帮主','长老'].includes(s.currentUser.role)){modal('帮会公告','<div class="dialog-copy"><p style="white-space:pre-wrap">'+esc(s.guild.announcement)+'</p><p class="subtle">当前职位：'+esc(s.currentUser.role)+'。仅帮主、长老可以编辑公告。</p></div>');return;}
 modal('编辑帮会公告','<label for="announcementInput">公告内容 <span class="subtle">8–180 字</span></label><textarea id="announcementInput" class="announcement-input" maxlength="180">'+esc(s.guild.announcement)+'</textarea><p class="subtle">编辑只影响本地演示。</p>','保存公告',()=>act({type:'UPDATE_ANNOUNCEMENT',text:$('announcementInput').value},true));
}
function exchange(id){
 const s=store.getState(),p=s.shop.find(x=>x.id===id);if(!p)return;const max=Math.min(p.stock,Math.floor(s.currentUser.contribution/p.cost));
 modal('兑换确认','<div class="dialog-product">'+img(p.icon)+'<div><h3>'+esc(p.name)+'</h3><p>'+fmt(p.cost)+' 贡献 / 份 · 剩余 '+p.stock+' 份</p></div></div><label class="quantity-label" for="exchangeQuantity">兑换数量<input id="exchangeQuantity" class="quantity-input" type="number" min="1" max="'+max+'" step="1" value="1" inputmode="numeric"></label><div class="quantity-total"><span>本次消耗</span><strong id="exchangeTotal">'+fmt(p.cost)+' 贡献</strong></div><p class="subtle">可用贡献 '+fmt(s.currentUser.contribution)+'</p>','确认兑换',()=>act({type:'EXCHANGE',id,quantity:Number($('exchangeQuantity').value)},true));
 $('exchangeQuantity').addEventListener('input',()=>{const n=Number($('exchangeQuantity').value);$('exchangeTotal').textContent=Number.isSafeInteger(n)&&n>0?fmt(n*p.cost)+' 贡献':'请输入有效数量';$('dialogError').hidden=true;});
}
function bag(){const items=Object.entries(store.getState().inventory).filter(([,n])=>n>0);modal('所得道具',items.length?'<ul class="bag-list">'+items.map(([id,n])=>'<li><span>'+esc(GuildModel.inventoryLabels[id])+'</span><strong>× '+n+'</strong></li>').join('')+'</ul><p class="subtle" style="margin-top:15px">来自本地委托奖励与帮会兑换。</p>':'<div class="empty-state"><h3>背包还空着</h3><p>领取委托奖励或前往帮会商店兑换。</p></div>');}
document.addEventListener('click',event=>{
 const b=event.target.closest('button');if(!b||b.disabled)return;const d=b.dataset;
 if(d.page)go(d.page,true);
 if(d.go){if($('actionDialog').open)$('actionDialog').close();go(d.go,true);}
 if(d.donate){const t=GuildModel.donationTiers[d.donate];modal(t.label,'<div class="dialog-copy"><p>本次捐献 <strong>'+fmt(t.coins)+' 铜钱</strong>。</p><p>获得贡献 <strong>+'+t.contribution+'</strong>，帮会建设 <strong>+'+t.construction+'</strong>，帮会资金 <strong>+'+fmt(t.funds)+'</strong>。</p><p class="subtle">当前铜钱 '+fmt(store.getState().currentUser.coins)+'，确认后保存到本地演示。</p></div>','确认捐献',()=>act({type:'DONATE',tier:d.donate},true));}
 if(d.task)act({type:'CLAIM_TASK',id:d.task});
 if(d.event){const e=store.getState().events.find(x=>x.id===d.event);if(e.joined)modal('取消报名','<p class="dialog-copy">取消「'+esc(e.name)+'」本次演示报名？</p>','确认取消',()=>act({type:'TOGGLE_EVENT',id:e.id},true),'保留报名');else act({type:'TOGGLE_EVENT',id:e.id});}
 if(d.buy)exchange(d.buy);
 if(d.profile){const m=store.getState().members.find(x=>x.id===d.profile);modal('道友资料','<div class="profile-card">'+avatar(m)+'<h3>'+esc(m.name)+'</h3><p>'+m.level+'级 · '+esc(m.role)+'</p>'+online(m)+'<p>本周贡献 '+fmt(m.weeklyContribution)+'</p><p class="subtle">青云道盟 · 本地成员样例</p></div>');}
 if(d.action==='rules')rules();if(d.action==='announcement')announcement();
 if(d.action==='clear-filter'){filters={query:'',online:false,sort:'contribution',page:1};render();$('memberSearch').focus();}
 if(d.action==='member-prev'||d.action==='member-next'){filters.page+=d.action==='member-next'?1:-1;render();focusBack(b);}
});
$('pageContent').addEventListener('input',e=>{if(e.target.id==='memberSearch'){filters.query=e.target.value;filters.page=1;$('memberResults').innerHTML=memberRows(store.getState());}});
$('pageContent').addEventListener('change',e=>{if(e.target.id==='onlineOnly')filters.online=e.target.checked;else if(e.target.id==='memberSort')filters.sort=e.target.value;else return;filters.page=1;$('memberResults').innerHTML=memberRows(store.getState());});
document.querySelector('.tabs').addEventListener('keydown',e=>{if(!e.target.matches('[role="tab"]'))return;const i=pages.indexOf(page);let n;if(e.key==='ArrowRight')n=(i+1)%pages.length;if(e.key==='ArrowLeft')n=(i+pages.length-1)%pages.length;if(e.key==='Home')n=0;if(e.key==='End')n=pages.length-1;if(n!==undefined){e.preventDefault();go(pages[n],true);}});
function closeWindow(){$('guildWindow').hidden=true;$('reopen').hidden=false;$('reopenButton').focus();}
$('closeWindow').addEventListener('click',closeWindow);
$('reopenButton').addEventListener('click',()=>{$('guildWindow').hidden=false;$('reopen').hidden=true;render();$('tab-'+page).focus();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('actionDialog').open&&!$('guildWindow').hidden){e.preventDefault();closeWindow();}});
$('signInButton').addEventListener('click',()=>act({type:'SIGN_IN'}));$('bagButton').addEventListener('click',bag);
$('hallButton').addEventListener('click',()=>modal('青云山门 · 帮会驻地','<p class="hall-note">驻地功能导航 · 本地预览</p><div class="hall-grid">'+[['donation','furnace','建设堂'],['tasks','compass','委托堂'],['events','sword','演武场'],['shop','pagoda','珍宝阁']].map(([id,icon,name])=>'<button data-go="'+id+'">'+img('round_badge_'+icon+'.png')+name+'</button>').join('')+'</div>'));
$('demoRoleButton').addEventListener('click',()=>{const role=store.getState().currentUser.role;modal('切换演示身份','<div class="dialog-copy"><p>用于查看公告编辑权限；不会改变任何真实帮会职务。</p><label class="role-selector" for="demoRole">演示职位<select id="demoRole">'+GuildModel.roles.map(r=>'<option'+(r===role?' selected':'')+'>'+r+'</option>').join('')+'</select></label></div>','切换身份',()=>act({type:'SET_DEMO_ROLE',role:$('demoRole').value},true));});
$('resetButton').addEventListener('click',()=>modal('重置演示数据','<div class="dialog-copy"><p>恢复初始贡献、铜钱、任务、报名、兑换和公告。此操作只清除当前浏览器的帮会演示进度。</p></div>','确认重置',()=>{const r=store.reset();filters={query:'',online:false,sort:'contribution',page:1};render();$('actionDialog').close();toast(r.message);}));
$('dialogClose').addEventListener('click',()=>$('actionDialog').close());
$('dialogActions').addEventListener('click',e=>{const b=e.target.closest('button');if(b?.id==='dialogCancel')$('actionDialog').close();if(b?.id==='dialogConfirm'&&dialogAction)dialogAction();});
$('actionDialog').addEventListener('close',()=>{const origin=dialogOrigin;dialogOrigin=null;dialogAction=null;focusBack(origin);});
$('actionDialog').addEventListener('keydown',e=>{if(e.key!=='Tab')return;const items=Array.from($('actionDialog').querySelectorAll('button:not(:disabled),input:not(:disabled),textarea:not(:disabled),select:not(:disabled),a[href]')).filter(el=>el.getClientRects().length>0);if(!items.length){e.preventDefault();return;}const at=items.indexOf(document.activeElement);if(e.shiftKey&&at<=0){e.preventDefault();items[items.length-1].focus();}else if(!e.shiftKey&&(at===items.length-1||at<0)){e.preventDefault();items[0].focus();}});
function onHistory(){page=pages.includes(location.hash.slice(1))?location.hash.slice(1):'overview';render();}
window.addEventListener('popstate',onHistory);window.addEventListener('hashchange',onHistory);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)render();});
store.subscribe(s=>{save(s);render();});save(store.getState());render();
}());

