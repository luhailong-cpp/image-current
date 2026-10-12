from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
inp=json.loads((b/'review/nw-review-input-20261004.json').read_text(encoding='utf-8'))
old=json.loads((b/'review-run-NW.json').read_text(encoding='utf-8-sig'))
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frames=[]
for idx,key in enumerate(inp['selected']):
 p=b/'staging'/(key+'.png'); im=Image.open(p);g=p.with_suffix('.png.generation.json')
 rec=json.loads(g.read_text(encoding='utf-8-sig'))
 item={'slot':f'run-NW-{idx+1:02}','file':p.as_posix(),'status':'pending_dynamic_grounding_and_edges','notes':inp['notes'][idx],'sha256':sha(p),'width':im.width,'height':im.height,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema(),'generationRecord':g.relative_to(b).as_posix(),'requestExists':(b/'provenance'/(key+'.request.json')).exists(),'toolReceiptExists':(b/'provenance'/(key+'.tool-result.json')).exists(),'sourceCopyMatchesRecordedSha':sha(p)==rec['sha256']}
 frames.append(item)
 rec['review']={'status':item['status'],'notes':item['notes'],'reviewedAt':now,'formalPassed':False}
 rec['evidence']['toolResultFile']='provenance/'+key+'.tool-result.json'
 dump(g,rec)
rejects=[]
for key,why in inp['rejected'].items():
 p=b/'staging'/(key+'.png');rejects.append({'file':p.as_posix(),'status':'superseded_for_sequence','reason':why,'notes':why})
 g=p.with_suffix('.png.generation.json')
 if g.exists():
  rec=json.loads(g.read_text(encoding='utf-8-sig'));rec['review']={'status':'superseded_for_sequence','notes':why,'reviewedAt':now,'formalPassed':False}
  if (b/'provenance'/(key+'.tool-result.json')).exists():rec['evidence']['toolResultFile']='provenance/'+key+'.tool-result.json'
  dump(g,rec)
audit=[]
for key in inp['newKeys']:
 p=b/'staging'/(key+'.png');g=p.with_suffix('.png.generation.json');im=Image.open(p);rec=json.loads(g.read_text(encoding='utf-8-sig'))
 request=b/'provenance'/(key+'.request.json');receipt=b/'provenance'/(key+'.tool-result.json')
 audit.append({'key':key,'sha256':sha(p),'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema(),'requestExists':request.exists(),'toolReceiptExists':receipt.exists(),'generationRecordExists':g.exists(),'recordShaMatches':rec['sha256']==sha(p),'referenceCount':len(json.loads(request.read_text(encoding='utf-8-sig'))['referenced_image_paths']),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality')})
r09=b.parent/'09_bamboo_archer_girl'
ref={'userAuthority':'用户最新明确认可09竹弓少女当前动作为对了；采用当前runtime同方向实际图作动作参照，旧文档needs_review不撤回该认可。','manifest':{'file':(r09/'manifest.json').as_posix(),'sha256':sha(r09/'manifest.json')},'timing':{'file':(r09/'animation-timing.json').as_posix(),'sha256':sha(r09/'animation-timing.json'),'usage':'仅来源快照；17节奏采用最新用户1200ms/16=75ms，未照搬09旧时长。'},'frames':[{'file':(r09/'runtime/run/NW'/f'{i:02}.png').as_posix(),'sha256':sha(r09/'runtime/run/NW'/f'{i:02}.png')} for i in range(1,17)],'observed':'09同方向能见接触/髋下承重/后伸/收腿回摆及前后遮挡变化；其弓持握约束不直接照搬为17的两臂姿势。对比脚长轴、膝踝和前后承重顺序，不只看脚在画面左右，也不把露鞋底一概称外撇。','styleFile':'D:/work/image/designs/jubaozhai-ui/02-characters.png','identityFile':'D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/17-delivery-preview/revisions/final-20260923/runtime/idle/NW.png'}
issues=inp['issues']
report={'character':b.name,'direction':'NW','reviewedAt':now,'status':'sixteen_candidates_pending_dynamic_grounding_and_edges','counts':{'expectedSlots':16,'availableSlots':16,'missing':0,'passed':0},'availableSlots':list(range(1,17)),'visualPassed':0,'sequencePassed':False,'clientTested':False,'method':'实际原生PNG、1254完整画布同尺度16格与脚部裁剪QA联系表人工复核；只改本角色图片，经image_gen每帧独立返回并原样复制。不按提示词/帧号宣布相位通过，不移动整图贴地。自然头部起伏不是单独失败理由。','timing':{'cycleMs':1200,'frameMs':75,'uniform':True,'authority':'最新用户明确要求','phaseWeightingApplied':False,'clientTested':False},'selectedForSequenceReview':frames,'frames':frames,'reviewed':[{'file':f['file'],'status':f['status'],'notes':f['notes']} for f in frames]+rejects,'supersededAttempts':rejects,'commonIssues':issues,'grounding':{'status':'not_accepted','rootAccepted':False,'supportCandidates':['01','02','03','09','10','11'],'toeOffCandidates':['05','13'],'flightCandidates':['06','14'],'contactRootCoordinates':None,'reason':'尚未建立经整段受力连续验证的根点；未用最低非透明像素或整图升降伪造接地。'},'referenceReview':'review/reference09-NW-20261004.json','qa':['review/reference09-NW-current-full.png','review/reference09-NW-current-legs.png','review/reference09-NW-09-before.png',inp['landingQA']], 'landingCorrectionMeasurement':inp['landingMeasurement'],'previousFourKeyframeSnapshot':old.get('previousFourKeyframeSnapshot',old)}
dump(b/'review-run-NW.json',report)
comparison={'character':b.name,'direction':'NW','reviewedAt':now,'reference':ref,'scope':'N参照小批整改后，用户最新授权扩展NW现有4关键帧及12缺帧。仅写17目录N/NW；未动其他方向及共享预览。','timing':report['timing'],'selectedForSequenceReview':frames,'newNativeCallsThisNwContinuation':len(audit),'newFramesAudit':audit,'formalPassed':0,'sequencePassed':False,'clientTested':False,'remainingIssues':issues,'rejectedOrSuperseded':rejects,'cleanup':'当前仍在制作、尚未确认导出成品，来源/比较候选暂保留；终稿确认后的素材清理按AGENTS执行。','limitations':'本次只完成16候选与逐帧人工审查，不能宣称手脚/接地已全部修好；未运行主预览构建或全角色inventory。'}
dump(b/'review/reference09-NW-20261004.json',comparison)
assert len(set(f['sha256'] for f in frames))==16
assert all(f['width']==1254 and f['height']==1254 and f['mode']=='RGBA' and f['requestExists'] and f['toolReceiptExists'] and f['sourceCopyMatchesRecordedSha'] for f in frames)
assert len(audit)==len(inp['newKeys']) and all(x['requestExists'] and x['toolReceiptExists'] and x['generationRecordExists'] and x['recordShaMatches'] and x['referenceCount']>=3 for x in audit)
print(json.dumps({'selected':len(frames),'uniquePngHashes':len(set(f['sha256'] for f in frames)),'newCalls':len(audit),'missing':0,'formalPassed':0,'selection':[Path(x['file']).name for x in frames]},ensure_ascii=False))

