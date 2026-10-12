from pathlib import Path
from PIL import Image
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parent;T=D.parents[1];NAME='r04_c04-pipeline-minimum-error-fbb8f7edb616-fe50f8';M=T/'candidate'/(NAME+'.assembly.json');A=json.loads(M.read_text(encoding='utf-8'));inputs=json.loads((D/'review-inputs.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def intersects(a,b):return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
issues=[
 {'id':'F1','severity':'minor','object':'门板竖槽','tileBoxApprox':[2492,1038,2503,1061],'finding':'同一竖槽的暗边与高光一起横跳约3–4px；属几何接缝。','evidence':str(D/'detail-y1024-col3-wood-native.png'),'evidenceSourceTileBox':[2398,864,2598,1184],'evidenceIssueLocalBoxApprox':[94,174,105,197]},
 {'id':'F2','severity':'moderate','object':'左侧浅石栏杆灰色斜面','tileBoxApprox':[603,3157,644,3187],'finding':'同一连续灰面出现无结构依据的斜切明暗边；几何轮廓大致连续，但色面拼接明显。','evidence':str(D/'detail-y3072-col1-gray-native.png'),'evidenceSourceTileBox':[500,2800,800,3410],'evidenceIssueLocalBoxApprox':[103,357,144,387]},
 {'id':'F3','severity':'moderate','object':'底排阶梯立面，x2048/y3072交点附近','tileBoxApprox':[2102,2987,2151,3090],'finding':'同一灰色阶梯立面内出现较大的深浅硬色块界，斜折边触及下方暗缝；不像正常石块分缝。','evidence':str(T/'qa'/NAME/'junction-x2048-y3072.png'),'evidenceSourceTileBox':[1888,2912,2208,3232],'evidenceIssueLocalBoxApprox':[214,75,263,178]},
 {'id':'F4','severity':'minor','object':'底排阶梯立面，x3072/y3072交点附近','tileBoxApprox':[3060,2990,3093,3091],'finding':'阶梯灰色立面有较弱块状色面接界，底部暗边也见轻微接点；没有明显结构断裂。','evidence':str(T/'qa'/NAME/'junction-x3072-y3072.png'),'evidenceSourceTileBox':[2912,2912,3232,3232],'evidenceIssueLocalBoxApprox':[148,78,181,179]}
]
for i in issues:i['worldBoxApprox']=[v+12288 for v in i['tileBoxApprox']];i['evidenceSha256']=sha(i['evidence']);i['verifiedByIndependentVisualReviewer']=True
deferred={
'internal-x1024-segment01':'条内木框存在矩形色面跳变，位于已交给upper_left处理的col2相接范围。',
'internal-x1024-segment02':'条右端附近有矩形木框/金边色面跳变，随col2返修检查。',
'internal-x2048-segment02':'后段灰石面及木框存在块状色阶，位于col2/col3交界；随col2返修检查。',
'internal-y1024-segment02':'朱红柱及邻接木框存在明显截面/矩形边界跳变，属于已知col2返修。',
'internal-y2048-segment02':'朱红柱脚及左侧木框存在已知拼接不连续，属于col2返修。',
'junction-x1024-y1024':'木框矩形色差与col2上部返修相接。',
'junction-x2048-y1024':'金色竖框有硬色阶，位于col2返修相接域。',
'junction-x1024-y2048':'红棕木框矩形色阶与col2柱脚返修域相接。',
'junction-x2048-y2048':'交点上部灰石面有色块边，属于col2返修相接范围，待新稿复核。'
}
pass_notes={
'internal-x1024-segment03':'石框、门槛、浅石栏杆与台阶轮廓在所见条内连续。',
'internal-x1024-segment04':'底排台阶及纵向栏杆相接连续，未见结构断缝。',
'internal-x2048-segment01':'红棕木面与金色窄框在所见条内连续。',
'internal-x3072-segment01':'门贴金边、红金纹面及木板接合连续。',
'internal-x3072-segment02':'门贴下缘、木板、红棕门槛至灰石面连续。',
'internal-y1024-segment01':'左侧木板和灯笼悬件在此横向边界连续。',
'internal-y1024-segment04':'红金门贴与木板主轮廓连续；金边有一处很轻微可疑边缘，单列watch，未据此判明确失败。',
'internal-y2048-segment01':'石墙、台阶与红色流苏轮廓连续。',
'internal-y2048-segment03':'浅色石板横缝、树影和红纸碎片连续。',
'internal-y2048-segment04':'石板横缝与光影连续。',
'internal-y3072-segment02':'台阶明暗带及石块分缝连续。',
'junction-x3072-y1024':'门贴斜金边、红金图案与木板接合连续。',
'junction-x3072-y2048':'地砖横缝、光影连续。',
'junction-x1024-y3072':'栏杆与台阶在交点所见区域连续。'
}
rows=[]
for q in A['qaFiles']:
 p=Path(q['file']);label=p.stem;found=[i['id'] for i in issues if intersects(q['cropLTRB'],i['tileBoxApprox'])]
 if label in deferred:verdict='DEFERRED_COL2_REPAIR';note=deferred[label]
 elif found:verdict='FAIL';note='包含已逐图确认的缺陷 '+', '.join(found)+'；同一缺陷可能横跨多个QA窗口。'
 else:verdict='PASS';note=pass_notes[label]
 rows.append({'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size),'cropLTRB':q['cropLTRB'],'rotationCCW90':q['rotationCCW90'],'actuallyViewed':True,'viewMethod':'Original-resolution 1:1 paste into labeled native batch; selected details also viewed individually','verdict':verdict,'issueIds':found,'note':note,'numericMetricsUsedToPass':False})
watch={'id':'W1','evidence':str(D/'detail-y1024-col4-gold-native.png'),'sourceTileBox':[3432,964,3732,1184],'localBoxApprox':[145,149,159,163],'tileBoxApprox':[3577,1113,3591,1127],'note':'金边下侧斜轮廓有很轻微小台阶，主斜向、厚度与色面连续；独立复核认为不能仅凭此图确定拼接成因，不单列为明确FAIL。'}
south=[]
checks={1:('FAIL','灰栏左外沿QA x568..580向右跳约11px，内槽x647..655向左跳约5px；右侧槽线x800..855及外缘x885..950明显不匹配。'),2:('PASS','全宽台阶暗边与踏面连续；QA x724..734附近竖缝在边界连续。'),3:('PASS','全宽阶梯横向暗边及踏面连续；x475附近竖缝从QA y419起始，是下一阶正常石缝。'),4:('PASS','全宽阶梯边界连续；x531附近上阶竖缝在y310自然终止于阶边，没有y320错接。')}
for j,item in enumerate(inputs['southBoundary'],1):
 r=dict(item);r.update({'actuallyViewed':True,'viewedBy':'boundary_audit and independent seam_diagnosis','verdict':checks[j][0],'note':checks[j][1],'numericMetricsUsedToPass':False});south.append(r)
report={'candidate':inputs['candidate'],'candidateSha256':inputs['candidateSha256'],'candidateUnchangedAtReviewEnd':sha(inputs['candidate'])==inputs['candidateSha256'],'manifest':str(M),
 'scope':'24 internal seam strips, 9 intersections, and 4 true south-neighbor boundaries for this exact candidate snapshot','nativePixelScale':1,'resampledByThisReview':False,'formalAccepted':False,
 'acceptanceMeaning':'PASS only means no evident discontinuity in the actual viewed crop. It is not whole-tile acceptance, and repaired candidates must be reviewed again. DEFERRED_COL2_REPAIR is the already assigned red-column repair area, not a pass.',
 'internalSummary':dict(Counter(r['verdict'] for r in rows)),'distinctNonCol2Failures':len(issues),'internalQA':rows,'issues':issues,'watchOnly':[watch],
 'southSummary':dict(Counter(r['verdict'] for r in south)),'southQA':south,'sharedSelectionOrProgressModified':False,'sourcesModified':False,'generatedImages':False,
 'reviewNote':'Actual visual judgments, independently cross-checked for all four non-col2 defects and four outer south strips. Source-selection paths or numerical pixel differences were not used to grant PASS.'}
(D/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'internal':report['internalSummary'],'distinctNonCol2Failures':4,'south':report['southSummary'],'file':str(D/'visual-review.json'),'candidateHashStable':report['candidateUnchangedAtReviewEnd']},ensure_ascii=False,indent=2))
