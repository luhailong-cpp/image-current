import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
for t,p in [('r10_c03','block2x2-r09r10c03c04-v1'),('r10_c07','block2x2-r09r10c06c07-v2'),('r11_c06','pair-r10r11c06-final-v5')]:
 out=z/'qa'/f'{p}-{t}-root-composition-preview.png'
 if not out.exists():
  im=Image.open(z/'qa'/f'{p}-{t}-candidate-4096.png');im.thumbnail((1400,1400));im.save(out)
left=Image.open(z/'qa/pair-r10r11c06-final-v5-r10_c06-context-native.png').convert('RGB')
right=Image.open(z/'qa/block2x2-r09r10c06c07-v2-r10_c07-context-native.png').convert('RGB')
out=z/'qa/pair-r10r11c06-final-v5-east-endpoint-100pct.png'
assert not out.exists()
im=Image.new('RGB',(690,600));im.paste(left.crop((3866,3726,4211,4326)),(0,0));im.paste(right.crop((115,3726,460,4326)),(345,0));im.save(out)
print('Created inspection previews and native endpoint crop')

