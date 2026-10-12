from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/'r09_c03/pipeline/output/9f21c0744b4d7769/assembly.json';a=read(ap);q=ap.parent/'root-handoff-review-20261013';v=read(q/'verification.json')
assert sha(ap)==v['assemblySha256'] and v['native16SourcesAndReceiptHashesVerified'] and v['coreEqualsExactContextCrop']
report={**v,'actualRootVisualReview':'targeted_native_and_overview_actually_viewed_with_failures','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'rootActuallyViewed':['overview-QA-only.png','targeted-1.native.png','targeted-2.native.png'],'findings':['Target1 gold eave has a sharp polygonal gold shading/material front; gray paving remains densely cellular.','Target2 steel vessel has vertical metal/shading discontinuity and slight stepped gold-band contour at the native join.','Overview shows lantern suspension/knob separated above the cap; worker full review also reports lower connection failure. Existing cross-r09c02/r09c03 boundary issues remain.'],'scope':'Independent root targeted native inspection only; whole internal/external review and repairs remain open.','internalPassed':False,'formalAccepted':False}
rp=q/'root-review.json';assert not rp.exists();atomic_json(rp,report)
cat=read(B/'current-candidates.json');cat['tiles']['r09_c03']={'tile':'r09_c03','source':'current-native-provisional-with-open-QA','assembly':str(ap),'candidate':a['output'],'context':a['contextOutput'],'review':str(rp),'internalPassed':False,'formalAccepted':False}
cat.update(updatedAtUtc=report['reviewedAtUtc'],complete4kCandidateCount=len(cat['tiles']),formalAcceptedCount=0);atomic_json(B/'current-candidates.json',cat)
print(json.dumps({'catalogCount':len(cat['tiles']),'review':str(rp),'formalAccepted':0},ensure_ascii=False))
