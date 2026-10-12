from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent.parent
for core in ['r01_c14_p01_01','r01_c14_p03_04']:
    dest=B/'qa'/f'{core}.repair-corner-native-compare.png'
    assert not dest.exists()
    panel=Image.new('RGB',(720,305))
    for i in range(2):
        im=Image.open(B/'native'/f'{core}_v{i+1}.png').convert('RGB')
        panel.paste(im.crop((100,850,460,1155)),(360*i,0))
    panel.save(dest)
print('Saved two original-scale before/after QA comparisons; final artwork unchanged.')
