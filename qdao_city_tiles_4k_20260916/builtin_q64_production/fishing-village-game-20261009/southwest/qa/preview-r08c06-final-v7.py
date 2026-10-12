import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
p=z/'qa/r08c06-south-final-v7-root-composition-preview.png'
assert not p.exists()
im=Image.open(z/'qa/r08c06-south-final-v7-r08_c06-candidate-4096.png');im.thumbnail((1400,1400));im.save(p)

