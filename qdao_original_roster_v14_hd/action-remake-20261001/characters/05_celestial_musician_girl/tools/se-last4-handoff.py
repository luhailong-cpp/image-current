from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'provenance/ground-contact-20261004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes={
13:'保留13-v4：远LEFT在身下偏前承担负荷，近RIGHT屈膝回收并悬空；两腿由裤腿前后遮挡连续可辨，琴手完整。',
14:'保留14-v7：远LEFT支撑脚向髋下收回，近RIGHT继续屈膝抬起；是第三位置段的第二张独立承重姿态。',
15:'选15-v9：远LEFT从髋后向下伸展，后側靴前掌处于低位支撑、鞋跟抬起；较大的近RIGHT裤腿覆盖前层且靴悬空。拒绝v6的前伸及v7/v8后脚过高。',
16:'选16-v9：远LEFT后側膝踝延伸、前掌低位支撑继续，近RIGHT回到身体中下方待下一帧落地；16→01接图可读腿交换，入脚距离较v7/v8收近。'
}
rows=[]
for frame,version in [(13,4),(14,7),(15,9),(16,9)]:
    file=f'staging/run/SE/ground-{frame:02}-v{version}.png'
    record=file+'.generation.json'
    meta=load(ROOT/record)
    assert sha(ROOT/file)==meta['sha256']
    assert sha(ROOT/meta['source']['file'])==meta['source']['sha256']
    assert meta['transform']['globalScale']==.65
    assert meta['transform']['sourceRoot']==[680,1195]
    assert meta['transform']['targetRoot']==[512,942]
    assert meta['edgeMaxAlpha']==0
    rows.append(dict(action='run',direction='SE',targetFrame=frame,sourceFile=file,sourceGenerationRecord=record,sha256=meta['sha256'],sourceGenerationRecordSha256=sha(ROOT/record),nativeSha256=meta['source']['sha256'],supportLeg='LEFT',positionSegment=3 if frame<15 else 4,pairOrdinal=1 if frame%2 else 2,visualNotes=notes[frame]))
assert len({r['sha256'] for r in rows})==4
selection=OUT/'position-selection-SE-last4.json'
save(selection,rows)
oldplan=OUT/'position-selection-SE-root.json'
review={
'reviewedAt':datetime.now(timezone.utc).isoformat(),
'scope':'SE13–16修图与固定配准后逐图/成对/16→01离线静态检查；SE01–12只读顺序意见。',
'selectionFile':str(selection.relative_to(ROOT)).replace('\\','/'),'selectionSha256':sha(selection),
'rootPlanReadOnlyFile':str(oldplan.relative_to(ROOT)).replace('\\','/'),'rootPlanReadOnlySha256':sha(oldplan),
'status':'offline_static_review_passed','clientValidated':False,
'registration':{'globalScale':.65,'sourceRoot':[680,1195],'targetRoot':[512,942],'perFrameNormalization':False},
'rows':rows,
'pairReview':[
{'frames':[13,14],'judgement':'保留。远LEFT支撑由下方偏前收至髋下；近RIGHT始终悬空；第三位置段两张姿态独立。'},
{'frames':[15,16],'judgement':'通过v9。远LEFT后侧靴从实际膝踝链向下伸展，前掌低位支撑；近RIGHT裤腿位于前层并遮挡远腿，近靴悬空。两脚均沿SE，未见明确外翻或多肢。'},
{'frames':[14,15],'judgement':'从髋下承重进入后侧支撑，远腿退至近腿后方，腿部遮挡变化可解释；无需将整图平移。'},
{'frames':[16,1],'judgement':'近RIGHT自由腿在16向中下方回收，在01成为支撑；远LEFT随后回收。已看固定配准连图，入脚跨度已较v7/v8收近，未见确定需继续扩修项。'}
],
'upperBodyReview':'13/14既有姿态变化保留；15/16保持14的面部、手臂连接及完整琴头/琴身。未见明显比例跳变、错手或肢体增殖。固定1024导出四边alpha0。',
'readOnlySE01to12':{'recommendation':'保持root现有顺序，不交换06/07。','reason':'06→07前掌点有小幅前移，但07脚跟进一步抬起、自由腿更展开；按仅屏幕足点x交换会使踝部受力相位倒退。现有05→08近RIGHT支撑链成立，未发现必须另画槽。','sourceFile':'provenance/ground-contact-20261004/position-selection-SE-root.json'},
'rejectedCandidates':[
{'files':['staging/run/SE/15-v6.native.png','staging/run/SE/16-v6.native.png'],'reason':'远LEFT靴回到屏右前侧，不适合后蹬段。'},
{'files':['staging/run/SE/15-v7.native.png','staging/run/SE/16-v7.native.png','staging/run/SE/15-v8.native.png','staging/run/SE/16-v8.native.png'],'reason':'远LEFT后侧靴过高，像悬空回收；不能签为真实支撑。v7/v8近RIGHT也过于向屏右伸出。'}
],
'evidence':[{'file':f'provenance/ground-contact-20261004/SE-last4-{kind}.jpg','sha256':sha(OUT/f'SE-last4-{kind}.jpg'),'purpose':'等比例固定配准13→14→15→16→01 '+kind} for kind in ['full','feet']],
'remainingRequiredEdits':[],
'limits':'本报告仅为离线源图/固定导出静态审阅；不宣称客户端播放、碰撞、世界位移或真实地面接触系统已验证。final、主selection与manifest未修改。'
}
save(OUT/'SE-position-independent-review.json',review)
print(json.dumps({'selectionFile':str(selection),'selectionSha256':sha(selection),'reviewSha256':sha(OUT/'SE-position-independent-review.json'),'rows':len(rows)},ensure_ascii=False))

