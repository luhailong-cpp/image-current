from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
inventory_bytes = (R/'delivery-current.json').read_bytes()
inventory_sha = hashlib.sha256(inventory_bytes).hexdigest()
delivery = json.loads(inventory_bytes)
expected = {'run':(8,16,60), 'hit':(2,6,40), 'attack':(2,12,30), 'cast':(2,16,45)}
slots=[]; pixels=set(); file_shas=set(); groups=delivery['groups']; errors=[]
for group, frames in groups.items():
    action, direction=group.split('/')
    n=expected[action][1]
    assert [f['frame'] for f in frames] == list(range(1,n+1)), group
    for f in frames:
        p=R/f['file']; record=R/f['generationRecord']
        meta=json.loads(record.read_text(encoding='utf-8'))
        im=Image.open(p); im.load()
        assert im.mode=='RGBA' and im.size==(1024,1024), str(p)
        assert sha(p)==f['sha256']==meta['sha256'], str(p)
        assert im.getchannel('A').getextrema()==(0,255), str(p)
        solid=im.getchannel('A').point(lambda a:255 if a>=32 else 0)
        box=solid.getbbox()
        assert box and box[0]>0 and box[1]>0 and box[2]<1024 and box[3]<1024, str(p)
        native=meta['nativeEvidence']; native_record=R/native['generationRecord']
        native_meta=json.loads(native_record.read_text(encoding='utf-8-sig'))
        assert native['size']==[1254,1254] and native['sha256']==f['nativeSHA']
        assert sha(native_record)==native['recordSHA256'], str(native_record)
        assert meta['sourceFrame']==f['sourceFrame'] and meta['playbackFrame']==f['frame']
        assert meta['frameDurationMs']==expected[action][2]==f['durationMs']
        pixel_sha=hashlib.sha256(im.tobytes()).hexdigest()
        assert pixel_sha not in pixels and f['sha256'] not in file_shas, group
        pixels.add(pixel_sha);file_shas.add(f['sha256'])
        slots.append({'action':action,'direction':direction,**f,'status':'production-art-export','size':[1024,1024],'mode':'RGBA','pixelSHA256':pixel_sha,'alpha32BBox':list(box),'nativeGenerationRecord':native['generationRecord'],'promptReferenceFromNativeRecord':native_meta.get('prompt')})
assert len(slots)==196 and len(groups)==14
for action,(directions,n,ms) in expected.items():
    assert sum(k.startswith(action+'/') for k in groups)==directions
counts={a:{'expected':dirs*n,'formalExports':dirs*n,'staticReview':'completed','frameMs':ms,'cycleMs':ms*n} for a,(dirs,n,ms) in expected.items()}
manifest={'character':'10_crimson_spear_girl','updatedAt':datetime.now(timezone.utc).isoformat(),'status':'production-art-export-complete','expectedTotal':196,'nativeCandidateTotal':196,'formalExportTotal':196,'missingTotal':0,'counts':counts,'targetCanvas':[1024,1024],'rootTarget':[512,942],'rootStatus':'offline fixed group registration reviewed; client placement untested','runFrameMs':60,'runCycleMs':960,'sourceOrderAppliedOnce':True,'clientIntegrated':False,'clientRuntimeTested':False,'userFinalAcceptance':False,'configTarget':'GPT Image 2.5 Sunburst / max','actualModel':None,'actualQuality':None,'toolRoute':'builtin','currentInventory':'delivery-current.json','historicalSourcePolicy':'Native/intermediate images are removed after final export validation; native SHA and original generation text records remain. Runtime PNGs are current assets.','slots':slots}
write(R/'manifest.json',manifest)
write(R/'validation.json',{'status':'passed','inventoryFile':'delivery-current.json','inventorySHA256':inventory_sha,'runtimeCount':196,'decoded1024RGBA':196,'uniqueFileSHA':196,'uniquePixelSHA':196,'transparentAlpha':196,'noAlpha32EdgeContact':196,'native1254EvidenceAndRecordHashesVerified':196,'sourceOrderAppliedOnce':True,'errors':errors,'staticArtReview':'all selected frames reviewed in directional contact sheets and targeted native views; see FINAL_REVIEW.md','localPlaybackReview':'browser rendering and stepping checked; deterministic timing test in preview/timing-verification.json','clientAcceptance':False,'userFinalAcceptance':False})

try: font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
except OSError: font=ImageFont.load_default()
for group, frames in groups.items():
    width=256; cell_h=292; canvas=Image.new('RGB',(width*4,cell_h*((len(frames)+3)//4)),'#e9e8e1'); draw=ImageDraw.Draw(canvas)
    for j,f in enumerate(frames):
        x=(j%4)*width;y=(j//4)*cell_h
        im=Image.open(R/f['file']).resize((width,width),Image.Resampling.LANCZOS)
        canvas.paste(im,(x,y),im); draw.line((x,y+942/4,x+width,y+942/4), fill='#8b9b91')
        draw.text((x+8,y+260),f"{group}/{f['frame']:02} · source {f['sourceFrame']:02}",font=font,fill='#263b34')
    out=R/'preview'/(group.replace('/','-')+'-contact.jpg');canvas.save(out,quality=94)
    write(Path(str(out)+'.generation.json'),{'file':out.relative_to(R).as_posix(),'sha256':sha(out),'operation':'current runtime full-canvas contact sheet; playback order','derivedFrom':[{'file':f['file'],'sha256':f['sha256'],'generationRecord':f['generationRecord']} for f in frames]})

chosen=[('run/S',4,'跑步'),('hit/E',3,'受击'),('attack/E',6,'普攻'),('cast/E',9,'施法')]
canvas=Image.new('RGB',(1600,450),'#e9e8e1');draw=ImageDraw.Draw(canvas);sources=[]
for j,(group,frame,label) in enumerate(chosen):
    f=groups[group][frame-1];im=Image.open(R/f['file']).resize((400,400),Image.Resampling.LANCZOS)
    canvas.paste(im,(j*400,0),im);draw.text((j*400+18,410),label,font=font,fill='#263b34');sources.append({'file':f['file'],'sha256':f['sha256'],'generationRecord':f['generationRecord']})
out=R/'preview/current-four-actions.jpg';canvas.save(out,quality=94)
write(Path(str(out)+'.generation.json'),{'file':out.relative_to(R).as_posix(),'sha256':sha(out),'operation':'current runtime full-canvas thumbnails','derivedFrom':sources})

if not (R/'full-limb-review-20261004/SCOPE.md').exists():
    handoff='''# 赤枪少女 · 成品交接

    本轮196张动作制作版已完成、导出并进行本机离线检查。当前素材入口为 `runtime/`，逐图清单为 `manifest.json` / `delivery-current.json`。尚未接入客户端或进行游戏内验收。

    | 动作 | 方向 | 每方向帧数 | 每帧 | 一圈 |
    |---|---|---:|---:|---:|
    | 跑步 | N / NE / E / SE / S / SW / W / NW | 16 | 60ms | 960ms |
    | 受击 | E / W | 6 | 40ms | 240ms |
    | 普攻 | E / W | 12 | 30ms | 360ms |
    | 施法 | E / W | 16 | 45ms | 720ms |

    跑步8方向均匀16×60ms，无阶段加权、无圈尾停顿；已移除480/640/720/800跑步档位。普攻第06帧为接触标记，施法第09帧为释放标记。运行目录编号01起已是最终播放顺序，不可再次应用旧N/S源帧重排；sourceFrame仅用于来源追溯。

    所有成品为1024×1024 RGBA。原生证据为1254×1254。既有成品保留原配准；本次基于已配准成品重绘的新图整画布1254→1024，不重复旧缩放。个别生成时发生整体缩放漂移的独立新姿势，按头饰、髋部、枪身锚点作有记录的等比配准；未按脚底最低点贴线。每张成品的实际处理见对应generation.json。没有镜像补方向、复制帧或插值补数。接入时仍需验证游戏世界坐标与地面层级。

    当前全动作预览 `preview/index.html`，八方向同屏 `preview/all-directions.html`，单方向跑步逐帧检查 `preview/timing-grounding.html`；支持正常1×、慢放¼、暂停、逐帧。14张当前联系表及四动作概览均从runtime生成。像素与来源校验见 `validation.json`，时序测试见 `preview/timing-verification.json`，美术检查范围见 `FINAL_REVIEW.md`。

    接地修订逐方向参照用户确认的09竹弓少女：同一只脚连续支撑8帧，沿运动轴相对髋部逐步向后推进4个空间位置，每处2张独立姿势；按连续四个位置各两张推进，随后换另一脚8帧。最后位置允许真实前掌支撑。核对脚尖方向、腿部轴线、手数、握枪和枪尖完整性。角色身份、红白金服饰和双手长枪保留，正确帧保留。各方向的起止播放位见RUN_CONTACT_PLAN.json；接地修订来源和重排记录见run-contact-revision-20261004/publish-report.json。

    本轮在原接地节奏上按新视频的运动平面定向修正腿脚轴线：NE15/16/01校正同一左摆动脚鞋尖突然转向镜头的问题，SW08、W06、NW10/11/12修正对应腿脚朝向与相邻帧衔接。保留各帧原支撑关系、双手长枪与角色构图；具体选稿和独立生成来源见run-axis-revision-20261004/publish-report.json及各方向审查记录。视频人物较小，仅用于运动平面和衔接参考，不宣称能测得精确踝角。正确帧保持，仍为16×60ms。

    按用户素材保留要求，成品验证后清理本角色目录的原生、拒稿和加工中间图片；清理清单见 `retention-report.json`。提示词、提交参数、回执、原生SHA及逐图生成文字记录保留。历史文档中的native源文件路径仅作出处证据，不是当前加载依赖。当前正式引用只使用runtime和preview文件。外部原角色idle/旧walk、09参照和全局设计图均未更改。

    配置目标为GPT Image2.5 Sunburst/max；内置工具没有可用model/quality选择参数，也没有披露实际型号/质量，实际值标为未确认(null)，不将目标或提示词当作实际版本证据。未调用单独收费API/CLI。

    本任务只修改本角色目录，未修改客户端、其他角色、共享配置或Git状态。客户端目录存在，但未接入、未执行游戏内验收。
    '''
    (R/'MERGE_HANDOFF.md').write_text(handoff,encoding='utf-8')
    (R/'STATUS.md').write_text('# 赤枪少女 · 当前状态\n\n196/196张成品已导出，缺槽0；本机离线检查完成。跑步8方向统一16×60ms=960ms。本轮完成NE15/16/01、SW08、W06、NW10/11/12腿脚轴线定向修正，发布记录见run-axis-revision-20261004/publish-report.json。当前资源入口runtime/，全动作preview/index.html，八方向同屏preview/all-directions.html。客户端未接入。\n\n详见MERGE_HANDOFF.md、FINAL_REVIEW.md与validation.json。\n',encoding='utf-8')
    (R/'README.md').write_text('# 赤枪少女动作成品\n\n已完成196张1024×1024 RGBA动作制作版：八方向跑步128张，E/W受击12张、普攻24张、施法32张。跑步各方向960ms/圈。本轮腿脚轴线定向修正记录见run-axis-revision-20261004/publish-report.json。客户端尚未接入。\n\n- [八方向同屏](preview/all-directions.html)\n- [全动作预览](preview/index.html)\n- [单方向跑步逐帧检查](preview/timing-grounding.html)\n- [四动作概览](preview/current-four-actions.jpg)\n- [成品清单](manifest.json)\n- [接入与来源说明](MERGE_HANDOFF.md)\n- [检查记录](FINAL_REVIEW.md)\n- [像素和来源校验](validation.json)\n\n当前资源为runtime/；历史生成记录保留模型、质量、提示词、回执与原生SHA。旧源图清理后不再作为加载依赖。\n',encoding='utf-8')
print(json.dumps({'runtimeVerified':len(slots),'contactSheets':14,'errors':errors}))
