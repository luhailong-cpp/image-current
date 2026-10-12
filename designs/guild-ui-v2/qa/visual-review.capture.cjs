const fs=require('fs'), path=require('path');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='E:/work/image/designs/guild-ui-v2/qa';
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage(); const errors=[],results=[];
 page.on('pageerror',e=>errors.push(e.message));
 for(const size of [{width:1600,height:675},{width:1920,height:1080},{width:390,height:844},{width:320,height:844}]){
  await page.setViewportSize(size);
  await page.goto('http://127.0.0.1:4345/guild-ui-v2/',{waitUntil:'networkidle'});
  for(const id of ['overview','members','donation','tasks','events','shop']){
   await page.locator('[data-page="'+id+'"]').click();
   await page.evaluate(()=>{scrollTo(0,0);document.querySelector('#pageContent').scrollTop=0;});
   await page.screenshot({path:path.join(out,'visual-review-'+size.width+'x'+size.height+'-'+id+'.png'),fullPage:true});
   const result=await page.evaluate(()=>{
    const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
    const visible=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getClientRects().length>0;};
    const clipped=[];
    for(const e of [...document.querySelectorAll('#guildWindow h1,#guildWindow h2,#guildWindow h3,#guildWindow button,#guildWindow p,#guildWindow strong,#guildWindow dt,#guildWindow dd,#guildWindow blockquote')].filter(visible)){
     const r=rect(e), s=getComputedStyle(e); if((e.scrollWidth>e.clientWidth+2&&s.whiteSpace==='nowrap')||(e.scrollHeight>e.clientHeight+2&&['hidden','clip'].includes(s.overflowY)))clipped.push({tag:e.tagName,id:e.id,className:e.className,text:e.innerText,rect:r,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight});
    }
    const pc=document.getElementById('pageContent'),summary=document.getElementById('guildSummary');
    return {viewport:{width:innerWidth,height:innerHeight},doc:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},window:rect(document.querySelector('#guildWindow')),pageContent:{...rect(pc),scrollWidth:pc.scrollWidth,clientWidth:pc.clientWidth,scrollHeight:pc.scrollHeight,clientHeight:pc.clientHeight,overflowY:getComputedStyle(pc).overflowY},summary:{...rect(summary),scrollWidth:summary.scrollWidth,clientWidth:summary.clientWidth},footer:rect(document.querySelector('.window-footer')),title:rect(document.querySelector('.title-plaque')),clippedText:clipped,missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),images:[...document.images].filter(visible).map(i=>({file:i.src.split('/').pop(),natural:[i.naturalWidth,i.naturalHeight],display:rect(i),fit:getComputedStyle(i).objectFit})),borderImage:getComputedStyle(document.querySelector('.guild-window'),'::before').borderImage,foregroundSamples:[...document.querySelectorAll('.subtle,.page-heading p,.tip-box,.guild-details dt,.shop-stock,.state-label')].filter(visible).map(e=>({text:e.innerText,color:getComputedStyle(e).color,fontSize:getComputedStyle(e).fontSize,opacity:getComputedStyle(e).opacity}))};
   });
   results.push({page:id,...result});
  }
 }
 await browser.close();
 const report={checkedAt:new Date().toISOString(),scope:'Read-only visual capture and layout measurements; no repeated business interaction tests',errors,results};
 fs.writeFileSync(path.join(out,'visual-review.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({captures:results.length,errors,issues:results.filter(r=>r.doc.width>r.viewport.width||r.pageContent.scrollWidth>r.pageContent.clientWidth+2||r.clippedText.length||r.missingImages.length).map(r=>({page:r.page,width:r.viewport.width,horizontalOverflow:r.doc.width-r.viewport.width,contentOverflow:r.pageContent.scrollWidth-r.pageContent.clientWidth,clipped:r.clippedText,missing:r.missingImages}))}));
})().catch(e=>{console.error(e);process.exit(1)});
