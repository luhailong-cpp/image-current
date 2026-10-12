"""Record manual original-pixel review; no asset changes."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

out = Path(__file__).resolve().parent
inspection = json.loads((out/'source-inspection.json').read_text(encoding='utf-8'))
sources = {s['id']:s for s in inspection['sources']}

def world(patch_id, box):
    x, y = sources[patch_id]['coordinates']['contextWorldBox'][:2]
    return [x+box[0], y+box[1], x+box[2], y+box[3]]

def evidence(name):
    p=out/name
    with Image.open(p) as im:
        size=list(im.size)
    return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'pixels':size,'resized':False,'blurred':False}

findings=[
 {'id':'UPPER-01','priority':'P2','status':'repair-required','sourceIds':['p12','p13','p22','p23'],
  'title':'p23 左上花叶形成矩形硬断口',
  'description':'四角原生 core 直接拼接时，p23 左上花簇形成矩形块：左侧在 world x=51200 与 p22 绿叶截断，底侧在 world y=21619 从粉花硬切到绿叶。不是正常的枝叶遮挡轮廓。',
  'primarySource':'p23','primaryNativeBox':[115,115,230,230],
  'primaryWorldBox':world('p23',[115,115,230,230]),
  'inspectionNativeBox':[60,130,365,365],
  'inspectionWorldBox':world('p23',[60,130,365,365]),
  'recommendedContextWorldBox':[51020,21370,51400,21730],
  'recommendation':'在上述四图角点用同一花叶结构做局部原生修复，保护红柱和屋瓦；同时处理左侧与底侧的断物体，不能只模糊横线。修复后重新核对两个接缝与四角。',
  'evidence':[evidence('p23-mixed-flower-leaf-100pct.png'),evidence('intersection-r1-c2-100pct.png'),evidence('vertical-p22-p23-join-100pct.png')]},
 {'id':'UPPER-02','priority':'P3','status':'minor-local-softness','sourceIds':['p11','p12'],
  'title':'p12 左上继承花簇局部偏软',
  'description':'小花的花心、花瓣轮廓明显比同一裁片下方大花柔软，但花枝方向连续，没有发现重复、错位或断裂。此项为局部清晰度建议，不认定整张原生图被放大。',
  'primarySource':'p12','primaryNativeBox':[115,115,280,245],
  'primaryWorldBox':world('p12',[115,115,280,245]),
  'inspectionNativeBox':[80,80,360,370],
  'inspectionWorldBox':world('p12',[80,80,360,370]),
  'recommendation':'若继续统一花簇清晰度，只处理这些小花的花心和轮廓，同时保持左邻已有花枝位置。',
  'evidence':[evidence('p12-upper-flower-softness-100pct.png')]}
]
seams=[]
for seam in inspection['seams']:
    pair=seam['sourceIds']
    affected=pair in [['p22','p23'],['p13','p23']]
    seams.append({**seam,'visualStatus':'P2 issue in reviewed crop; see UPPER-01' if affected else 'no obvious geometric discontinuity in original-pixel seam crop',
                  'note':'p13→p23 actual core cut is continuous; UPPER-01 sits 115 pixels below this cut and reaches left corner' if pair==['p13','p23'] else None})
lower=[]
for p in ['p21','p22','p23','p24']:
    box=[115,955,1139,1254]
    lower.append({'upperSource':p,'selectedFile':sources[p]['file'],
                  'nativeInspectionBox':box,'worldInspectionBox':world(p,box),
                  'seamWorldY':22528,
                  'status':'checked against p31; gold ridge and blue tiles continuous' if p=='p21' else 'upper native lower edge inspected only; lower counterpart deliberately outside this task',
                  'objects':{'p21':'gold ridge, blue roof tiles, flowers','p22':'blue tiles, beige wall and red column','p23':'red window frames/lattice, beige wall, dark foliage','p24':'red window frame/lattice, beige wall and right red column'}[p],
                  'followup':None if p=='p21' else 'Read the selected lower source and compare exact 230-pixel overlap and core cut when its producer completes it.',
                  'evidence':evidence(f'{p}-lower-core-and-halo-100pct.png')})
for source in sources.values():
    assert hashlib.sha256(Path(source['file']).read_bytes()).hexdigest()==source['sha256']
report={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),
        'tile':'r06_c13','status':'QA complete with one P2 and one P3',
        'scope':inspection['reviewScope'],'selectedNative':inspection['selectedNative'],
        'sourceInspection':str(out/'source-inspection.json'),
        'method':'assemble.py load_plan and inspect_source; exact integer core crops and pastes; original-pixel visual inspection; no resize, interpolation, enhancement or blur',
        'coordinateConvention':'[x0,y0,x1,y1), exclusive right/bottom; world means art-canvas pixel coordinates only',
        'sourceEvidence':{'selectedCount':9,'dimensions':[1254,1254],'hashesVerified':True,'sourceHashesUnchangedAtEnd':True,'actualModelAndQuality':'kept as recorded; no inference'},
        'counts':{'reviewedSeamPairs':11,'reviewedFourWayIntersections':3,'P1':0,'P2':1,'P3':1},
        'findings':findings,'seams':seams,'lowerEdgeReview':lower,
        'limits':['No p32 or later source read, even if concurrently created.','No external tile seams reviewed in this task.','This does not mark the tile formally accepted.'],
        'writes':{'directory':str(out),'nativeModified':False,'promptsModified':False,'selectionModified':False,'candidateModified':False,'progressModified':False,'imageGenerationCalls':0}}
(out/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out/'visual-review.json'),'P2':1,'P3':1,'sourcesUnchanged':True},ensure_ascii=False))
