const {chromium}=require("C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const fs=require("fs");
const path=require("path");
(async()=>{
 let browser;
 try {browser=await chromium.launch({headless:true});}
 catch(e){browser=await chromium.launch({headless:true,channel:"msedge"});}
 const page=await browser.newPage({viewport:{width:1440,height:1120},deviceScaleFactor:1});
 const errors=[];page.on("pageerror",e=>errors.push(e.message));
 await page.goto("file:///"+path.join(__dirname,"index.html").replace(/\\/g,"/"));
 await page.locator("#sprite").waitFor({state:"visible"});
 await page.waitForFunction(()=>document.querySelector("#sprite").complete&&document.querySelector("#sprite").naturalWidth>0);
 const checks=[];
 checks.push({name:"initial image loads via file protocol",pass:await page.locator("#sprite").evaluate(e=>e.naturalWidth>=1024)});
 await page.screenshot({path:path.join(__dirname,"qa-desktop.png"),fullPage:true});
 await page.getByRole("button",{name:"施法",exact:true}).click();
 checks.push({name:"cast E01 missing remains empty",pass:await page.locator("#empty").isVisible()});
 await page.selectOption("#mode","research");
 checks.push({name:"research uses E10 v3 still pending",pass:await page.locator("#variant").inputValue()==="cast-E-10-v3"&&(await page.locator("#status").innerText()).includes("待验收")});
 await page.getByRole("button",{name:"浅底",exact:true}).click();
 await page.screenshot({path:path.join(__dirname,"qa-cast-light.png"),fullPage:true});
 await page.selectOption("#mode","slots");
 await page.locator("#next").click();
 checks.push({name:"complete slots show missing E11",pass:(await page.locator("#slotName").innerText()).startsWith("cast-E-11")&&await page.locator("#empty").isVisible()});
 await page.getByRole("button",{name:"跑步",exact:true}).click();
 await page.getByRole("button",{name:"N",exact:true}).click();
 await page.selectOption("#mode","research");
 checks.push({name:"empty direction cannot play research",pass:await page.locator("#play").isDisabled()});
 await page.getByRole("button",{name:"普攻",exact:true}).click();
 await page.selectOption("#mode","slots");
 await page.locator("#frameSlider").evaluate(e=>{e.value="6";e.dispatchEvent(new Event("input",{bubbles:true}));});
 await page.waitForFunction(()=>document.querySelector("#sprite").complete&&document.querySelector("#sprite").naturalWidth>0);
 checks.push({name:"old attack E06 relative source loads",pass:(await page.locator("#sprite").getAttribute("src")).includes("combat-20260929")&&await page.locator("#sprite").evaluate(e=>e.naturalWidth>=1024)});

 for (const [value,expected] of [["1",30],["0.25",120]]) {
   await page.selectOption("#speed",value);
   const timing=await page.evaluate(async()=>{
     const stamps=[];const node=document.querySelector("#slotName");
     const observer=new MutationObserver(()=>{stamps.push(performance.now());});
     observer.observe(node,{childList:true});document.querySelector("#play").click();
     await new Promise(resolve=>{const check=()=>stamps.length>=6?resolve():setTimeout(check,20);check();});
     document.querySelector("#play").click();observer.disconnect();
     return stamps.slice(1).map((t,i)=>t-stamps[i]);
   });
   const average=timing.reduce((a,b)=>a+b,0)/timing.length;
   checks.push({name:"playback speed "+value,pass:average>=expected*.75&&average<=expected+80,measuredMeanMs:average});
 }
 await page.getByRole("button",{name:"深底",exact:true}).click();
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(__dirname,"qa-mobile.png"),fullPage:true});
 checks.push({name:"mobile no horizontal overflow",pass:await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)});
 checks.push({name:"no JavaScript runtime errors",pass:errors.length===0,errors});
 fs.writeFileSync(path.join(__dirname,"qa-results.json"),JSON.stringify({testedAt:new Date().toISOString(),checks},null,2));
 console.log(JSON.stringify(checks));
 await browser.close();
 if(checks.some(x=>!x.pass))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1);});

