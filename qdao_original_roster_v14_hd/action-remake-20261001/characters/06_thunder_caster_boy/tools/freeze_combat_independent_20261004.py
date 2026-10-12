"""Freeze the independently inspected 68 combat PNGs and factual source checks."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--e09sha',required=True);p.add_argument('--e10sha',required=True)
args=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for frame,expected in [(9,args.e09sha),(10,args.e10sha)]:
    assert sha(ROOT/'runtime/attack/E'/f'{frame:02d}.png')==expected, 'E09/10 have changed since actual independent inspection'
notes={
('hit','E'):'近侧右手持杖、远侧左手持符牌；后仰/缓冲中双靴仍朝东，02 抬起前靴而没有外拧。',
('hit','W'):'近侧左手持符牌、远侧右手持杖；反冲中双靴朝西。00 与 02 已额外查看完整单帧，握持清楚。',
('attack','E'):'近侧右臂持杖、远侧左手持符牌；脚尖朝东。00/09/10/11 换手错误经独立 AI 重绘后再次实际查看。06 前伸出手，随后收招。',
('attack','W'):'近侧左手持符牌、远侧右手持杖；脚尖朝西。06 完整单帧可见出手手臂与杖柄连贯，08–11 收招。',
('cast','E'):'近侧右手持杖、远侧左手持符牌；脚尖朝东。09 释放与 12–15 收势完整单帧已额外查看，未见换手。',
('cast','W'):'近侧左手持符牌、远侧右手持杖；脚尖朝西。09 释放及 11/12 完整单帧已额外查看，11/12 鞋尖向左、鞋跟在右。'
}
full={('hit','E'):[2],('hit','W'):[0,2],('attack','E'):[0,1,6,9,10,11],('attack','W'):[6],('cast','E'):[9,12,13,14,15],('cast','W'):[9,11,12]}
frames=[];blocking=[];sourceWarnings=[]
for action,count in [('hit',6),('attack',12),('cast',16)]:
    for direction in ['E','W']:
        for frame in range(count):
            f=ROOT/'runtime'/action/direction/f'{frame:02d}.png';j=f.with_name(f.name+'.generation.json')
            meta=read(j);im=Image.open(f);current=sha(f);derived=meta.get('derivedFrom',[])
            checks={'runtimeShaMatchesSidecar':current==meta.get('sha256'),'rgba1024':im.size==(1024,1024) and im.mode=='RGBA','transparentPixels':im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0}
            sources=[]
            for src in derived:
                sr=ROOT/src['generationRecord'];record=read(sr)
                q=ROOT/src['file'];location='character-work'
                if not q.exists():
                    q=Path(record.get('evidence',{}).get('hostOutputPath',''))
                    location='host-generated-native'
                exists=q.is_file()
                source={'file':src['file'],'sha256':src['sha256'],'generationRecord':src['generationRecord'],'generationRecordSha256':sha(sr),'recordShaMatches':record.get('sha256')==src['sha256'],'nativeImageAvailable':exists,'nativeImageLocation':location if exists else None,'nativeShaMatches':sha(q)==src['sha256'] if exists else None,'actualModel':record.get('actualModel'),'actualQuality':record.get('actualQuality')}
                if exists:
                    ni=Image.open(q)
                    source['nativeSize']=list(ni.size)
                    source['nativeFullCanvasExportMatches']=ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()==im.tobytes()
                else:
                    sourceWarnings.append({'file':f.relative_to(ROOT).as_posix(),'reason':'原生图片不在当前工作目录或宿主原路径；文字来源记录仍保留。'})
                if source['recordShaMatches'] is False or source['nativeShaMatches'] is False or source.get('nativeFullCanvasExportMatches') is False:
                    blocking.append({'file':f.relative_to(ROOT).as_posix(),'issue':'来源链或固定整幅导出核对失败','source':source})
                sources.append(source)
            if not all(checks.values()) or not sources:
                blocking.append({'file':f.relative_to(ROOT).as_posix(),'issue':'尺寸/透明/SHA/来源记录检查未通过','checks':checks})
            frames.append({'file':f.relative_to(ROOT).as_posix(),'sha256':current,'action':action,'direction':direction,'frame':frame,'visualInspection':'contact sheet plus full-frame inspection' if frame in full[(action,direction)] else 'full contact-sheet cell inspection','staticObservation':notes[(action,direction)],'technicalChecks':checks,'sources':sources})
assert len(frames)==68
report={'schemaVersion':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_ew independent subagent','scope':'68 combat frames only; static inspection','staticVisualInspectionCompleted':True,'dynamicPlaybackReviewed':False,'clientIntegrated':False,'method':'实际查看全部六组联系表中的 68 张图片；对重点帧另看完整 1024 图。原联系表 68 个来源 SHA 在修复前与正式图一致；随后对 E00/09/10/11 新图完整查看。当前报告重新计算所有 68 个正式 SHA 与逐图来源。','observations':[{'action':a,'direction':d,'observation':n} for (a,d),n in notes.items()],'resolvedIssues':[{'files':['runtime/attack/E/00.png','runtime/attack/E/09.png','runtime/attack/E/10.png','runtime/attack/E/11.png'],'issue':'原图近侧解剖右手错持符牌','resolution':'各自 AI 重绘为近侧右手持杖、远侧左手持符牌；新的 4 张正式图已实际查看。'}],'limitations':['本报告是静态逐图检查，不代表完整正常/慢放循环验收。','E11 新稿头部位置与旧稿存在约 30px 高度变化，现整体更接近 E00/01；循环衔接由主窗口单独复核。','宿主未披露实际型号及质量；配置目标 GPT Image 2.5 Sunburst/max 不当作实测。','当前无客户端，未接入或运行客户端。'],'sourceWarnings':sourceWarnings,'unresolvedBlockingIssues':blocking,'frames':frames}
out=ROOT/'review/combat_final_independent_20261004.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 06 战斗 68 帧独立静态复核','', '本报告逐图核对受击 12、普攻 24、施法 32 张当前正式图。只证明静态核对；未代填动态循环或客户端验收。','', '## 观察','']+[f"- {a}/{d}：{n}" for (a,d),n in notes.items()]
lines+=['','## 已修正问题','','普攻 E00/09/10/11 的近侧右手错持符牌已各自通过 AI 重绘修复；四张新图已重新实际查看。','','## 当前限制','']+['- '+x for x in report['limitations']]
lines+=['',f"当前未解决阻断问题：{len(blocking)} 项。来源图片不可用提示：{len(sourceWarnings)} 项。",'','## 当前正式图 SHA','','| file | SHA256 |','| --- | --- |']+[f"| {x['file']} | {x['sha256']} |" for x in frames]
out.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out),'sha256':sha(out),'frameCount':len(frames),'blockingCount':len(blocking),'sourceWarnings':len(sourceWarnings),'blocking':blocking},ensure_ascii=False))

