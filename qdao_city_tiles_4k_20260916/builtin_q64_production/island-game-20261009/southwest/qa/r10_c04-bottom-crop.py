from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parent.parent
im=Image.open(r/'qa/c04-hardseam-r10c04-v01-candidate-4096.png')
im.crop((550,3400,1850,4096)).save(r/'qa/r10_c04-col12-bottom-native100.png')

