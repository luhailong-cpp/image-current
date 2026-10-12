"""Build manifest, technical checks, contact sheets and browser preview; never modify runtime PNGs."""
from __future__ import annotations
import hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SPECS=[("hit",6,40),("attack",12,30),("cast",16,45)]
LABELS={"hit":"受击","attack":"普攻","cast":"施法"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def resolve(p):
    pp=Path(p)
    return pp if pp.is_absolute() else ROOT/pp
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
def native_metadata(record):
    native=dict(record.get("native") or {})
    derived=record.get("derivedFrom") or {}
    if not isinstance(derived,dict):derived={}
    earlier=derived.get("native") or {}
    size=record.get("nativeSize") or derived.get("nativeSize") or [None,None]
    native["width"]=native.get("width") or record.get("nativeWidth") or earlier.get("width") or size[0]
    native["height"]=native.get("height") or record.get("nativeHeight") or earlier.get("height") or size[1]
    native["sha256"]=native.get("sha256") or record.get("nativeSha256") or record.get("sourceSha256") or derived.get("sha256")
    native["format"]=native.get("format") or record.get("nativeFormat") or earlier.get("format")
    native["mode"]=native.get("mode") or record.get("nativeMode") or earlier.get("mode")
    native["path"]=record.get("sourceNativePath") or record.get("nativeFile") or record.get("source") or derived.get("path") or derived.get("file")
    return native
def apply_visual_qa(manifest,validation):
    path=ROOT/"VISUAL_QA.json"
    if not path.is_file():return
    try:
        review=json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(review,dict):raise ValueError("Expected JSON object")
    except Exception as e:
        validation["warnings"].append({"warning":"visual_qa_unreadable","detail":str(e)})
        return
    evidence={"file":"VISUAL_QA.json","sha256":sha(path),"review":review}
    manifest["visualReviewEvidence"]=evidence
    validation["visualReviewEvidence"]=evidence
    # Only an explicit independent review can change visual/playback status.
    manifest["visualStatus"]=review.get("status","independent-review-recorded")
    validation["visualApproval"]=review.get("visualApproval") is True
    validation["sequencePlaybackVerified"]=review.get("sequencePlaybackVerified") is True
    reviewed_hashes=review.get("frameSha256")
    if isinstance(reviewed_hashes,dict):
        stale=[f["id"] for f in manifest["frames"] if f.get("sha256")!=reviewed_hashes.get(f["id"])]
        if stale:
            manifest["visualStatus"]="stale-review-evidence"
            validation["visualApproval"]=False
            validation["sequencePlaybackVerified"]=False
            validation["warnings"].append({"warning":"visual_qa_hashes_stale","frames":stale})
            return
    frame_reviews=review.get("frames",{})
    if isinstance(frame_reviews,list):frame_reviews={r.get("id"):r for r in frame_reviews if isinstance(r,dict)}
    for frame in manifest["frames"]:
        item=frame_reviews.get(frame["id"]) if isinstance(frame_reviews,dict) else None
        if isinstance(item,dict):frame["visualStatus"]=item.get("status",frame["visualStatus"])
    group_reviews=review.get("groups",{})
    if isinstance(group_reviews,list):group_reviews={r.get("id"):r for r in group_reviews if isinstance(r,dict)}
    for group in manifest["groups"]:
        item=group_reviews.get(group["id"]) if isinstance(group_reviews,dict) else None
        if isinstance(item,dict):group["visualReview"]=item
def check_record(r,p,hashval):
    errors=[]
    if r.get("sha256")!=hashval:errors.append("record_sha256_mismatch")
    for key in ("configSnapshot","submittedParameters","actualModel","actualQuality","generatedAt","prompt","references","unverifiedReason"):
        if key not in r:errors.append("record_field_missing:"+key)
    prompt=r.get("prompt")
    if isinstance(prompt,str) and not resolve(prompt).is_file(): errors.append("prompt_missing")
    evidence=r.get("evidence",{})
    for key in ("resultMetadata",):
        if key in evidence and not resolve(evidence[key]).is_file():errors.append("evidence_missing:"+key)
    return errors
def main():
    built=datetime.now(timezone.utc).isoformat()
    frames=[];groups=[]; errors=[];warnings=[];refs=[];hashes={};pixelhashes={}
    for action,count,duration in SPECS:
        for direction in ("E","W"):
            gid=direction+"-"+action; groupframes=[]
            for num in range(1,count+1):
                file=ROOT/"runtime"/action/direction/f"{num:02d}.png"
                options=[ROOT/"records"/gid/f"{num:02d}.generation.json",ROOT/"records"/gid/f"{num:02d}.json"]
                rp=next((p for p in options if p.is_file()),None)
                entry={"id":f"{gid}-{num:02d}","file":rel(file),"action":action,"direction":direction,"frame":num,"durationMs":duration,"pivot":[0.5,0.08],"anchorTopLeftPx":[512,942],"event":("recoil_peak" if action=="hit" and num==3 else "attack_release" if action=="attack" and num==7 else "cast_release" if action=="cast" and num==11 else None),"exists":file.is_file(),"sourceRecord":rel(rp) if rp else None,"visualStatus":"not-package-approved"}
                if file.is_file():
                    try:
                        with Image.open(file) as im:
                            im.load()
                            entry.update(width=im.width,height=im.height,mode=im.mode,format=im.format,sha256=sha(file))
                            hashes.setdefault(entry["sha256"],[]).append(entry["id"])
                            pix=hashlib.sha256(im.tobytes()).hexdigest()
                            pixelhashes.setdefault(pix,[]).append(entry["id"])
                            entry["pixelSha256"]=pix
                            if im.size!=(1024,1024):errors.append({"frame":entry["id"],"error":"size_not_1024"})
                            if im.mode!="RGBA":errors.append({"frame":entry["id"],"error":"mode_not_RGBA"})
                            else:
                                alpha=im.getchannel("A")
                                entry["alphaExtrema"]=list(alpha.getextrema())
                                entry["alphaBBox"]=alpha.getbbox()
                                core=alpha.point(lambda a:255 if a>=8 else 0)
                                entry["alpha8BBox"]=core.getbbox()
                                hist=alpha.histogram()
                                entry["transparentPixels"]=hist[0]
                                entry["lowAlphaPixels"]=sum(hist[1:8])
                                if hist[0]==0 or hist[255]==0: errors.append({"frame":entry["id"],"error":"invalid_transparent_alpha"})
                                cb=entry["alpha8BBox"]
                                if cb and (cb[0]<16 or cb[1]<16 or cb[2]>1008 or cb[3]>1008):warnings.append({"frame":entry["id"],"warning":"alpha8_near_edge","bbox":cb})
                    except Exception as e:errors.append({"frame":entry["id"],"error":str(e)})
                    if not rp:errors.append({"frame":entry["id"],"error":"generation_record_missing"})
                    else:
                        try:
                            r=json.loads(rp.read_text(encoding="utf-8-sig"))
                            for err in check_record(r,rp,entry.get("sha256")):errors.append({"frame":entry["id"],"error":err})
                            entry["source"]={"tool":r.get("tool"),"route":r.get("route"),"generatedAt":r.get("generatedAt"),"actualModel":r.get("actualModel"),"actualQuality":r.get("actualQuality"),"configSnapshot":r.get("configSnapshot"),"prompt":r.get("prompt"),"native":native_metadata(r),"operation":r.get("operation"),"review":r.get("visualReview",r.get("visualStatus"))}
                            for reference in r.get("references",[]):
                                path=reference.get("path") if isinstance(reference,dict) else reference
                                if path:
                                    refs.append({"frame":entry["id"],"path":path,"exists":resolve(path).is_file(),"role":reference.get("role",reference.get("purpose")) if isinstance(reference,dict) else None})
                        except Exception as e:errors.append({"frame":entry["id"],"error":"record_read:"+str(e)})
                frames.append(entry);groupframes.append(entry)
            groups.append({"id":gid,"action":action,"direction":direction,"label":LABELS[action]+" "+direction,"expected":count,"present":sum(f["exists"] for f in groupframes),"durationMs":duration,"totalDurationMs":count*duration,"frames":groupframes,"contactSheet":"qa/"+gid+"-contact.png"})
    duplicates=[v for v in hashes.values() if len(v)>1]
    pixelduplicates=[v for v in pixelhashes.values() if len(v)>1]
    if duplicates:errors.append({"error":"duplicate_file_sha256","groups":duplicates})
    if pixelduplicates:errors.append({"error":"duplicate_decoded_pixels","groups":pixelduplicates})
    missing=[f["file"] for f in frames if not f["exists"]]
    missingrefs=[r for r in refs if not r["exists"]]
    # Historical native sources may be intentionally deleted after approved exports.
    if missingrefs:warnings.append({"warning":"reference_sources_not_on_disk","items":missingrefs,"note":"Historical native references require explicit cleanup/replacement mapping; not automatically treated as live design references."})
    manifest={"schemaVersion":1,"name":"桂灯童","builtAt":built,"coordinateSystem":"top-left pixels for anchor; bottom-left normalized pivot","canvas":[1024,1024],"expectedFrameCount":68,"presentFrameCount":sum(f["exists"] for f in frames),"animationScope":["hit","attack","cast"],"directions":{"E":"斜前朝右下","W":"真正斜后朝左上"},"modelEvidenceNote":"配置目标不等于实际版本；未披露的 actualModel/actualQuality 保留 null。","visualStatus":"pending-human-sequence-review","clientIntegration":"not-tested","groups":groups,"frames":frames}
    validation={"builtAt":built,"expected":68,"present":manifest["presentFrameCount"],"technicalStatus":"complete" if not errors and not missing else "incomplete" if not errors else "issues","missingFrames":missing,"errors":errors,"warnings":warnings,"duplicateFileGroups":duplicates,"duplicatePixelGroups":pixelduplicates,"referenceChecks":refs,"unknownActualModelCount":sum(f.get("source",{}).get("actualModel") is None for f in frames if f["exists"]),"unknownActualQualityCount":sum(f.get("source",{}).get("actualQuality") is None for f in frames if f["exists"]),"visualApproval":False,"sequencePlaybackVerified":False,"clientIntegrationVerified":False,"note":"尺寸/透明/SHA技术检查不能替代逐帧、连续播放与客户端验收。"}
    apply_visual_qa(manifest,validation)
    dump(ROOT/"manifest.json",manifest);dump(ROOT/"validation.json",validation)
    (ROOT/"SHA256SUMS.txt").write_text("".join(f["sha256"]+"  "+f["file"]+"\n" for f in frames if f.get("sha256")),encoding="utf-8")
    contacts(groups);preview(manifest)
    own=[f for f in frames if f["direction"]=="W" and f["action"] in ("hit","attack")]
    dump(ROOT/"records"/"W-attack"/"technical-qa.json",{"builtAt":built,"count":sum(f["exists"] for f in own),"expected":18,"errors":[e for e in errors if str(e.get("frame","")).startswith(("W-hit","W-attack"))],"sequencePlaybackVerified":validation.get("sequencePlaybackVerified") is True,"singleFramesInspected":True,"frames":[{"file":f["file"],"sha256":f.get("sha256"),"size":[f.get("width"),f.get("height")],"alphaExtrema":f.get("alphaExtrema")} for f in own]})
    print(json.dumps({"present":manifest["presentFrameCount"],"expected":68,"errors":len(errors),"warnings":len(warnings),"missing":len(missing),"preview":str(ROOT/"preview"/"index.html")},ensure_ascii=False))
def contacts(groups):
    dest=ROOT/"qa";dest.mkdir(exist_ok=True)
    try:font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",18)
    except OSError:font=ImageFont.load_default()
    cell=256;label=30;cols=4
    for g in groups:
        out=Image.new("RGB",(cols*cell,math.ceil(g["expected"]/cols)*(cell+label)),(220,222,216))
        d=ImageDraw.Draw(out)
        for i,f in enumerate(g["frames"]):
            x=(i%cols)*cell;y=(i//cols)*(cell+label)
            for by in range(0,cell,16):
                for bx in range(0,cell,16):
                    shade=(235,237,231) if ((bx//16+by//16)%2)==0 else (206,211,201)
                    d.rectangle((x+bx,y+by,x+bx+15,y+by+15),fill=shade)
            if f["exists"]:
                with Image.open(ROOT/f["file"]) as im:
                    thumb=im.convert("RGBA").resize((cell,cell),Image.Resampling.LANCZOS)
                    out.paste(thumb,(x,y),thumb)
            else:d.text((x+70,y+115),"MISSING",fill=(150,30,30),font=font)
            d.text((x+9,y+cell+3),f'{g["id"]}  {f["frame"]:02d}/{g["expected"]:02d}  {g["durationMs"]}ms',fill=(30,45,35),font=font)
        out.save(dest/(g["id"]+"-contact.png"))
def preview(manifest):
    template=TEMPLATE
    # Embedded data also works with file://; PNG URLs remain relative to preview/index.html.
    data=json.dumps(manifest,ensure_ascii=False).replace("<","\\u003c")
    path=ROOT/"preview"/"index.html";path.parent.mkdir(exist_ok=True)
    path.write_text(template.replace("__MANIFEST_JSON__",data),encoding="utf-8")
TEMPLATE=r'''<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>桂灯童 · 三动作验看</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f3ed;color:#20362e;font:15px/1.5 "Segoe UI","Microsoft YaHei",sans-serif}main{max-width:1260px;margin:auto;padding:28px}h1{font-size:28px;margin:0 0 6px}.note{color:#68746d;margin:0 0 20px}.layout{display:grid;grid-template-columns:minmax(320px,1fr) 310px;gap:24px}.panel{background:#fffef9;border:1px solid #d8ddd1;border-radius:16px;padding:18px}.stage{width:min(100%,calc(100vh - 225px));width:min(100%,calc(100dvh - 225px));max-height:calc(100dvh - 225px);aspect-ratio:1;margin-inline:auto;position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:10px;background-color:#dce1d9;background-image:linear-gradient(45deg,#edf0e9 25%,transparent 25%),linear-gradient(-45deg,#edf0e9 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#edf0e9 75%),linear-gradient(-45deg,transparent 75%,#edf0e9 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0}.stage.dark{background-color:#26332f;background-image:linear-gradient(45deg,#35443d 25%,transparent 25%),linear-gradient(-45deg,#35443d 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#35443d 75%),linear-gradient(-45deg,transparent 75%,#35443d 75%)}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.empty{background:#fffdebdc;padding:18px;border-radius:8px;color:#6c4638;max-width:90%;text-align:center;z-index:2}.caption{margin-top:10px;display:flex;justify-content:space-between;gap:12px}label{font-weight:600;display:block;margin:0 0 6px}select,button{font:inherit;border:1px solid #bdc9bd;border-radius:8px;padding:9px 12px;background:#fff;color:#20362e}button{cursor:pointer}button:hover{background:#e5eee3}.primary{background:#245e4c;color:white;border-color:#245e4c}.primary:hover{background:#1a4d3c}.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:15px 0}.wide{width:100%}input[type=range]{width:100%;accent-color:#245e4c}.meta{font-size:13px;overflow-wrap:anywhere;border-top:1px solid #e0e5dc;padding-top:14px;margin-top:16px}.meta p{margin:8px 0}a{color:#246450}.warning{padding:11px;border-radius:8px;background:#f7efda;color:#725730}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px;margin-top:22px}.sheet img{width:100%;display:block;border-radius:7px}.sheet strong{display:block;margin-bottom:7px}.sheet{text-decoration:none;color:inherit}.footer{font-size:13px;color:#6c766d;margin-top:25px}@media(max-width:800px){main{padding:14px}.layout{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.panel{padding:12px}}
</style></head>
<body><main><h1>桂灯童 · 三动作验看</h1><p class="note">受击 / 普攻 / 施法 · E 斜前朝右下 / W 斜后朝左上 · 1024 透明原地战斗帧</p>
<div class="layout"><section class="panel"><div id="stage" class="stage"><img id="sprite" alt="当前动作帧"><div id="empty" class="empty" hidden></div></div><div class="caption"><strong id="caption"></strong><span id="clock"></span></div><input id="frame" type="range" min="1" max="6" value="1" aria-label="帧编号"></section>
<aside class="panel"><label for="group">动作与方向</label><select id="group" class="wide"></select><div class="row"><button id="play" class="primary">播放</button><button id="prev" aria-label="上一帧">← 上一帧</button><button id="next" aria-label="下一帧">下一帧 →</button></div><label for="speed">播放速度</label><select id="speed" class="wide"><option value="1">正常 · 1× 原帧时长</option><option value="0.25">慢放 · 0.25×</option></select><div class="row"><button id="light">浅棋盘底</button><button id="dark">深棋盘底</button></div><p id="availability" class="warning"></p><div class="meta"><p id="framepath"></p><p id="recordpath"></p><p id="timing"></p><p>锚点 [512, 942]，左下 pivot [0.5, 0.08]。播放时未按脚底重对齐。</p><p>方向、手足、持物、蓄力—出手—回收需实际验看。文件检查不代表美术或客户端验收。</p><p id="model"></p><p><a href="../manifest.json">manifest</a> · <a href="../validation.json">技术检查</a> · <a href="../SHA256SUMS.txt">SHA-256</a></p></div></aside></div>
<div id="sheets" class="grid"></div><p class="footer" id="built"></p></main>
<script>
const manifest=__MANIFEST_JSON__;
const $=id=>document.getElementById(id);
const groupEl=$("group"),image=$("sprite"),empty=$("empty"),range=$("frame");
let current=manifest.groups[0],index=0,playing=false,lastTime=null,accum=0,frameChanges=0;
for(const g of manifest.groups){const o=document.createElement("option");o.value=g.id;o.textContent=g.label+" · "+g.present+"/"+g.expected+" 帧";groupEl.append(o)}
const preload=new Map;
for(const f of manifest.frames){if(f.exists){const img=new Image;img.src="../"+f.file;preload.set(f.file,img)}}
function groupReviewComplete(){
if(manifest.visualStatus==="stale-review-evidence")return false;
const packageReview=manifest.visualReviewEvidence?.review||{},groupReview=current.visualReview||{};
const packagePassed=packageReview.visualApproval===true&&packageReview.sequencePlaybackVerified===true;
const groupPassed=groupReview.visualApproval===true&&groupReview.sequencePlaybackVerified===true;
const groupStatusPassed=["passed","approved","passed-frame-and-sequence"].includes(groupReview.status)&&groupReview.visualApproval!==false&&groupReview.sequencePlaybackVerified!==false;
return packagePassed||groupPassed||groupStatusPassed;
}
function render(){
const f=current.frames[index];range.value=index+1;range.max=current.expected;
$("caption").textContent=current.label+" · "+String(index+1).padStart(2,"0")+" / "+current.expected;
$("clock").textContent=(index*current.durationMs)+" / "+current.totalDurationMs+" ms";
image.hidden=!f.exists;empty.hidden=f.exists;
if(f.exists){image.src="../"+f.file;image.alt=current.label+" 第 "+f.frame+" 帧";empty.textContent=""}else{image.removeAttribute("src");empty.textContent="此帧尚未落盘："+f.file}
$("framepath").innerHTML="当前图：";const link=document.createElement("a");link.href="../"+f.file;link.textContent=f.file;$("framepath").append(link);
$("recordpath").textContent="";if(f.sourceRecord){const r=document.createElement("a");r.href="../"+f.sourceRecord;r.textContent="本帧生成来源与实际模型证据";$("recordpath").append(r)}else $("recordpath").textContent="生成记录暂缺";
$("model").textContent="实际模型："+(f.source?.actualModel||"未披露")+"；实际质量："+(f.source?.actualQuality||"未披露")+"。";
$("timing").textContent="每帧 "+current.durationMs+" ms；本动作 "+current.totalDurationMs+" ms。当前速度 "+$("speed").value+"×。";
$("availability").textContent="整包 "+manifest.presentFrameCount+"/68 帧 · 本组 "+current.present+"/"+current.expected+" 帧。"+(current.present<current.expected?"缺帧以提示显示，未补造帧。":groupReviewComplete()?"本组逐帧与连续播放已验看。":"本组文件齐全，连续播放待验看。");
window.previewState={group:current.id,frame:index+1,playing,speed:Number($("speed").value),frameChanges};
}
function pause(){playing=false;$("play").textContent="播放";accum=0;lastTime=null;render()}
function step(delta){pause();index=(index+delta+current.expected)%current.expected;render()}
$("play").onclick=()=>{playing=!playing;$("play").textContent=playing?"暂停":"播放";lastTime=null;accum=0;render()};
$("prev").onclick=()=>step(-1);$("next").onclick=()=>step(1);
range.oninput=()=>{const requested=Number(range.value)-1;pause();index=requested;render()};
groupEl.onchange=()=>{pause();current=manifest.groups.find(g=>g.id===groupEl.value);index=0;render()};
$("speed").onchange=()=>{accum=0;lastTime=null;render()};
$("light").onclick=()=>{$("stage").classList.remove("dark")};$("dark").onclick=()=>{$("stage").classList.add("dark")};
document.addEventListener("keydown",e=>{if(e.target.tagName==="SELECT"||e.target.tagName==="INPUT")return;if(e.key==="ArrowRight"){e.preventDefault();step(1)}if(e.key==="ArrowLeft"){e.preventDefault();step(-1)}if(e.code==="Space"){e.preventDefault();$("play").click()}});
image.onerror=()=>{image.hidden=true;empty.hidden=false;empty.textContent="当前图暂不可读取："+current.frames[index].file};
function tick(now){const elapsed=lastTime===null?0:Math.max(0,Math.min(now-lastTime,1000));lastTime=now;if(playing){accum+=elapsed*Number($("speed").value);const advances=Math.floor(accum/current.durationMs);if(advances>0){index=(index+advances)%current.expected;accum-=advances*current.durationMs;frameChanges+=advances;render()}}requestAnimationFrame(tick)}
for(const g of manifest.groups){const a=document.createElement("a");a.className="sheet panel";a.href="../"+g.contactSheet;a.target="_blank";const title=document.createElement("strong");title.textContent=g.label+" · 全帧排列";const img=document.createElement("img");img.src="../"+g.contactSheet;img.alt=g.label+"全帧检查图";img.loading="lazy";a.append(title,img);$("sheets").append(a)}
$("built").textContent="快照生成于 "+manifest.builtAt+"。允许重新运行 tools/build_package.py 更新落盘帧。客户端未验证。";
render();requestAnimationFrame(tick);
</script></body></html>'''
if __name__=="__main__":main()
