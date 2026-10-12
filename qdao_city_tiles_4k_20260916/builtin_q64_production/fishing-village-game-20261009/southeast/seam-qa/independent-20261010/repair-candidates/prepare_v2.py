import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence
s=Sources()
record=write_evidence(s,HERE,'east-deck-v2-input',[32200,37888,33454,39142],{'actualTileEdgeGlobalX':32768,'source':'current native selections, never prior generated repair'})
print(json.dumps(record))
