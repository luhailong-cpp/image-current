from pathlib import Path
from PIL import Image
q=Path(__file__).resolve().parent/'r13_c12-sol-20261013-v01'
groups=[('water-h',[f'h{r}{c}' for r in [3,4] for c in range(1,4)],3),('row2-v',[f'v2{c}' for c in range(1,5)],1),('water-v',[f'v3{c}' for c in range(1,5)],2),('junctions',[f'junction_{r}{c}' for r in range(1,4) for c in range(1,4)],3)]
for name,names,cols in groups:
 first=Image.open(q/f'{names[0]}.png');w,h=first.size;sheet=Image.new('RGB',(w*cols,h*((len(names)+cols-1)//cols)),(50,50,50))
 for i,n in enumerate(names):sheet.paste(Image.open(q/f'{n}.png'),((i%cols)*w,(i//cols)*h))
 sheet.save(q/f'contact-{name}.png')
print('Actual unchanged crop pixels arranged in contact sheets; no resize or final-art modification.')
