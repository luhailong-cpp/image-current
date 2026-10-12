from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent/'r11_c10'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
m=read(T/'colorpass-selected.json');old=read(T/'selected-patches.json')
old.update(patches=m['patches'],status='candidate_complete_internal_repair_QA_pending',internalReady=False,candidate=m['candidate']['file'],candidateSha256=m['candidate']['sha256'])
write(T/'selected-patches.json',old)
gens=list(T.rglob('*.png.generation.json'))
write(T/'progress.json',{'tile':'r11_c10','generatedNativeImageCount':len(gens),'selectedNativeCount':16,'remainingPositions':[],'complete4kCandidateCount':1,'internalReady4kCount':0,'formalAcceptedCount':0,'status':old['status'],'candidate':m['candidate'],'pending':['independent adopted G1/Q1 boundaries','final color 24 seams and 9 crossings','final north and west external review']})
print(json.dumps({'nativeImageCount':len(gens),'candidate':m['candidate']}))

