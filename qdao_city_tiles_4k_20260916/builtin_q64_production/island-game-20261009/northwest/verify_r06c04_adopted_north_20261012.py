from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
z=Path(__file__).resolve().parent
a=z/"tiles/r05_c04_candidate-v4_4096.png"
b=z/"tiles/connected-r04-r05-cross-v4/r05_c04_cross-paving-right-v1_4096.png"
aa=np.asarray(Image.open(a));bb=np.asarray(Image.open(b))
assert aa.shape==bb.shape==(4096,4096,3)
box=[0,2957,4096,4096]
equal=np.array_equal(aa[2957:4096],bb[2957:4096])
assert equal
rec=lambda p:{"path":p.as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
o={"schemaVersion":1,"oldReference":rec(a),"adoptedCurrent":rec(b),"comparisonBoxHalfOpen":box,"allPixelsEqual":equal,"southEdgeEqual":bool(np.array_equal(aa[-1],bb[-1])),"meaning":"All current core pixels used by derived r06_c04 north anchors are byte-identical to adopted connected r05c04; original archived halo unchanged. Old proof remains honest exact reference and is geometrically compatible with adopted north tile.","originalAnchorProof":rec(z/"guides/r06_c04_r05c04_v4_top_anchors.json")}
p=z/"qa/r06_c04_current_north_anchor_equivalence_20261012.json";assert not p.exists()
p.write_text(json.dumps(o,indent=2)+"\n",encoding="utf8")
print(json.dumps(rec(p)))

