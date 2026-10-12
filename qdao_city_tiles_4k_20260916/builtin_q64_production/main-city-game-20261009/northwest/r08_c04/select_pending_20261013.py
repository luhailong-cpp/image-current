from pathlib import Path
import sys
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent))
import production_v2 as p
print(p.record_selection('r08_c04','s01_04','s01_04_fix01','Best repaired courtyard source; NW curb junction unpassed, south/east independent edges stable',str(T/'qa/source-review/s01_04_fix01/review.json')))
