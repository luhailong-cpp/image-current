from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest');T=B/'r13_c05';P=T/'pipeline';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,o):p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();lane=B/'r12_c05/repairs-resume-20261012/lane-state.json';l=json.loads(lane.read_text());l.update({'status':'checkpointed_pending_parent_independent_review','largeBlueNotchSameClassRetriesStopped':True,'largeBlueNotchOpenReason':'Eight builtin geometry/control variants did not preserve the exact fixed native anchor line; all failed variants retained and explicitly rejected. Parent instructed stop repeating this class. No tolerance widened.','handoffTo':'r13_c05','handoffAtUtc':now,'currentCandidateAssembly':str(B/'r12_c05/repairs-resume-20261012/integrated-local-v14/assembly.json')});write(lane,l)
src=B/'r12_c05/repairs-resume-20261012/integrated-local-v10/r12_c05.candidate.context.png';assembly=src.with_name('assembly.json');assert sha(src)=='29f28eccdf3adee08173b25eeb322e9946285140cb1f032a198ebd4765e9f57c';im=Image.open(src).convert('RGB');anchor=P/'anchors/r12_c05-v10-bottom230.native.png';anchor.parent.mkdir(exist_ok=True,parents=True);im.crop((0,4096,4326,4326)).save(anchor)
write(str(anchor)+'.derivation.json',{'file':str(anchor),'sha256':sha(anchor),'source':ref(src),'sourceAssembly':ref(assembly),'sourceCandidateStatus':'parent independently verified provisional; formalAccepted false','sourceContextBox':[0,4096,4326,4326],'sourceWorldBox':[16269,49037,20595,49267],'operation':'exact native crop only','sourceResampling':False,'gameArtNative':True,'formalAccepted':False})
sheet=Image.new('RGB',(1024,1088),(35,35,35));draw=ImageDraw.Draw(sheet)
for r in range(1,5):
 for c in range(1,5):
  guide=T/'guides'/f'p{r:02d}_{c:02d}.layout-only.png';g=Image.open(guide).convert('RGB');sheet.paste(g.resize((256,256),Image.Resampling.NEAREST),((c-1)*256,(r-1)*272));draw.text(((c-1)*256+8,(r-1)*272+257),f'p{r:02d}_{c:02d} layout guide only',fill='white')
sheet.save(P/'qa/layout-contact-resized.png') if (P/'qa').exists() else None
(P/'qa').mkdir(exist_ok=True);sheet.save(P/'qa/layout-contact-resized.png')
write(P/'lane-state-20261012.json',{'tile':'r13_c05','owner':'/root/sol_r12_repair_20261012','status':'native_production_active','startedAtUtc':now,'selectedNativeSlots':0,'plannedNativeSlots':16,'activePatch':'p01_01','topAnchor':ref(anchor),'mandatoryReferenceCount':3,'actualModel':None,'actualQuality':None,'internalAccepted':False,'formalAccepted':False,'nextStep':'Generate16 native1254 patches with exact saved prompts/refs; assemble each row and native QA; independent root final review.'})
print(json.dumps({'tile':'r13_c05','topAnchor':str(anchor),'r12Checkpoint':str(lane),'layoutContact':str(P/'qa/layout-contact-resized.png')}))
