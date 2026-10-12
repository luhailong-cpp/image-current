from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
status=read(ROOT/'status.json');counts=status['counts']
audit=read(ROOT/'audit/eight-direction-paired-grounding.json')
rows=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'runtime').rglob('*.png'))]
assert len(rows)==196
(ROOT/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['file']}\n" for r in rows),encoding='utf-8')
old={r['file']:r['sha256'] for r in read(ROOT/'accepted-version.json')['frames']}
changed=[r for r in rows if old.get(r['file'])!=r['sha256']]
video_path=ROOT/'audit/video-axis-current-closeout.json'
video=read(video_path) if video_path.exists() else None
video_section=''
limb_path=ROOT/'audit/full-limb-current-closeout.json'
limb=read(limb_path) if limb_path.exists() else None
limb_section=''
if limb:
 repaired='、'.join(r['slot'] for r in limb['changedFrames'])
 limb_section=f'''## 最新完整手脚复核

本轮对全部196张原图检查肩肘腕、握持、髋膝踝和脚掌方向；修正6张孤立跳动的右空手：{repaired}。每张修后由主代理查看当前原图，保留已修好的腿脚和左手持弓。其余190张（含68张战斗帧）保留。本轮记录见[完整手脚复核](audit/full-limb-current-closeout.json)。

用户随后询问是否已改60ms/帧；实际检查仍为75ms/帧，已提出60/75选择，尚未收到选择，本轮未改时长。当前时长事实和待同步文件见[时长核对](audit/timing-clarification-20261005.json)。

NW被怀疑换支撑腿的01/02→03/04、10→11段重新沿可见大腿、膝、靴和遮挡关系复核，未确证换腿，腿图保留。髋根仍有遮挡，不能宣称解剖同脚追踪完全确认，详见[NW专项记录](audit/NW-full-support-chain-review.json)。正常倍速实播及客户端接地仍未验收。

'''
if video:
 repaired='、'.join(r['slot'] for r in video['changedFrames'])
 video_section=f'''## 前一轮视频反馈修订（历史）

前一轮结合用户视频连续帧和当时八方向128张原图，修订 {len(video['changedFrames'])} 张：{repaired}。具体修正和当时文件校验值见[历史视频对照记录](audit/video-axis-current-closeout.json)。当前文件以最新完整手脚复核及SHA256SUMS为准。

参考只用于判断腿部前后摆动和鞋掌朝向，保留本角色已确认美术。参考人物较小且有遮挡，不能据此证明细小鞋底形状、世界地面锁定或正常倍速实播已验收。

'''
def pairs_text(pairs):return ' → '.join('/'.join(f'{int(i):02d}' for i in pair) for pair in pairs)
table=[];detail=[]
for item in audit['reviews']:
 d=item['review'];direction=item['direction'];orders=d.get('supportOrder') or {}
 if not orders:
  for s in d.get('segments',[]):
   orders[{'left':'L','right':'R'}.get(s['foot'],s['foot'])]=[x['frames'] for x in s['positions']]
 if not orders:
  orders={name:s['pairs'] for name,s in zip(['A','B'],d.get('intendedSegments',[]))}
 labels=['A','B'] if direction in ['E','W'] else ['左','右']
 values=list(orders.values()) if direction=='W' else [orders.get('L',[]),orders.get('R',[])]
 table.append(f"| {direction} | {labels[0]}：{pairs_text(values[0])} | {labels[1]}：{pairs_text(values[1])} |")
 issues=d.get('remainingIssues') or d.get('remainingNotPassed') or d.get('unresolvedObservations') or d.get('limitations') or d.get('remaining') or []
 if isinstance(issues,dict):issues=[str(k)+': '+str(v) for k,v in issues.items()]
 if isinstance(issues,str):issues=[issues]
 detail.append(f"- {direction}：[逐帧记录]({item['file']})。"+('；'.join(str(i) for i in issues) if issues else '逐帧静态检查已记录；实播及客户端仍未验收。'))
timing={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'run':{'frameMs':75,'frameDurationsMs':[75]*16,'cycleMs':1200,'slowFrameMs':300,'slowCycleMs':4800,'availableNormalCycleMs':[1200],'extraLoopPauseMs':0,'formalClientTimingConfirmed':False},'hit':{'frameMs':40,'cycleMs':240,'peakFrame':3},'attack':{'frameMs':30,'cycleMs':360,'fullDrawFrame':6,'releaseFrame':7},'cast':{'frameMs':45,'cycleMs':720,'fullDrawFrame':9,'releaseFrame':10},'clientIntegration':'not_integrated'}
(ROOT/'animation-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
text=f"""# 09竹弓少女 · 当前修订交付

更新：{datetime.now(timezone.utc).isoformat()}。

[打开动作预览](preview/index.html) · [八方向1200ms总览](preview/qa/run-eight-directions-1200.apng)

本轮按最新“直脚着地两帧，再旁边点两帧，依次过渡”要求修改跑步。以同脚连续8张为目标，分为前落地、近身承重、身体经过、后蹬四段，每段2帧；按行进轴与透视改变相对位置，未用复制帧或移动整张图替代动作。各方向的实际证据和局限分别记录，侧向遮挡未被冒充为同脚确认。与此前认可快照相比，当前共{len(changed)}张图片发生必要修订；旧认可不自动适用于新图。

{limb_section}{video_section}## 实际接地帧号

以下每格按四个位置段列出；斜线两侧各是一张不同的独立帧。左右标签为设计标注；E/W/NW髋根存在遮挡，同一解剖脚的连续身份不能仅靠屏幕左右位置确认。每对150ms，每组8帧600ms，整圈16帧1200ms。原图证据、当前SHA和具体空间观察见[八方向记录](audit/eight-direction-paired-grounding.json)。

| 方向 | 支撑序列一 | 支撑序列二 |
|---|---|---|
{chr(10).join(table)}

## 文件和验证

- 正式资源196张：跑步8方向各16张；受击E/W各6张，普攻各12张，施法各16张。全部1024×1024 RGBA。
- 当前技术检查{counts['technicalChecksPassed']}/196，原生分辨率来源{counts['nativeResolutionEvidencePassed']}/196，来源链{counts['sourceEvidencePassed']}/196。没有用镜像补方向、插值或重复图补帧。检查结果见[status.json](status.json)。
- [SHA256SUMS.txt](SHA256SUMS.txt)、[manifest.json](manifest.json)、selection和逐图generation记录绑定当前文件。修改图像后旧SHA审阅不再适用。
- 正常跑步75ms/帧、1200ms/圈，慢放300ms/帧、4800ms/圈，无额外首尾停顿。旧快速选项已移除。受击40ms、普攻30ms、施法45ms保持原时长；本轮未改战斗PNG。
- 正常/慢速跑步APNG及HTML均使用准确时长，播放器循环边界用VM模拟检查。图片预览带当前SHA版本参数，避免加载之前的同名帧。
- 当前196张均绑定当前SHA审阅记录，明确视觉通过登记{counts['visualPassedSlots']}/196；动态通过{counts['dynamicPassedSequences']}/14。帧数齐全、技术通过与动态观感通过是不同结论。

## 尚未通过的范围

没有完成正常倍速浏览器实播和游戏内地面/位移匹配验收。此前浏览器工具对本地file页面的导航被安全策略拒绝，未绕过；因此只报告原图、256px接触表及离线时间检查的实见结果，不能声称游戏内滑步完全消除。

{chr(10).join(detail)}

客户端D:/work/mmorpg-client只读检查发现v14目前仍有30ms/480ms校验，且位移步频受Fps/ReferenceRunSpeed影响。本包尚未接入客户端；复制资源之外还需同步时长校验和位移关系。[只读证据](audit/client-readonly-check.json)。

## 模型、根点与保留规则

本批配置目标GPT Image2.5 Sunburst/max，使用宿主内置image_gen。工具未提供型号/质量选择器及实际返回值，实际model/quality均按null未确认记录；配置或提示词不是已锁定型号的证据。逐图请求、回执、参考SHA、生成时间、原生尺寸与来源路径均保留。

导出为原生完整画布等比缩至1024，无逐帧包围盒缩放、整图位移或最低脚对齐；仅透明度≤2/255的噪点归零。预览地面线是诊断线，不是已完成的游戏地面标定。本角色目录内原稿和拒稿仅保留来源文字记录，当前正式图片与必要预览/接入文件保留；宿主生成缓存位于本目录之外，本轮未删除。
"""
(ROOT/'MERGE_HANDOFF.md').write_text(text,encoding='utf-8')
receipt={'atUtc':datetime.now(timezone.utc).isoformat(),'runtimeFrames':196,'changedSinceHistoricalAcceptance':changed,'historicalAcceptanceRewritten':False,'latestRequirementFile':'audit/latest-grounding-requirement.json','pairedReviewFile':'audit/eight-direction-paired-grounding.json','preview':'preview/index.html','technicalChecksPassed':counts['technicalChecksPassed'],'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated'}
if video:
 receipt['latestVideoAxisRevision']={'file':'audit/video-axis-current-closeout.json','sha256':sha(video_path),'changedFrames':video['changedFrames'],'retainedFrames':video['retainedFrames']}
if limb:
 receipt['latestFullLimbRevision']={'file':'audit/full-limb-current-closeout.json','sha256':sha(limb_path),'changedFrames':limb['changedFrames'],'retainedFrames':limb['retainedFrames']}
(ROOT/'audit/current-revision-delivery.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'runtimeFrames':196,'changedImages':len(changed),'handoff':'MERGE_HANDOFF.md','dynamicVisualAcceptance':False}))
