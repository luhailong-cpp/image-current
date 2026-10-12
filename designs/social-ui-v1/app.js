"use strict";
(() => {
  const root = document.getElementById("view-root");
  let cleanup = () => {};
  let activeView = "groups";
  let toastTimer;
  const titles = {groups:"仙 友 会",world:"四 海 传 音",rumor:"仙 闻 谣 言"};
  const notes = {groups:"道友相聚，一言一语皆是仙缘。",world:"四海同游，与道友共话仙山见闻。",rumor:"仙闻由系统传来，点击消息可查看详情。"};
  const helpers = {
    asset: name => "assets/" + name,
    toast: text => {
      clearTimeout(toastTimer);
      const box = document.getElementById("toast");
      box.textContent = text;
      box.hidden = false;
      toastTimer = setTimeout(() => {box.hidden=true;},4000);
    }
  };
  function showView(view,updateUrl=true) {
    if (!Object.hasOwn(titles,view)) view="groups";
    cleanup();
    activeView=view;
    document.getElementById("simulate-message").hidden=view!=="world";
    root.replaceChildren();
    document.getElementById("screen-title").textContent=titles[view];
    document.getElementById("shell-note").textContent=notes[view];
    document.querySelectorAll("[data-view]").forEach(button=>button.setAttribute("aria-pressed",button.dataset.view===view));
    if(view==="groups") cleanup=window.GroupsUI?.mount(root,helpers)||(()=>{});
    else cleanup=window.ChannelsUI?.mount(root,view,helpers)||(()=>{});
    if(!root.children.length) root.innerHTML='<div class="empty-state"><h2>仙山传音尚在准备</h2><p>请稍后切换查看。</p></div>';
    if(updateUrl) {const url=new URL(location.href);url.searchParams.set("view",view);history.replaceState({},"",url);}
    root.dataset.view=view;
    document.title="五行奇谈 · "+titles[view].replaceAll(" ","");
  }
  document.querySelector(".view-navigation").addEventListener("click",event=>{const button=event.target.closest("[data-view]");if(button)showView(button.dataset.view);});
  document.getElementById("simulate-message").addEventListener("click",()=>window.ChannelsUI?.simulateIncoming?.("world"));
  document.getElementById("reset-demo").addEventListener("click",()=>{
    cleanup();cleanup=()=>{};
    window.GroupsUI?.reset?.();window.ChannelsUI?.reset?.();
    window.dispatchEvent(new CustomEvent("social-preview-reset"));
    showView(activeView,false);helpers.toast("已恢复初始演示内容");
  });
  document.getElementById("close-social").addEventListener("click",()=>{document.querySelector(".social-window").hidden=true;document.getElementById("reopen-panel").hidden=false;document.getElementById("reopen-social").focus();});
  document.getElementById("reopen-social").addEventListener("click",()=>{document.querySelector(".social-window").hidden=false;document.getElementById("reopen-panel").hidden=true;document.getElementById("close-social").focus();});
  function fitStage(){if(innerWidth>900)document.getElementById("stage").style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/2560,innerHeight/1080)})`;}
  window.addEventListener("resize",fitStage);
  window.addEventListener("popstate",()=>showView(new URLSearchParams(location.search).get("view")||"groups",false));
  showView(new URLSearchParams(location.search).get("view")||"groups",false);fitStage();
})();
