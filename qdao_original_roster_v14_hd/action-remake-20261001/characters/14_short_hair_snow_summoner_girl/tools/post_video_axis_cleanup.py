from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,ast
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cleanup=read(R/'audit/video-axis-cleanup.json');qa=read(R/'audit/technical-qa.json')
assert qa['technicalPass']==196 and cleanup['removedCount']==50
assert not [p for p in (R/'run/staging').rglob('*') if p.is_file() and p.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.gif']]
for name in ['video-axis-final-review.json','video-axis-N-NE-review.json','video-axis-W-NW-review.json','video-axis-S-SE-SW-review.json']:
 p=R/'audit'/name;o=read(p);o['processImageRetention']={'status':'process_bitmaps_removed_after_final_review','record':'audit/video-axis-cleanup.json','textualEvidenceRetained':True,'currentVisualEvidence':'preview/run-{direction}-sheet.jpg and normal/slow.webp; current formal run/{direction}/*.png','note':'Any run/staging image path in this audit is historical reviewed process evidence, not a runtime dependency.'};o['rootFinalReview']='audit/video-axis-final-review.json';save(p,o)
p=R/'audit/bamboo-final-browser-review.json';o=read(p)
o['files']={f:sha(R/f) for f in o['files']};o['metadataHashesRefreshedAfterCleanup']=datetime.now(timezone.utc).isoformat();o['latestVisualEvidence']='audit/video-axis-final-review.json';save(p,o)
for p in (R/'tools').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for name in ['STATUS.md','MERGE_HANDOFF.md']:
 p=R/name;s=p.read_text(encoding='utf-8');s+='\n本次成品及引用核实后已删除50张本轮过程图，保留全部逐图文字来源、提示词和生成记录，见 `audit/video-axis-cleanup.json`。上一轮清理历史未覆盖。\n';p.write_text(s,encoding='utf-8')
print(json.dumps({'finalFrames':196,'runReviewed':128,'localRepairs':6,'previewFiles':42,'processImagesRemaining':0,'removedThisFollowup':50,'allPythonSyntax':'passed','previousCleanupHistoryPreserved':(R/'audit/bamboo-cleanup.json').exists()}))
