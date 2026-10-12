from pathlib import Path
from PIL import Image
import json, hashlib, sys
z=Path(__file__).resolve().parent.parent
name=sys.argv[1]
target=Image.open(z/'native'/f'{name}.png').convert('RGB')
top=Image.open(z/'native/r06_c12_p12-bridge-candidate.png').convert('RGB')
left=Image.open(z/'native/r06_c12_p21-v2.png').convert('RGB')
right=Image.open(z/'native/r06_c12_p23-v1.png').convert('RGB')
out=Image.new('RGB',(1536,1024))
out.paste(left.crop((883,115,1139,1139)),(0,0))
out.paste(target.crop((115,115,1139,1139)),(256,0))
out.paste(right.crop((115,115,371,1139)),(1280,0))
out.save(z/'qa'/f'{name}-left-right-seams.png')
out=Image.new('RGB',(1024,512))
out.paste(top.crop((115,883,1139,1139)),(0,0))
out.paste(target.crop((115,115,1139,371)),(0,256))
out.save(z/'qa'/f'{name}-top-seam.png')
print('Mechanical 1:1 seam strips saved; no blending or scaling')
