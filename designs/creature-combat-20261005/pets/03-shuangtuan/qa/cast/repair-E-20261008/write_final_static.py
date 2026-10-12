from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
BASE=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
QA=BASE/'qa/cast/repair-E-20261008'
now=datetime.now(timezone.utc).isoformat()
frames=[]
for n in range(1,17):
    p=BASE/f'runtime/cast/E/{n:02d}.png'
    im=Image.open(p);a=im.getchannel('A');h=hashlib.sha256(p.read_bytes()).hexdigest()
    record=json.loads((BASE/f'records/cast/E/{n:02d}.generation.json').read_text(encoding='utf-8-sig'))
    assert h==record['sha256'] and im.mode=='RGBA' and im.size==(1024,1024)
    frames.append({'frame':n,'file':p.relative_to(BASE).as_posix(),'sha256':h,'visualStatus':'passed-static','identity':'existing pearl-gray round-eared ferret retained','anatomy':'four limbs, one curled tail, front/hind limb roles retained','edgeStatus':'no substantive body/limb/tail clipping observed; whisker endpoints inside canvas after localized repair' if n in [5,7,8,12,13] else 'no new substantive clipping observed in static review','rightEdgeAlphaAbove127':sum(a.getpixel((1023,y))>127 for y in range(1024)),'generationRecord':f'records/cast/E/{n:02d}.generation.json'})
assert len({r['sha256'] for r in frames})==16
report={'reviewedAt':now,'action':'cast','direction':'E','status':'passed-static','scope':'Actual full-frame image inspection and final current 16-frame contact sheet; not realtime playback or game integration','contactSheet':'qa/cast/repair-E-20261008/E-contact-repaired.png','technicalRecord':'qa/cast/repair-E-20261008/technical.json','frames':frames,'unresolvedStaticIssues':[],'limits':['Tiny low-alpha fringe/speckles may touch canvas; alpha extent is not itself proof of subject clipping.','Normal and slow realtime playback verification belongs to root report, not this static review.','Client not read, integrated or tested.']}
(QA/'final-static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
edge={'reviewedAt':now,'status':'passed-after-localized-whisker-repair','findingBeforeRepair':'Fine continuous right whisker curves genuinely reached and were cut at canvas boundary in E05/07/08/12/13. Earlier full-frame provisional description as mere edge pixels was insufficient.','findingAfterRepair':'Final full-frame and contact-sheet inspection: shortened right whiskers terminate inside canvas, no retained substantive whisker cutoff; body and four-limb roles preserved.','frames':[r for r in frames if r['frame'] in [5,7,8,12,13]],'notChangedByReviewer':'No runtime pixels edited or generated during final static inspection.'}
(QA/'edge-review.json').write_text(json.dumps(edge,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# cast E 最终静态验收','',f'检查时间：{now}。最终16帧静态合格。','', '已实际查看全帧与最终接触表；边缘窄修后的 E05/07/08/12/13 右侧胡须端点已回到画内。四肢、一尾、圆耳、饰品、既定前爪施法阶段及后足支撑保持。细微半透明外缘与散点不等于主体截断。','', '原 E05/07/08/12/13 的连续细胡须确实在画布边线处被截断，已由根/另一代理分别执行真实AI窄修。本次复核未修改runtime。','', '|帧|当前 SHA256|静态结论|','|---|---|---|']
lines += [f"|{r['frame']:02d}|`{r['sha256']}`|合格|" for r in frames]
lines += ['','本目录 E-contact-repaired.png、technical.json 已按上述当前16张重新生成。final-static-review.json 的逐图SHA供根验收导入；旧 review.md 是后足修复阶段记录，边缘结论已由本报告和 edge-review.json 更新。','', '动态连播、正常/慢放播放验收单独由根窗口记录，本报告不据静态图宣称动态通过。客户端未读取、未接入、未验证。']
(QA/'final-static-review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(QA/'edge-review.md').write_text('# cast E 右边缘定点复核\n\n原05/07/08/12/13右侧连续细胡须实质触边截断，不能仅按少量alpha像素排除问题。真实AI窄修后，已实际查看最终全图和当前16帧接触表：胡须端点完整回到画内，主体、四足支撑与施法阶段保留。\n\n逐图当前SHA与证据见 edge-review.json；完整静态验收见 final-static-review.json/md。没有在本静态复核中修改runtime或新增生图。\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'frames':len(frames),'edgeFrames':[r['frame'] for r in edge['frames']]}))
