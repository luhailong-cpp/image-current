from pathlib import Path
from datetime import datetime,timezone
import json
O=Path(__file__).resolve().parent
p=O/'summary.json';d=json.loads(p.read_text(encoding='utf-8'))
findings={
 ('r03_c10','r03_c11'):'四段石板缝、树叶与地面轮廓跨共享边连续；未见沿共享边的突变带。r03_c10内部旧石面直带待修不受此结果影响。',
 ('r03_c12','r03_c13'):'四段金玉饰边、陶罐外轮廓及石阶线连续。',
 ('r03_c13','r04_c13'):'四段罐身、台阶、红柱与石栏线连续。',
 ('r03_c14','r04_c14'):'四段石栏、花叶、水纹连续，未见新的水平硬切。',
 ('r04_c12','r04_c13'):'四段陶罐底边、地砖、金色屋脊及蓝瓦槽线连续。',
 ('r04_c12','r05_c12'):'四段红木构件、檐头、瓦槽与金边连续。',
 ('r05_c12','r05_c13'):'四段墙面、木框、台阶及地砖线连续。'
}
for e in d['newEdgeReviews']:
 e.update(status='shared_edge_local_visual_passed',actuallyViewed=True,viewedAtOriginalPixelScale=True,finding=findings[tuple(e['tiles'])])
 for s in e['segments']:s.update(actuallyViewed=True,status='local_visual_passed')
for e,f in zip(d['newCrossReviews'],['陶罐轮廓、蓝饰与石地连续。','灯笼、飘带、石栏和植株交汇连续。','蓝瓦、金色屋脊与墙面交汇连续。']):
 e.update(status='local_junction_visual_passed',actuallyViewed=True,viewedAtOriginalPixelScale=True,finding=f)
d.update(reviewCompletedAtUtc=datetime.now(timezone.utc).isoformat(),newEdgePairCount=7,newSeamSegmentCount=28,newCrossCount=3,existingOpenFindingsRetained=True,reviewScope='Complete-source adjacent borders not inspected by previous four local groups; all inspected pixels unchanged from baseline; local pass does not accept tile internals or whole map')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# 八仙岛东北增量接缝检查

当前19坐标的选用核心和覆盖与上批相同：279个1024核心、16张完整覆盖候选、3个部分覆盖坐标，正式验收为0。319张当前选用源图、覆盖图和成图的SHA256均未变化；海岸选择文件只有元数据变化，有效核心矩阵与成图路径不变。

原15对共享边沿用既有检查结果，包含原未通过问题。本次补查此前未覆盖的7对共享边，28张原像素接缝裁片及3个四交汇实际查看后，局部轮廓与材质接续通过。未重建既有8192局部拼接，也未重新扫描历史原生档案。

新查共享边为 r03_c10与r03_c11、r03_c12与r03_c13、r03_c13与r04_c13、r03_c14与r04_c14、r04_c12与r04_c13、r04_c12与r05_c12、r05_c12与r05_c13。每对各4段，原像素裁片、世界坐标和来源hash见[检查汇总](summary.json)。三个交汇分别位于 r03_c12、r03_c13、r04_c12 的右下角。

r02_c13与r02_c14海水直线材质带，以及r03_c10内部石面直带，仍按[原待修清单](../../root-audit-v01/repair-queue.json)保持未通过。当前局部共享边通过不等同图块内部或整图验收。北侧民居新片由单独的增量记录维护。

[来源核对](source-delta.json)只覆盖冻结截点的当前有效选择；后续新版本需针对变化像素复核。此批零生图、零生产写入、零Git操作。
'''
(O/'review.md').write_text(text,encoding='utf-8')
print('7 new edges / 28 segments / 3 crosspoints reviewed; 15 old edge results reused')
