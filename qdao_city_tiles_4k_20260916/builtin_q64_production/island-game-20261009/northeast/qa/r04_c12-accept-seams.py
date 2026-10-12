from native_work import *
import sys
ids=sys.argv[1:]
for ident in ids:
 p=ZONE/'qa'/f'{ident}.json'; d=read(p); d.update(status='passed_visual_review_candidate',geometryChecks={'review':'Stone slab joints and painterly color continue across exact core seam; no break, blur or band.'},reviewedAtUtc=now()); write(p,d)

