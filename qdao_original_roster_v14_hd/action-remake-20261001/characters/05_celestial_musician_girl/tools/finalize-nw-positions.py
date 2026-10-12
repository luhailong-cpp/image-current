from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;D=R/'provenance/ground-contact-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=read(D/'NW-reviewed-map.json')
for row in rows:
 p=R/row['sourceFile']; meta=read(R/row['sourceGenerationRecord']);assert sha(p)==meta['sha256']
 row.update(sha256=sha(p),nativeSha256=meta['source']['sha256'])
 if row['sourceFile'].startswith('staging/'):
  gr=R/meta['source']['generationRecord'];g=read(gr);assert sha(R/g['file'])==g['sha256']
  prompt=gr.with_suffix('.prompt.txt');prompt.write_text(g['submittedParameters']['prompt'],encoding='utf-8')
  g['promptFile']=prompt.relative_to(R).as_posix()
  for i,x in enumerate(g['references']):x['role']='edit_target' if i==0 else ('approved_style_reference' if i==len(g['references'])-1 else 'phase_anatomy_reference')
  g['editTarget']=g['references'][0]
  g['visualReview']={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'agent_reviewed_parent_pending','notes':row['visualNotes'],'nativeActuallyViewed':True,'registeredExportActuallyViewed':True,'upperBodyScaleAndQinPreserved':True,'shoeDirection':'NW aligned; no required outward-yaw repair'}
  g['status']='agent_visual_reviewed_parent_pending';save(gr,g)
  meta['sourceGeneration']=g;meta['agentVisualReview']=g['visualReview'];save(R/row['sourceGenerationRecord'],meta)
 row['agentReviewedAt']=datetime.now(timezone.utc).isoformat()
assert len(rows)==16 and len({x['sourceFile'] for x in rows})==16
save(D/'position-selection-NW-ready.json',rows)
save(D/'NW-position-review.json',{'status':'agent_offline_review_complete_parent_pending','timing':{'frameMs':75,'cycleMs':1200},'selection':'position-selection-NW-ready.json','fullAndFeetActuallyViewed':True,'legOrder':'RIGHT01-08,LEFT09-16; old halves swapped as actual anatomical support identities differ','pairReview':['01/02前侧接触到膝踝接受负荷','03/04同一远RIGHT早承重和对腿前摆','05/06髋下收平到略后提跟','07/08同一远RIGHT早蹬到晚蹬，前掌持续接地','09/10近LEFT前侧接触到压缩','11/12近LEFT承重与对腿经过','13/14近LEFT髋下收平到略后提跟','15/16近LEFT后掌抬起而趾掌持续接地'], 'loopReview':'08→09由远RIGHT后蹬转近LEFT接触；16→01由近LEFT后蹬转远RIGHT接触；两条腿不按屏幕横坐标换身份。上身/琴/头冠尺度没有明显突跳。','mandatoryRemainingEdits':[],'frames':rows})
print(json.dumps({'direction':'NW','rows':16,'unique':16,'path':'provenance/ground-contact-20261004/position-selection-NW-ready.json'}))

