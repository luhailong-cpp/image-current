from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,ast,copy
from PIL import Image
R=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
now=datetime.now(timezone.utc).isoformat();p=R/'generation/W/11-v2.png';im=Image.open(p);a=im.getchannel('A');bb=list(a.point(lambda v:255 if v>8 else 0).getbbox())
seqp=R/'review/run-W-sequence-input.json';seq=json.loads(seqp.read_text(encoding='utf8'));before=copy.deepcopy(seq);f=next(x for x in seq['frames'] if x['slot']==11);assert f['source'].endswith('/11-v1.png')
issues=['11-v2已局部恢复莲灯体量，握点和双脚承重姿态保持；灯细节仍有AI差异。','右侧头发靠近边缘；头向左漂；这些原有问题本次未改。']
phase='远右身体下方全掌支撑，近左膝向前通过，灯回髋侧；11-v2局部恢复灯体量'
review=dict(schemaVersion=1,reviewedAt=now,status='selected_wip_pending_full_cycle_review',visualAccepted=False,sourceSha256=sha(p),selectedSlot=11,observedPhase=phase,issues=issues,imageViewed=True,nearFarArms='near anatomical LEFT flask, far anatomical RIGHT lantern; target grip and shoulders retained',shoeAxis='WEST toe axes and support pose retained; no full-cycle acceptance',nativeCanvas=list(im.size),alphaGt8Bounds=bb,nativeRoot=[610,1179],rootStatus='provisional diagnostic only; no sprite transformation',actualModel=None,actualQuality=None,durationMs=75,operation='one local AI lantern-body redraw; no programmatic PNG transform',manualComparison={'method':'full native image visual comparison; approximate manual landmarks, uncertainty10–15px','lampBowlWidthPx':{'11-v1':195,'11-v2':250,'10-v2':240,'12-v1':240},'gripXY':[640,665],'rightSupportShoeBottomY':{'11-v1':1191,'11-v2':1192},'result':'body/feet/nearLeftFlask preserved; lantern restored close to neighbors, slightly larger by manual estimate'},dynamicAccepted=False,clientTested=False)
write(p.with_suffix('.review.json'),review);gp=Path(str(p)+'.generation.json');g=json.loads(gp.read_text(encoding='utf8'));g.update(status='selected_wip_pending_full_cycle_review',reviewFile='generation/W/11-v2.review.json',action='run',direction='W',frame=11);write(gp,g)
f.update(source=str(p).replace('\\','/'),sourceSha256=sha(p),observedPhase=phase,issues=issues,durationMs=75,alphaGt8Bounds=bb,diagnosticLowestShoeY=bb[3]-1,diagnosticFloorClearance=1179-(bb[3]-1))
seq['issues']=[x.replace('04→05 and11→12 arm travel jumps; lamp shrinks in11.','04→05 and11→12 arm travel jumps;11-v2 restores lamp dimensions while keeping original grip and feet.') for x in seq.get('issues',[])]
assert all(old==new for old,new in zip(before['frames'],seq['frames']) if old['slot']!=11)
assert all(x['durationMs']==75 for x in seq['frames']) and len({x['sourceSha256'] for x in seq['frames']})==16
write(seqp,seq)
scriptp=R/'tools/review_w_sequence.py';script=scriptp.read_text(encoding='utf8');oldsha=sha(scriptp)
assert "'10-v2','11-v1','12-v1'" in script
script=script.replace("'10-v2','11-v1','12-v1'","'10-v2','11-v2','12-v1'")
script=script.replace('远右身体下方全掌支撑，近左膝向前通过，灯回髋侧',phase)
script=script.replace("['莲灯直径相对邻帧缩小；右侧头发靠近边缘；头向左漂']","['11-v2局部恢复灯体量，持手与双脚保持；右侧头发靠近边缘；头向左漂']")
script=script.replace('04→05 and11→12 arm travel jumps; lamp shrinks in11.','04→05 and11→12 arm travel jumps;11-v2 restores lamp dimensions while keeping original grip and feet.')
script=script.replace('11灯缩小','11-v2灯体量已局部恢复')
script=script.replace('duration=[45]*16','duration=[75]*16')
tree=ast.parse(script);choices=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='choices' for t in n.targets));assert ast.literal_eval(choices)[10]=='11-v2'
scriptp.write_text(script,encoding='utf8')
verification=dict(checkedAtUtc=now,source=str(p),sourceSha256=sha(p),selectionSha256=sha(seqp),selectedSlot=11,other15SlotsUnchanged=True,all16SourcesUnique=True,frameMs=75,totalMs=1200,scriptSyntax='ast.parse passed',scriptSelection11='11-v2',scriptShaBefore=oldsha,scriptShaAfter=sha(scriptp),apngDurationCorrectedFrom45To75=True,scriptExecuted=False,reasonNotExecuted='root will rebuild; avoided rewriting unrelated reviews/contact and shared preview',previewFilesModified=False,sourcePNGModified=False,visualAccepted=False,review=review)
write(R/'review/run-W11-lamp-repair-verification.json',verification)
print(json.dumps({k:verification[k] for k in ['sourceSha256','selectionSha256','selectedSlot','other15SlotsUnchanged','all16SourcesUnique','totalMs','scriptSyntax','scriptSelection11','previewFilesModified']}))

