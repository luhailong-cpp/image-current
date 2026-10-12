from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/05_celestial_musician_girl');D=R/'provenance/ground-contact-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
notes=read(D/'SW-final-visual-notes.json')
rows=[x for x in read(D/'SWNW-candidate-map.json') if x['direction']=='SW']
versions={5:5,6:6,7:7,8:5}
for row in rows:
 n=row['targetFrame']
 if n in versions:
  row['sourceFile']=f'staging/run/SW/ground-{n:02}-v{versions[n]}.png';row['sourceGenerationRecord']=row['sourceFile']+'.generation.json'
 p=R/row['sourceFile'];m=read(R/row['sourceGenerationRecord']);assert sha(p)==m['sha256']
 im=Image.open(p);assert im.size==(1024,1024) and im.mode=='RGBA'
 row.update(sha256=sha(p),nativeSha256=m['source']['sha256'],visualNotes=notes[n-1],visualStatus='agent_offline_reviewed_parent_final_merge_pending',agentReviewedAt=datetime.now(timezone.utc).isoformat(),shoeDirectionReview='SW轴与膝踝一致；游离前摆脚露底不当作外撇')
 if row['sourceFile'].startswith('staging/'):
  gr=R/m['source']['generationRecord'];g=read(gr);assert sha(R/g['file'])==g['sha256']
  prompt=gr.with_suffix('.prompt.txt');prompt.write_text(g['submittedParameters']['prompt'],encoding='utf-8')
  g['promptFile']=prompt.relative_to(R).as_posix()
  for i,x in enumerate(g['references']):x['role']='edit_target' if i==0 else ('approved_style_reference' if i==len(g['references'])-1 else 'phase_anatomy_reference')
  g['editTarget']=g['references'][0]
  g['visualReview']={'reviewedAt':row['agentReviewedAt'],'status':'agent_offline_reviewed_parent_final_merge_pending','notes':row['visualNotes'],'nativeActuallyViewed':True,'registeredExportActuallyViewed':True,'upperBodyScaleAndQinPreserved':True,'shoeDirection':row['shoeDirectionReview']}
  g['status']='agent_offline_reviewed_parent_final_merge_pending';save(gr,g)
  m['sourceGeneration']=g;m['agentVisualReview']=g['visualReview'];save(R/row['sourceGenerationRecord'],m)
nw=read(D/'position-selection-NW-ready.json')
allrows=rows+nw
assert len(allrows)==32 and len({x['sourceFile'] for x in allrows})==32 and len({x['sha256'] for x in allrows})==32
for x in allrows:assert sha(R/x['sourceFile'])==x['sha256']
save(D/'position-selection-SWNW.json',allrows)
save(D/'SWNW-candidate-map.json',allrows)
save(D/'SW-position-review.json',{'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'agent_offline_review_complete_parent_final_merge_pending','selection':'position-selection-SWNW.json','timing':{'frames':16,'frameMs':75,'cycleMs':1200},'registration':{'scale':0.65,'sourceRoot':[615,1205],'targetRoot':[512,942],'perFrameAlignment':False},'fullAndFeetActuallyViewed':True,'perPairReview':['01/02同RIGHT前位初触与承接，两张不同姿态','03/04同RIGHT压缩与身体经过，原02/03复用','05/06同RIGHT髋下到稍后承重，LEFT折膝经过','07/08同RIGHT后位前掌蹬地，LEFT前摆，腿身份依裤腿遮挡连续追踪','09/10LEFT前位接触与接受负荷','11/12LEFT早承重压缩与上升','13/14LEFT髋下至稍后，RIGHT前摆','15/16LEFT后侧前掌持续负重，RIGHT准备01落地'],'loopReview':'08→09由RIGHT后蹬转LEFT落地；16→01由LEFT后蹬转RIGHT初触。鞋轴沿SW，无额外横向外撇。头冠/上身/琴手和角色尺度未见明显突跳。','independentReviewResolution':{'reviewers':['root','finish_ew'],'selected':'07-v7 + 08-v5 + original08 as new09','reason':'按LEFT前屈膝裤腿覆盖RIGHT后裤腿根部追踪，08v5后侧RIGHT低右靴仍承重；不能仅以屏幕横坐标或靴大小判定换脚。08v6保留为未选候选。08v7仅提示草案未调用。'},'mandatoryRemainingEdits':[],'clientValidated':False,'frames':rows})
out=Image.new('RGB',(2000,390),(211,218,221))
for i,n in enumerate([5,6,7,8,9]):
 row=next(x for x in rows if x['targetFrame']==n);im=Image.open(R/row['sourceFile']).convert('RGBA');bg=Image.new('RGBA',im.size,(211,218,221,255));bg.alpha_composite(im)
 out.paste(bg.convert('RGB').crop((325,635,725,1000)),(400*i,25));ImageDraw.Draw(out).text((400*i+5,5),f'SW{n:02} '+row['sourceFile'].split('/')[-1],fill='black')
out.save(D/'SW05-09-final-contact.jpg',quality=96)
print(json.dumps({'rows':32,'uniqueFiles':32,'uniqueHashes':32,'selectionSha256':sha(D/'position-selection-SWNW.json'),'selection':'provenance/ground-contact-20261004/position-selection-SWNW.json'}))

