from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from export_frame import run
ROOT=Path(__file__).resolve().parents[1]
versions={1:2,2:2,3:3,4:3,5:3,6:3,7:4,8:3,9:2,10:2,12:2,14:3,15:3,16:2}
for i in range(1,17):
    src=ROOT/'run'/'staging'/f'run-E-{i:02d}-v{versions.get(i,1)}.png'
    run(src,ROOT/'run'/'E'/f'{i:02d}.png')
