import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
old='r12_c04_s02_03_v01';new='r12_c04_s02_03_v02'
r=load(ROOT/'prompts'/f'{old}.request.json')
r['references'][0]=metadata(ROOT/'native'/f'{old}.png','native edit target; repair internal vertical discontinuity only')
for k in ['submitted','submittedAtUtc','promptSha256']:r.pop(k,None)
assert not (ROOT/'prompts'/f'{new}.request.json').exists()
dump(ROOT/'prompts'/f'{new}.request.json',r)
dump(ROOT/'prompts'/f'{new}.coordinates.json',r['coordinates'])
