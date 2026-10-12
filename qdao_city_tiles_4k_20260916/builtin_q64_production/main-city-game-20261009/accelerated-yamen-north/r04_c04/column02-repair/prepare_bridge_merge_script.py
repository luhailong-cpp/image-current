from pathlib import Path
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/column02-repair")
s=(d/"merge_three.py").read_text()
s=s.replace("merged-three-v1","merged-three-v2")
old='(D/"repair-v1-native.png",[13197,13709,14451,14963],D/"repair-v1-evidence.json","lower seam-centered native repair")]'
new='(D/"repair-v1-native.png",[13197,13709,14451,14963],D/"repair-v1-evidence.json","lower seam-centered native repair"),\n (D/"bridge-shading-work/bridge-v1-native.png",[13197,13258,14451,14512],D/"bridge-shading-work/bridge-v1-evidence.json","native red-lacquer shading continuity repair")]'
assert old in s
s=s.replace(old,new).replace("for idx in [3,4]:","for idx in [3,4,5]:")
old="topBand=[180,370] if idx==3 else [180,350];bottomBand=[975,1180]"
new="topBand={3:[180,370],4:[180,350],5:[120,300]}[idx];bottomBand=[830,945] if idx==5 else [975,1180]"
assert old in s
s=s.replace(old,new)
(d/"merge_three_bridge.py").write_text(s,encoding="utf-8")

