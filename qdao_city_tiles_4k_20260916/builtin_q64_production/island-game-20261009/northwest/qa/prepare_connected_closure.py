from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest"); P=Z/"tiles/connected-r03-r04-c03-c04-v1"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
tiles=[]
for tid in ("r03_c03","r03_c04","r04_c03","r04_c04"):
 tiles.append(dict(tileId=tid,image=info(P/f"{tid}_connected_4096.png"),record=info(P/f"{tid}_connected_4096.connected-projection.json")))
out=Z/"qa/connected-closure-current-v1.manifest.json"
with out.open("x",encoding="utf8") as f:json.dump(dict(schemaVersion=1,tiles=tiles),f,indent=2)
R=Z.parents[1]/"parallel_20261005/daylight-only-20261009"
refs=[dict(**info(R/"penglai/penglai-natural-stone-wall-trees-v6.png"),role="sole approved full layout; no layout pixels as final"),dict(**info(R/"penglai/penglai-natural-stone-detail-v1.png"),role="independent stone, tree, wood and daylight material reference"),dict(**info(R/"user-references-20261009/mail-daoist-style.jpg"),role="primary approved rounded Daoist Q style reference")]
with (Z/"qa/connected-closure-base-references.json").open("x",encoding="utf8") as f:json.dump(refs,f,indent=2)
print(out)

