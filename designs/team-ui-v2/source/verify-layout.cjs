const fs = require('fs');
const path = require('path');
const {chromium} = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir = path.resolve(__dirname, '..', 'qa');
(async()=> {
 fs.mkdirSync(dir, {recursive:true});
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();
 const errors=[], badResponses=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400) badResponses.push({url:r.url(),status:r.status()})});
 const results=[];
 for (const viewport of [{width:2560,height:1080},{width:1920,height:1080},{width:390,height:844}]) {
  await page.setViewportSize(viewport);
  await page.goto('http://127.0.0.1:4311/team-ui-v2/',{waitUntil:'networkidle'});
  await page.screenshot({path:path.join(dir,`preview-${viewport.width}.png`),fullPage:true});
  results.push(await page.evaluate(()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,body:document.body.innerText,missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),buttons:[...document.querySelectorAll('button')].map(b=>({text:b.textContent.trim(),label:b.getAttribute('aria-label'),id:b.id,disabled:b.disabled}))})));
 }
 const report={checkedAt:new Date().toISOString(),browser:await browser.version(),errors,badResponses,viewports:results};
 fs.writeFileSync(path.join(dir,'layout-report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));
 await browser.close();
 if(errors.length||badResponses.length||results.some(r=>r.missingImages.length||r.scrollWidth>r.width)) process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
