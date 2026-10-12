from pathlib import Path
import sys
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
sys.path.insert(0,str(R/'tools'))
from export_frame import run
for i in range(1,7): run(R/'hit/staging'/f'hit-E-{i:02d}-v11-side.png',R/'hit/E'/f'{i:02d}.png')
exec((R/'tools/registration_grids.py').read_text(),{'__file__':str(R/'tools/registration_grids.py')})

