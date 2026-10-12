"""Build a file:// offline review page from real, read-only PNG inventory.
Writes only preview/. Missing slots remain empty. No processing of image pixels.
Run again after new frames arrive; refresh preview/index.html.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, os, re, struct

BASE = Path(__file__).resolve().parents[1]
ROSTER = BASE.parents[2]
OUT = BASE / "preview"
OLD = ROSTER / "combat-20260929" / "characters" / BASE.name
RUN_TIMING = json.loads((BASE / "animation-timing.json").read_text(encoding="utf-8"))["run"]
ACTIONS = {
    "run": {"label": "跑步", "directions": ["N","NE","E","SE","S","SW","W","NW"], "count":16,"duration_ms":RUN_TIMING["frameMs"]},
    "hit": {"label": "受击", "directions":["E","W"],"count":6,"duration_ms":40},
    "attack": {"label":"普攻","directions":["E","W"],"count":12,"duration_ms":30},
    "cast": {"label":"施法","directions":["E","W"],"count":16,"duration_ms":45},
}
PRIOR_KEYS = ["hit-E-03-v3","hit-W-03-v2","attack-E-06-v2","attack-W-06-v1","cast-E-10-v2","cast-W-10-v2"]
RX = re.compile(r"^(run|hit|attack|cast)-(N|NE|E|SE|S|SW|W|NW)-(\d{2})-v(\d+)\.png$")
def relative(path):
    return os.path.relpath(path, OUT).replace("\\", "/")
def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
def inspect(path, origin):
    data=path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG: "+str(path))
    width,height=struct.unpack(">II",data[16:24])
    color_type=data[25]
    match=RX.match(path.name)
    action,direction,num,version=match.groups()
    record_path = path.with_suffix(".png.generation.json") if origin=="current" else OLD/"provenance"/"receipts"/(path.stem+".json")
    record=load_json(record_path)
    return {"key":path.stem,"slot":f"{action}-{direction}-{num}","action":action,"direction":direction,"frame":int(num),"version":int(version),
            "path":relative(path),"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"width":width,"height":height,"png_color_type":color_type,
            "origin":origin,"record_path":relative(record_path) if record_path.is_file() else None,
            "actual_model":record.get("actualModel"),"actual_quality":record.get("actualQuality"),
            "target_model":record.get("configSnapshot",{}).get("model"),"target_quality":record.get("configSnapshot",{}).get("quality"),
            "review_status":record.get("review",{}).get("status","pending"),"review_notes":record.get("review",{}).get("notes",""),
            "selection_reason":"当前在制候选，仅用于研究，不代表验收" if origin=="current" else "本地已提交旧关键帧，来源保留；需要重新检查边缘与动态"}
def build():
    OUT.mkdir(parents=True,exist_ok=True)
    inventory=[]
    for path in sorted((BASE/"staging").glob("*.png")):
        if RX.match(path.name):
            inventory.append(inspect(path,"current"))
    prior=[inspect(OLD/"staging"/(key+".png"),"prior") for key in PRIOR_KEYS if (OLD/"staging"/(key+".png")).is_file()]
    review_by_file={}
    explicit_selections={}
    for review_path in sorted(list(BASE.glob("review-*.json"))+list((BASE/"review").glob("review-*.json")),key=lambda p:p.stat().st_mtime):
        review=load_json(review_path)
        for group in ("selectedForSequenceReview","frames","reviewed","attempts"):
            for item in review.get(group,[]):
                raw=item.get("file") or item.get("currentFile") or item.get("selectedFile")
                if not raw and item.get("key"):
                    raw=item["key"]+".png"
                if not raw:
                    continue
                filename=Path(raw).name
                review_by_file[filename]=item
                slot=item.get("slot")
                if not isinstance(slot,str) or not slot.startswith(("run","hit","attack","cast")):
                    slot=RX.match(filename).group(0).rsplit("-v",1)[0] if RX.match(filename) else None
                if slot and group in ("selectedForSequenceReview","frames"):
                    explicit_selections[slot.replace("/","-")]=filename
    for item in inventory:
        extra=review_by_file.get(item["key"]+".png")
        if extra:
            item["review_status"]=extra.get("status",item["review_status"])
            item["review_notes"]=extra.get("notes") or extra.get("review") or extra.get("visualNotes") or extra.get("actualObservation") or "；".join(x for x in [extra.get("handConnection"),extra.get("groundingObservation"),"；".join(extra.get("issues",[]))] if x)
    by_slot={}
    for item in prior+inventory:
        by_slot.setdefault(item["slot"],[]).append(item)
    slots=[]
    for action,spec in ACTIONS.items():
        for direction in spec["directions"]:
            for frame in range(1,spec["count"]+1):
                slot=f"{action}-{direction}-{frame:02}"
                candidates=by_slot.get(slot,[])
                eligible=[x for x in candidates if "superseded" not in x["review_status"] and x["review_status"] not in ["rejected","failed"]]
                preferred=next((x for x in candidates if x["key"]+".png"==explicit_selections.get(slot)),None)
                selected=preferred or max(eligible or candidates,key=lambda x:(x["origin"]=="current",x["version"]),default=None)
                slots.append({"slot":slot,"action":action,"direction":direction,"frame":frame,"duration_ms":spec["duration_ms"],"selected":selected,
                              "variants":candidates,"status":"missing" if selected is None else ("passed" if selected["review_status"]=="passed" else "pending"),
                              "event":"释放" if action=="cast" and frame==10 else ("接触" if action=="attack" and frame==6 else "")})
    data={"schema_version":1,"character":"17_ghost_script_calligrapher_boy","label":"17 灵篆书生",
          "built_at":datetime.now(timezone(timedelta(hours=-4))).isoformat(),"timezone":"America/New_York",
          "read_only_sources":True,"automatic_refresh":"重新运行 tools/build_preview.py 后刷新本页；浏览器不会扫描本地目录",
          "selection_policy":"优先使用逐帧审查明确选择的文件，未有明确选择才按候选版本排序。较高版本号不代表视觉通过。未生成槽位为空。",
          "run_timing":{"normal_cycle_ms":RUN_TIMING["cycleMs"],"frame_ms":RUN_TIMING["frameMs"],"uniform":True,"client_tested":False,"preview":"timing-grounding.html"},
          "actions":ACTIONS,"slots":slots,"prior_keyframes":prior,"current_inventory":inventory,
          "counts":{"expected":len(slots),"available":sum(s["selected"] is not None for s in slots),"missing":sum(s["selected"] is None for s in slots),
                    "passed":sum(s["status"]=="passed" for s in slots),"current_pngs":len(inventory),"prior_keyframes":len(prior)}}
    (OUT/"manifest-preview.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    html=HTML.replace("__MANIFEST__",json.dumps(data,ensure_ascii=False).replace("</","<\\/"))
    (OUT/"index.html").write_text(html,encoding="utf-8")
    print(json.dumps({"page":str(OUT/"index.html"),"counts":data["counts"]},ensure_ascii=False))
HTML=r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>17 灵篆书生 · 动作制作预览</title><style>
:root{color-scheme:dark;--bg:#101919;--panel:#172525;--line:#314343;--text:#ecf1eb;--muted:#9fb4ac;--gold:#d9b872;--teal:#9ad8c1;--red:#ffb4a6}*{box-sizing:border-box}body{margin:0;background:var(--bg);font:14px/1.55 "Microsoft YaHei","Segoe UI",sans-serif;color:var(--text)}button,select,input{font:inherit}button,select{border:1px solid var(--line);border-radius:7px;padding:8px 12px;background:#1d2e2d;color:var(--text)}button{cursor:pointer}button:hover{border-color:var(--teal)}button:disabled{opacity:.4;cursor:default}button.active{color:#13211c;background:var(--teal);border-color:var(--teal)}a{color:var(--teal)}header{padding:22px 28px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:24px;align-items:center}h1{font-size:24px;letter-spacing:.02em;margin:0;font-weight:600}header p{margin:4px 0 0;color:var(--muted)}.eyebrow{font-size:11px;letter-spacing:.14em;color:var(--gold);margin-bottom:4px}.stats{display:flex;gap:24px}.stat b{font-size:26px;color:var(--gold);font-weight:500}.stat span{display:block;font-size:12px;color:var(--muted)}main{padding:20px 28px 28px;max-width:1600px;margin:auto}.toolbar{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-bottom:16px}.actions,.directions,.buttons{display:flex;gap:6px;flex-wrap:wrap}.actions button{min-width:80px}.directions button{min-width:41px;padding:7px 9px}.spacer{flex:1}.chip{font-size:12px;color:var(--gold);padding:5px 10px;border:1px solid #635739;border-radius:20px}.workspace{display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:18px}.canvas-card,.inspector,.film{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--panel)}.canvas-top{display:flex;justify-content:space-between;gap:16px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line)}.canvas-top strong{font-size:15px;font-weight:500}.canvas-top small{color:var(--muted)}.stage{position:relative;height:min(58vh,650px);min-height:390px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#222a2d}.stage.light{background:#eee8dc}.stage.checker{background-color:#dadbd4;background-image:linear-gradient(45deg,#bfc7c0 25%,transparent 25%),linear-gradient(-45deg,#bfc7c0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#bfc7c0 75%),linear-gradient(-45deg,transparent 75%,#bfc7c0 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.square{position:relative;width:min(100%,58vh,650px);aspect-ratio:1;flex-shrink:0}.sprite{position:absolute;width:100%;height:100%;object-fit:contain;display:none}.missing{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#94a6a3;gap:6px}.missing .symbol{font-size:42px;font-weight:200;opacity:.5}.missing b{font-size:20px;font-weight:400}.stage.light .missing,.stage.checker .missing{color:#53675e}.root-guide{position:absolute;left:3%;right:3%;top:92.105%;border-top:1px dashed #ecb26c80;pointer-events:none}.root-guide::after{content:"虚拟地面参考";position:absolute;right:0;top:3px;font-size:10px;color:#d69b52}.root-guide.hidden{display:none}.frame-badge{position:absolute;left:14px;top:14px;font-size:12px;color:#e5f2e7;background:#102720cc;border:1px solid #5a7864;border-radius:5px;padding:3px 8px}.mode-note{min-height:44px;display:flex;align-items:center;padding:9px 16px;color:#ebcd8c;background:#2c2b20;font-size:12px;border-top:1px solid #48432d}.transport{display:flex;align-items:center;gap:10px;padding:12px 16px;flex-wrap:wrap}.transport .play{background:var(--teal);color:#13211c;min-width:76px}.transport label{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}.transport input{accent-color:#9ad8c1}.slider-row{padding:0 16px 14px;display:flex;gap:12px;align-items:center}.slider-row input{flex:1;accent-color:#9ad8c1}.slider-row span{font-variant-numeric:tabular-nums;min-width:68px;color:var(--muted)}.inspector{padding:18px}.inspector h2{font-size:15px;font-weight:500;margin:0 0 16px}.field{margin:0 0 14px}.field dt{font-size:11px;letter-spacing:.02em;color:var(--muted);margin-bottom:4px}.field dd{margin:0;font-size:13px;overflow-wrap:anywhere}.status{color:var(--gold)}.sha{font-family:Consolas,monospace;font-size:11px!important;color:#b3c6bc}.notes{padding:10px 12px;background:#22302b;border-left:2px solid var(--gold);font-size:12px;color:#ddd2af;min-height:62px;margin:16px 0}.variant-select{width:100%;font-size:12px;padding:7px}.rule{padding-top:12px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)}.film{margin-top:18px;padding:14px 16px}.film-head{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:12px;font-size:13px}.film-head small{color:var(--muted)}.frames{display:grid;grid-template-columns:repeat(16,minmax(36px,1fr));gap:7px}.thumb{position:relative;aspect-ratio:.78;padding:2px 2px 18px;border-radius:7px;border:1px solid var(--line);background:#222e2c;overflow:hidden}.thumb img{width:100%;height:100%;object-fit:contain;display:block}.thumb span{position:absolute;bottom:1px;left:0;right:0;font-size:10px;color:var(--muted);text-align:center}.thumb.empty{border-style:dashed;background:#192321}.thumb.empty::before{content:"·";position:absolute;top:15%;left:0;right:0;text-align:center;font-size:24px;color:#45554e}.thumb.selected{outline:2px solid var(--teal);outline-offset:1px}.thumb.event::after{content:"";position:absolute;width:5px;height:5px;right:5px;top:5px;border-radius:50%;background:var(--gold)}.footer{margin-top:16px;display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;font-size:11px;color:var(--muted)}.legend{display:flex;gap:15px;align-items:center}.legend i{display:inline-block;width:6px;height:6px;background:var(--gold);border-radius:50%;margin-right:5px}button:focus-visible,select:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--gold);outline-offset:3px}@media(max-width:1050px){.workspace{grid-template-columns:minmax(0,1fr) 270px}.stats{gap:15px}.frames{gap:4px}}@media(max-width:760px){header{padding:16px 18px;display:block}.stats{gap:20px;margin-top:14px;justify-content:space-between}.stat b{font-size:20px}.stat span{font-size:10px}h1{font-size:20px}main{padding:16px 12px}.workspace{grid-template-columns:1fr}.stage{height:56vh;min-height:340px}.inspector{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}.inspector h2,.inspector .notes,.inspector .rule{grid-column:1/-1}.frames{grid-template-columns:repeat(8,minmax(28px,1fr))}.toolbar{gap:10px}.actions button{min-width:60px;padding:7px 10px}.directions button{min-width:35px}.canvas-top{padding:10px 12px}.transport{padding:10px 12px;gap:7px}.transport select{max-width:100%;font-size:12px}header p{font-size:11px}.chip{display:none}}
</style></head><body>
<header><div><div class="eyebrow">五行奇谈 / ANIMATION REVIEW</div><h1>17 灵篆书生</h1><p>动作制作预览 · 独立 PNG · 本地离线</p></div><div class="stats"><div class="stat"><b id="available">0</b><span>有图槽位 / 196</span></div><div class="stat"><b id="missingTotal">0</b><span>尚缺帧数</span></div><div class="stat"><b id="passed">0</b><span>视觉通过</span></div></div></header>
<main><div class="toolbar"><div class="actions" id="actions"></div><div class="directions" id="directions"></div><div class="spacer"></div><span class="chip">在制候选 · 未接入客户端</span></div>
<div class="workspace"><section class="canvas-card"><div class="canvas-top"><div><strong id="sequenceTitle"></strong><small id="sequenceCount"></small></div><div class="buttons" aria-label="背景"><button data-bg="dark" class="active">深底</button><button data-bg="light">浅底</button><button data-bg="checker">棋盘</button></div></div><div class="stage" id="stage"><div class="square"><img class="sprite" id="sprite" alt=""><div class="missing" id="empty"><span class="symbol">◇</span><b>本槽位尚未生成</b><span>保留为空，继续核对真实帧序</span></div><div class="root-guide" id="guide"></div></div><span class="frame-badge" id="frameBadge"></span></div><div class="mode-note" id="modeNote"></div><div class="transport"><button id="previous" title="上一帧（←）">←</button><button class="play" id="play">播放</button><button id="next" title="下一帧（→）">→</button><select id="speed" aria-label="播放速度"><option value="1">正常速度 ×1</option><option value="0.25">慢速 ×0.25</option></select><select id="mode" aria-label="帧组模式"><option value="slots">完整槽位 · 缺帧留空</option></select><label><input type="checkbox" id="guideToggle" checked>地面参考</label></div><div class="slider-row"><input id="frameSlider" type="range" min="1" max="16" value="1" aria-label="逐帧位置"><span id="framePosition"></span></div></section>
<aside class="inspector"><h2>当前帧与来源</h2><dl class="field"><dt>槽位</dt><dd id="slotName"></dd></dl><dl class="field"><dt>检查状态</dt><dd class="status" id="status"></dd></dl><dl class="field"><dt>来源</dt><dd id="origin"></dd></dl><dl class="field"><dt>原生 PNG / 每帧时长</dt><dd id="dimensions"></dd></dl><dl class="field"><dt>版本选择（不表示通过）</dt><dd><select id="variant" class="variant-select" aria-label="选择候选版本"></select></dd></dl><dl class="field"><dt>模型与质量实测</dt><dd id="modelInfo"></dd></dl><dl class="field"><dt>PNG 与逐图记录</dt><dd id="fileLinks"></dd></dl><dl class="field"><dt>当前文件 SHA-256</dt><dd class="sha" id="sha"></dd></dl><div class="notes" id="reviewNotes"></div><div class="rule">画布完整等比显示，不按人物包围盒缩放，也不逐帧贴地。旧关键帧保留原路径；版本号更高不代表验收通过。</div></aside></div>
<section class="film"><div class="film-head"><span id="filmTitle">完整槽位</span><small>点击缩略图逐帧查看 · ← / → 逐帧 · 空格播放</small></div><div class="frames" id="frames"></div></section><div class="footer"><span id="buildInfo"></span><div class="legend"><span><i></i>接触 / 释放标记</span><a href="manifest-preview.json">真实文件清单</a></div><span>新图落盘后重跑 build_preview.py，再刷新本页。</span></div></main>
<script id="data" type="application/json">__MANIFEST__</script><script>
"use strict";
const M=JSON.parse(document.getElementById("data").textContent), $=id=>document.getElementById(id);
let action="attack", direction="E", frame=1, playing=false, timer=null, variant=null, deadline=0;
$("available").textContent=M.counts.available; $("missingTotal").textContent=M.counts.missing; $("passed").textContent=M.counts.passed;
$("buildInfo").textContent="盘点时间 "+M.built_at.replace("T"," ").slice(0,19)+"（纽约）";
const sequence=()=>M.slots.filter(s=>s.action===action&&s.direction===direction);
const current=()=>sequence().find(s=>s.frame===frame);
const playlist=()=>sequence();
function stop(){playing=false;clearTimeout(timer);$("play").textContent="播放";}
function updateButtons(){
  $("actions").replaceChildren(...Object.entries(M.actions).map(([key,value])=>{const b=document.createElement("button");b.textContent=value.label;b.className=key===action?"active":"";b.onclick=()=>{stop();action=key;direction=M.actions[key].directions.includes(direction)?direction:"E";frame=1;variant=null;updateButtons();render();};return b;}));
  $("directions").replaceChildren(...M.actions[action].directions.map(key=>{const b=document.createElement("button");b.textContent=key;b.className=key===direction?"active":"";b.onclick=()=>{stop();direction=key;frame=1;variant=null;updateButtons();render();};return b;}));
}
function render(){
  const seq=sequence(),s=current(),v=s.variants.find(x=>x.key===variant)||s.selected;
  const spec=M.actions[action],available=seq.filter(x=>x.selected).length;
  $("sequenceTitle").textContent=spec.label+" / "+direction+"  ";
  $("sequenceCount").textContent=available+" / "+spec.count+" 帧有图";
  $("frameBadge").textContent=direction+" · "+String(frame).padStart(2,"0")+(s.event?" · "+s.event:"");
  $("framePosition").textContent=String(frame).padStart(2,"0")+" / "+spec.count;
  $("frameSlider").max=spec.count;$("frameSlider").value=frame;
  $("slotName").textContent=s.slot+(s.event?" · "+s.event:"");
  $("status").textContent=!v?"缺失":v.review_status==="passed"?"视觉通过":"待验收 / "+v.review_status;
  $("origin").textContent=!v?"尚无图片":v.origin==="current"?"本批新稿":"本地旧关键帧（原来源）";
  $("dimensions").textContent=v?v.width+" × "+v.height+" · "+(v.png_color_type===6?"RGBA":"PNG 类型 "+v.png_color_type)+" · "+s.duration_ms+" ms":"— · "+s.duration_ms+" ms";
  $("modelInfo").textContent=v?((v.actual_model||"未确认")+" / "+(v.actual_quality||"未确认")):"—";
  $("sha").textContent=v?v.sha256:"—";
  $("reviewNotes").textContent=!v?"本槽位尚未生成。当前不使用占位图、复制图或插值补齐。":v.review_notes||"当前在制候选。需检查手脚、持物、透明边缘及整段连续性，图片存在不等于通过。";
  $("variant").replaceChildren();
  if(v){for(const candidate of [...s.variants].reverse()){const o=document.createElement("option");o.value=candidate.key;o.textContent=candidate.key+(candidate.origin==="prior"?" · 旧":"");o.selected=candidate.key===v.key;$("variant").append(o);}}
  else{$("variant").append(new Option("无图片",""));}
  $("variant").disabled=!v;
  $("fileLinks").replaceChildren();
  if(v){const a=document.createElement("a");a.href=v.path;a.textContent="打开 PNG";a.target="_blank";$("fileLinks").append(a);if(v.record_path){$("fileLinks").append(" · ");const rec=document.createElement("a");rec.href=v.record_path;rec.textContent="生成记录";rec.target="_blank";$("fileLinks").append(rec);}}
  else{$("fileLinks").textContent="—";}
  $("sprite").style.display=v?"block":"none";$("empty").style.display=v?"none":"flex";
  if(v){$("sprite").src=v.path;$("sprite").alt=s.slot+" "+(v.origin==="prior"?"旧关键帧":"新在制稿");}
  else{$("sprite").removeAttribute("src");}
  $("modeNote").textContent=$("mode").value==="research"?"研究连播：仅跳转现有关键帧，跳过缺口；不等于完整动作，也不代表动态验收通过。":"完整槽位模式：按原帧序和时长播放，缺失位置显示为空。当前序列 "+available+" / "+spec.count+" 帧有图。";
  if(action==="run"){$("modeNote").append(" 跑步正常1×：1200ms/圈，16帧均匀75ms。 ");const a=document.createElement("a");a.href="timing-grounding.html";a.textContent="接地与逐帧检查";$("modeNote").append(a);}
  $("filmTitle").textContent=spec.label+" "+direction+" · 全部 "+spec.count+" 个真实槽位";
  $("frames").replaceChildren(...seq.map(slot=>{const b=document.createElement("button");b.className="thumb"+(!slot.selected?" empty":"")+(slot.frame===frame?" selected":"")+(slot.event?" event":"");b.title=slot.slot+" · "+(slot.status==="passed"?"视觉通过":slot.selected?"待验收":"缺失");if(slot.selected){const im=document.createElement("img");im.src=slot.selected.path;im.alt="";b.append(im);}const n=document.createElement("span");n.textContent=String(slot.frame).padStart(2,"0");b.append(n);b.onclick=()=>{stop();frame=slot.frame;variant=null;render();};return b;}));
  $("play").disabled=$("mode").value==="research"&&available===0;
}
function step(delta){const items=playlist();if(!items.length){stop();return;}let index=items.findIndex(s=>s.frame===frame);if(index<0)index=delta>0?-1:0;frame=items[(index+delta+items.length)%items.length].frame;variant=null;render();}
function schedule(){timer=setTimeout(tick,Math.max(0,deadline-performance.now()));}
function tick(){if(!playing)return;step(1);deadline+=M.actions[action].duration_ms/Number($("speed").value);schedule();}
$("play").onclick=()=>{if(playing){stop();return;}if(!playlist().length)return;playing=true;$("play").textContent="暂停";if($("mode").value==="research"&&!current().selected){frame=playlist()[0].frame;render();}deadline=performance.now()+M.actions[action].duration_ms/Number($("speed").value);schedule();};
$("previous").onclick=()=>{stop();step(-1);};$("next").onclick=()=>{stop();step(1);};
$("frameSlider").oninput=()=>{stop();frame=Number($("frameSlider").value);variant=null;render();};
$("mode").onchange=()=>{stop();if($("mode").value==="research"&&!current().selected&&playlist().length)frame=playlist()[0].frame;render();};
$("speed").onchange=()=>{if(playing){clearTimeout(timer);deadline=performance.now()+M.actions[action].duration_ms/Number($("speed").value);schedule();}};
$("variant").onchange=()=>{stop();variant=$("variant").value;render();};
$("guideToggle").onchange=()=>$("guide").classList.toggle("hidden",!$("guideToggle").checked);
document.querySelectorAll("[data-bg]").forEach(b=>b.onclick=()=>{$("stage").className="stage "+b.dataset.bg;document.querySelectorAll("[data-bg]").forEach(x=>x.classList.toggle("active",x===b));});
document.addEventListener("keydown",e=>{if(["INPUT","SELECT","BUTTON","A"].includes(document.activeElement.tagName))return;if(e.code==="Space"){e.preventDefault();$("play").click();}if(e.key==="ArrowLeft"){$("previous").click();}if(e.key==="ArrowRight"){$("next").click();}});
document.addEventListener("visibilitychange",()=>{if(document.hidden)stop();});
updateButtons();render();
</script></body></html>'''
if __name__=="__main__":
    build()

