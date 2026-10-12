from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
from collections import Counter
import json, hashlib

OUT=Path(__file__).resolve().parent
TILE=OUT.parent
STEM='r03_c05-pipeline-minimum-error-ece82fe09771-fbbe92'
candidate=TILE/'candidate'/f'{STEM}.png'
assembly=TILE/'candidate'/f'{STEM}.assembly.json'
qa=TILE/'qa'/STEM
data=json.loads(assembly.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert Image.open(candidate).size==(4096,4096)
assert sha(candidate)=='60ecd41051d16e950bd301453236cec3cd0227945ac8d034b9e379e6fce89760'
native=[]
for s in data['nativeSources']:
 p=Path(s['file']); assert sha(p)==s['sha256']; assert Image.open(p).size==(1254,1254)
 native.append({'patch':s['patch'],'file':str(p),'sha256':s['sha256'],'pixels':[1254,1254],'generationRecord':s['generationRecord']})
assert len(native)==16

# Verdicts refer to the complete 320-pixel seam-centered inspection window.
# Some failed geometry is 115 pixels from the formal core boundary, inside the window.
rows=[
('x',1024,1,'FAIL',['D1'],'窗口右端出现上排光滑大瓦与下排小瓦的平直截断，约 tile y=909。'),
('x',1024,2,'PASS',[],'斜瓦沟与高光跨缝延续；局部窄瓦片形状已单独放大核看，未确认切断。'),
('x',1024,3,'FAIL',['D2'],'窗口起点邻近 y=2048 的木底/青瓦交界有尖角碎片和不自然裁口。'),
('x',1024,4,'FAIL',['D3'],'青色圆瓦当花心双重化，中心与花瓣在拼接后重复。'),
('x',2048,1,'FAIL',['D1'],'窗口右端约 y=909 存在瓦面相位/画法突变；金色卷饰主体连续。'),
('x',2048,2,'FAIL',['D2'],'窗口尾端出现青瓦矩形碎片压到木底上，边缘直切。'),
('x',2048,3,'FAIL',['D2','D4'],'起点青瓦/木底裁口，尾端约 y=2960 的斜瓦与横瓦错接。'),
('x',2048,4,'PASS',[],'金色卷边、青瓦圆当及木面延续，未见明确切口。'),
('x',3072,1,'PASS',[],'斜瓦行列和高光跨缝延续。'),
('x',3072,2,'PASS',[],'斜金脊、瓦面和木构的跨缝轮廓延续。'),
('x',3072,3,'FAIL',['D4'],'窗口尾端约 y=2960 出现横向窄重复瓦行，行距突然压缩。'),
('x',3072,4,'PASS',[],'瓦沟、圆瓦当和木板跨缝未见明确错位。'),
('y',1024,1,'FAIL',['D1'],'窗口上部 y≈909 为明显水平截断，上方长大亮瓦和下方较小纹理瓦相位冲突。'),
('y',1024,2,'FAIL',['D1'],'同一水平截断延续到第二列；不是仅颜色差。'),
('y',1024,3,'PASS',[],'斜金脊和两侧青瓦延续，未见明确断点。'),
('y',1024,4,'PASS',[],'金色卷饰及其周围瓦沟延续。'),
('y',2048,1,'FAIL',['D2'],'青瓦顶端伸入木底，边缘为突出的三角形/裁切轮廓。'),
('y',2048,2,'FAIL',['D2'],'木底与青瓦交界有明显锯齿切缝、悬空碎片。'),
('y',2048,3,'FAIL',['D2'],'段首 x≈2048..2200 有矩形青瓦片与木底硬接；段内其余木梁较连续。'),
('y',2048,4,'PASS',[],'金色瓦当脊与蓝瓦面的跨缝轮廓连续。'),
('y',3072,1,'PASS',[],'水平金梁及下方横瓦延续，未见明确切口。'),
('y',3072,2,'FAIL',['D4','D5'],'金色弧梁起点有直立切边/角形色块，右上瓦面存在行距与方向突变。'),
('y',3072,3,'FAIL',['D4'],'左端斜瓦截接横瓦，且窗口上部有细窄重复瓦缝横带。'),
('y',3072,4,'FAIL',['D4'],'上部瓦行被压成细窄横带，与下方行距不一致。'),
]
items=[]
for axis,coord,segment,verdict,defects,note in rows:
 q=(segment-1)*1024
 box=[coord-160,q,coord+160,q+1024] if axis=='x' else [q,coord-160,q+1024,coord+160]
 name=f'internal-{axis}{coord}-segment{segment:02d}'
 p=qa/(name+'.png'); assert p.is_file()
 items.append({'id':name,'verdict':verdict,'scope':'complete 320-pixel seam-centered review window','defectIds':defects,'finding':note,'tileCropBox':box,'worldCropBox':[box[0]+16384,box[1]+8192,box[2]+16384,box[3]+8192],'evidence':str(p),'actuallyViewed':True,'sourceScale':1})
jrows=[
(1024,1024,'FAIL',['D1'],'窗口上沿光滑瓦与纹理瓦的硬截断。'),
(1024,2048,'FAIL',['D2'],'木底/青瓦尖角和裁口。'),
(1024,3072,'FAIL',['D5'],'右上金梁由水平变弧形处保留垂直直切边。'),
(2048,1024,'FAIL',['D1'],'上沿左侧仍接触同一瓦面相位变化带。'),
(2048,2048,'FAIL',['D2'],'木底上留有矩形/三角青瓦碎片。'),
(2048,3072,'FAIL',['D4'],'斜瓦与横瓦之间有直边，薄横瓦缝异常。'),
(3072,1024,'PASS',[],'斜瓦及局部金脊延续。'),
(3072,2048,'PASS',[],'金色垂饰、红木梁和瓦面在交点连续。'),
(3072,3072,'FAIL',['D4'],'交点上部窄重复横瓦行延续。'),
]
junctions=[]
for x,y,v,ds,note in jrows:
 name=f'junction-x{x}-y{y}'; p=qa/(name+'.png'); assert p.is_file()
 box=[x-160,y-160,x+160,y+160]
 junctions.append({'id':name,'verdict':v,'scope':'complete 320x320 inspection window','defectIds':ds,'finding':note,'tileCropBox':box,'worldCropBox':[box[0]+16384,box[1]+8192,box[2]+16384,box[3]+8192],'evidence':str(p),'actuallyViewed':True,'sourceScale':1})

external=json.loads((OUT/'external-candidate/manifest.json').read_text(encoding='utf-8'))
efindings={
'west-segment01':('PASS','正式西界的瓦沟和高光延续；窗口 y≈909 的既有水平瓦面变化另记 D1，不能据此称整窗无瑕疵。',[]),
'west-segment02':('PASS','正式边界的斜金脊和斜瓦沟延续；无明确断口。',[]),
'west-segment03':('FAIL','正式边界存在直线色阶跳变，在木面及末端金色竖边最明显；几何大体对齐。',['E1']),
'west-segment04':('FAIL','正式边界将青色圆瓦当截成错位的两段；周围瓦沟/木面也有切线。',['E2']),
'south-segment01':('FAIL','北侧大面积木门板与南侧金边、红墙、柱框不匹配；竖框位置错开。',['E3']),
'south-segment02':('FAIL','北侧木门板直接接到南侧红色大灯笼，实体结构不连续。',['E4']),
'south-segment03':('FAIL','北侧木门板直接接到南侧灯笼右缘、墙/柱/格栅窗；结构不连续。',['E5']),
'south-segment04':('FAIL','北侧木门板/柱直接接到南侧浅色格栅窗；框线和材质整体冲突。',['E6']),
}
for e in external['items']:
 v,n,ds=efindings[e['id']]; e.update(verdict=v,finding=n,defectIds=ds,actuallyViewed=True,scope='formal candidate-to-candidate boundary')

defects=[
('D1',[0,895,2160,940],'上排/第二排之间的瓦型、材质和行相位发生平直切换，主可见线约 tile y=909。'),
('D2',[500,1930,2210,2160],'木底与青瓦的最小误差路径留下锯齿、三角/矩形残片。'),
('D3',[980,3440,1080,3590],'x=1024 附近圆瓦当花心重复；不是单纯颜色差。'),
('D4',[1900,2945,4096,3020],'斜/横瓦转换有断点，横瓦顶部出现压缩的重复窄瓦行。'),
('D5',[1135,2912,1290,3090],'金弧梁起点保留直边，亮暗面的角形块突变。'),
('E1',[0,2048,160,3072],'西界第三段沿正式界线的木面/金边色阶跳变。'),
('E2',[0,3420,160,3660],'西界第四段圆瓦当与瓦沟错位。'),
('E3',[0,3936,1024,4096],'南界第一段门板对金边、红墙、柱框结构冲突。'),
('E4',[1024,3936,2048,4096],'南界第二段门板对灯笼结构冲突。'),
('E5',[2048,3936,3072,4096],'南界第三段门板对灯笼/墙柱/窗结构冲突。'),
('E6',[3072,3936,4096,4096],'南界第四段门板对格栅窗结构冲突。'),
]
defect_records=[]
for id,b,n in defects:
 defect_records.append({'id':id,'approximateTileROI':b,'approximateWorldROI':[b[0]+16384,b[1]+8192,b[2]+16384,b[3]+8192],'finding':n,'roiIsApproximate':True})
report={
'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r03_c05','candidate':{'file':str(candidate),'sha256':sha(candidate),'pixels':[4096,4096],'assemblyManifest':str(assembly)},
'formalAccepted':False,'completionState':'16 source cores generated and assembled; candidate does not pass visual continuity QA',
'nativeSourceCount':16,'nativeGeneratedFilesRetained':18,'nativeSourcePixels':[1254,1254],'corePixels':1024,'haloPixelsPerSide':115,'overlapPixels':230,'actualModel':None,'actualQuality':None,
'nativeSources':native,'counts':{'internalSegments':dict(Counter(i['verdict'] for i in items)),'junctions':dict(Counter(i['verdict'] for i in junctions)),'externalSegments':dict(Counter(i['verdict'] for i in external['items']))},
'reviewMethod':'All 24 seam windows and 9 junctions actually viewed at original pixel scale, as six unscaled strip batches and one unscaled junction grid. All 8 candidate-to-candidate external strips actually viewed as two unscaled batches. Border labels added outside source images. No automatic visual pass derived from metrics.',
'verdictInterpretation':'Internal verdicts cover the entire 320-pixel-wide seam-centered crop, including artifacts up to 160 pixels from formal core boundaries. Repeated FAIL windows can refer to one shared defect, and are not counts of independent defects. External verdicts assess the formal tile boundary; known nearby internal defects are separately identified.',
'internalSegments':items,'junctions':junctions,'external':external,'uniqueDefects':defect_records,
'southRepair':{'attempted':False,'merged':False,'note':'真正以南界为中心的修复仅规划，未制作/生成/合入。四段实际结构冲突全部保留并明确未通过。没有未落盘的成功生成结果。'},
'notAssessed':['north external boundary: no corresponding final neighbor candidate reviewed','east external boundary: no corresponding final neighbor candidate reviewed'],
'evidenceBatches':[str(OUT/f'internal-batch-{i}.png') for i in range(1,7)]+[str(OUT/'junction-grid.png'),str(OUT/'external-candidate/west-batch-native.png'),str(OUT/'external-candidate/south-batch-native.png')],
'noResize':True,'noFurtherGenerationAtWrapUp':True,'sharedRootProgressModified':False,
}
report_path=OUT/'final-visual-review.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['r03_c05 最终稳定候选 / 尚未正式验收',str(candidate),'SHA256: '+sha(candidate),'','16/16 原生来源已生成并选择；18 张原始生成文件及回执保留。实际模型和 quality 未知。','4096×4096 候选用无缩放最小误差源像素选择拼接；1254 原生 / 1024 core / 每侧115 halo。','内部 24 窗口：9 PASS / 15 FAIL；9 交点：2 PASS / 7 FAIL。','西界：前两段 PASS，第三段色阶 FAIL，第四段瓦当错位 FAIL。','南界：4/4 结构冲突 FAIL；南界修复未尝试、未合入，无待保存的生成结果。','内部 FAIL 以整个320像素检查窗口判定；同一缺陷可出现在多个窗口，不能将22个失败窗口说成22个独立缺陷。','北、东外缘未验收。','']
for group,rr in [('24 内缝',items),('9 交点',junctions),('8 实际候选外界',external['items'])]:
 lines.append(group)
 for i in rr: lines.append(f"{i['id']} | {i['verdict']} | {i['finding']}")
 lines.append('')
lines.append('独立缺陷位置（tile ROI 为近似定位，精确裁图框与 world 坐标见 JSON）')
for d in defect_records: lines.append(f"{d['id']} | tile {d['approximateTileROI']} | world {d['approximateWorldROI']} | {d['finding']}")
lines += ['','JSON报告: '+str(report_path),'来源回执与原图: '+str(TILE/'native'),'接缝路径/选择来源完整证据: '+str(assembly),'外界真实候选哈希和无缩放裁图来源: '+str(OUT/'external-candidate/manifest.json')]
(OUT/'final-visual-review.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(TILE/'final-handoff.json').write_text(json.dumps({'tile':'r03_c05','candidate':report['candidate'],'formalAccepted':False,'sourceCoresComplete':16,'visualCounts':report['counts'],'visualReport':str(report_path),'readableReport':str(OUT/'final-visual-review.txt'),'southernRepairAttempted':False,'southernRepairMerged':False,'outstandingGeneratedResults':0,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(report_path),'counts':report['counts'],'candidateSha256':sha(candidate),'validatedNativeSources':len(native)},ensure_ascii=False,indent=2))
