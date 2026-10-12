from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1]
box=[900,1400,1200,1650];gb=[16384,36864]
for stem in ['r10_c05_s02_01_v01','r10_c05_s02_02_v01','r10_c05_panelbevel_v01']:
 rec=json.loads((R/'native'/f'{stem}.png.generation.json').read_text());b=rec['coordinates']['nativeGlobalBox']
 Image.open(R/'native'/f'{stem}.png').crop(tuple(box[i]+gb[i%2]-b[i%2] for i in range(4))).save(R/'qa'/f'{stem}-panel-native-crop.png')
