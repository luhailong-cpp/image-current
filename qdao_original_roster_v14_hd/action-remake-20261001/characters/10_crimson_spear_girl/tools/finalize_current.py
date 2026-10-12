from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'delivery-current.json').exists():
    import runpy
    runpy.run_path(str(ROOT/'tools/finalize_delivery.py'),run_name='__main__')
    raise SystemExit(0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8'))
expected={'run':(list(['N','NE','E','SE','S','SW','W','NW']),16,75),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
slots=[];errors=[];counts={};present=[]
for action,(directions,n,ms) in expected.items():
    counts[action]={'expected':len(directions)*n,'nativeCandidates':0,'candidateExports':0,'formalExports':0,'visualPassed':0,'dynamicPassed':0}
    for direction in directions:
        actual={f['frame']:f for f in data['groups'].get(action+'/'+direction,[])}
        for i in range(1,n+1):
            entry={'action':action,'direction':direction,'frame':i,'durationMs':ms,'timingStatus':'user-requested-1200ms-uniform' if action=='run' else 'specified-battle-timing','status':'missing','file':None,'sha256':None}
            if i in actual:
                f=actual[i];p=ROOT/f['url'][3:];record=Path(str(p)+'.generation.json')
                im=Image.open(p);im.load()
                if not record.exists():errors.append(str(record)+' missing')
                else:
                    meta=json.loads(record.read_text(encoding='utf-8-sig'))
                    recorded=meta.get('sha256') or meta.get('sha256Native')
                    if recorded and recorded.lower()!=sha(p):errors.append(str(p)+' SHA mismatch')
                if im.mode!='RGBA' or min(im.size)<1024:errors.append(str(p)+' native size or mode failed')
                entry.update(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),generationRecord=record.relative_to(ROOT).as_posix(),nativeSize=list(im.size),mode=im.mode,status='candidate-needs-visual-and-root-review',alphaExtrema=list(im.getchannel('A').getextrema()))
                if action=='attack' and i==6:entry['plannedEvent']='contact'
                if action=='cast' and i==9:entry['plannedEvent']='release'
                candidate=ROOT/'candidate'/action/direction/f'{i:02}.png'
                candidate_record=Path(str(candidate)+'.generation.json')
                if candidate.exists() and candidate_record.exists():
                    cm=json.loads(candidate_record.read_text(encoding='utf-8-sig'))
                    if any(x.get('sha256')==entry['sha256'] for x in cm.get('derivedFrom',[])):
                        entry['candidateExport']={'file':candidate.relative_to(ROOT).as_posix(),'sha256':sha(candidate),'status':'provisional-registration-not-approved'}
                        counts[action]['candidateExports']+=1
                counts[action]['nativeCandidates']+=1;present.append(entry)
            slots.append(entry)
manifest={'character':'10_crimson_spear_girl','updatedAt':datetime.now(timezone.utc).isoformat(),'status':'incomplete','expectedTotal':196,'nativeCandidateTotal':len(present),'formalExportTotal':0,'visualPassedTotal':0,'dynamicPassedTotal':0,'missingTotal':196-len(present),'counts':counts,'targetCanvas':[1024,1024],'rootTarget':[512,942],'rootStatus':'unverified; no lowest-foot alignment or per-frame bbox scaling applied','clientIntegrated':False,'clientRuntimeTested':False,'configTarget':'GPT Image 2.5 Sunburst / max','actualModel':None,'actualQuality':None,'toolRoute':'builtin','slots':slots}
manifest['candidateExportTotal']=sum(c['candidateExports'] for c in counts.values())
write(ROOT/'manifest.json',manifest)
write(ROOT/'validation.json',{'candidateCount':len(present),'decodedPngCount':len(present),'nativeSizeAndAlphaChecks':'passed' if not errors else 'failed','sourceRecordChecks':'passed' if not errors else 'failed','errors':errors,'visualAcceptance':False,'dynamicAcceptance':False,'clientAcceptance':False})
selected=[]
for key,number,label in [('run/E',4,'跑步 · 腾空候选'),('hit/E',3,'受击 · 后仰候选'),('attack/E',6,'普攻 · 前刺候选'),('cast/E',9,'施法 · 释放候选')]:
    f=next((f for f in data['groups'].get(key,[]) if f['frame']==number),None)
    if f:selected.append((f,label))
canvas=Image.new('RGB',(1600,480),'#e8e7df');draw=ImageDraw.Draw(canvas)
try:font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
except OSError:font=ImageFont.load_default()
for j,(f,label) in enumerate(selected):
    im=Image.open(ROOT/f['url'][3:]);im.thumbnail((400,400));canvas.paste(im,(j*400,0),im)
    draw.text((j*400+20,416),label,fill='#293b36',font=font)
out=ROOT/'preview'/'current-four-actions.jpg';canvas.save(out,quality=94)
write(Path(str(out)+'.generation.json'),{'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'operation':'preview-only full-canvas thumbnail composition','derivedFrom':[{'file':f['url'][3:],'sha256':f['sha256'],'generationRecord':f['url'][3:]+'.generation.json'} for f,_ in selected]})
lines=['# 10 赤枪少女 · 当前交接','',f'当前保留 {len(present)}/196 个槽位的原生候选，尚缺 {196-len(present)} 槽。正式导出、完整美术验收、动态验收均未完成，不可直接替换客户端。','', '| 动作 | 已生成候选 | 目标 | 正式导出 |','|---|---:|---:|---:|']
for a,c in counts.items():lines.append(f'| {a} | {c["nativeCandidates"]} | {c["expected"]} | 0 |')
lines+=['','## 文件与来源','', '逐槽路径、SHA、缺口、时长和命中/释放标记见 manifest.json；像素解码及来源校验见 validation.json。动态候选入口 preview/index.html 支持1200ms跑步正常播放、正常速度/慢速及逐帧；含缺口的组并非完整动作。preview/timing-grounding.html固定16帧×75ms=1200ms，保留慢放、暂停、逐帧；缺槽禁播整圈，旧速度档已移除。四动作概览 preview/current-four-actions.jpg。各生成PNG旁均有来源记录，提示词/回执保留在generation、hit-work、attack-work、cast-work。','', '目标为GPT Image2.5 Sunburst/max；当前内置工具未开放model/quality参数，也未在结果披露实际型号/质量，均标null。未调用收费API/CLI。','', '## 合并边界与未完成','', '只合并本角色目录；本聊天未改共享配置、分支、暂存区、提交或其他角色。旧八向128帧walk和8帧idle仍保留原处，只读审计见PRIOR_INVENTORY.json；旧run-correction/combat本角色没有可复用的已完成修正PNG。','', '正式目标1024×1024 RGBA、虚拟根点(512,942)，原生候选1254×1254。根锚与一致比例尚未通过，未以逐帧最低脚贴地或包围盒缩放掩盖漂移。跑步E/S/W/N/NW已建立16帧当前选择并导出固定整方向配准候选，继续核对脚尖朝向、左右腿交替/肩肘变化及落地感。战斗68槽原生候选已齐，仍做局部脚向修复、固定根锚和顺序验收。详细问题见RUN_REVIEW.md、hit-work、attack-work/REVIEW.md与cast-work/STATUS.json。','', '历史生成失败回执保留文字，当前内置生图可用。正在完成NE/SW并完成SE既有帧的交替支撑修正，现有正确帧保留，错误处定向修复；缺槽没有占位PNG。最新脚向要求见LATEST_REQUIREMENTS_20261003.md，不再把任何其他角色整套或垂直方向视作已正确模板。','', '本机D:/work/mmorpg-client目录存在（2026-10-03只读确认）；本任务只修改本角色素材目录，未接入客户端或进行游戏内验收。']
(ROOT/'MERGE_HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'STATUS.md').write_text('\n'.join(lines[:8+len(counts)])+'\n\n当前状态：制作未完成，详见MERGE_HANDOFF.md与manifest.json。\n',encoding='utf-8')
print(json.dumps({'candidateCount':len(present),'missing':196-len(present),'errors':errors},ensure_ascii=False))
