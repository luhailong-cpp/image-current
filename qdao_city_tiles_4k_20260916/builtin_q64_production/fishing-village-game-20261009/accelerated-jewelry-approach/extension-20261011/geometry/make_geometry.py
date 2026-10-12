from pathlib import Path
from PIL import Image, ImageDraw
import json
OUT=Path(__file__).resolve().parent
BASE=OUT.parents[1]
plan=json.loads((BASE/'coordinate-plan.json').read_text())
im=Image.open(plan['references'][0]['file']).convert('RGB')
for tile,x0,x1 in [('r05_c10',36864,40960),('r05_c11',40960,45056)]:
    box=(x0*1254/57344,16384*1254/57344,x1*1254/57344,20480*1254/57344)
    view=im.transform((896,896),Image.Transform.EXTENT,box,Image.Resampling.NEAREST)
    view.save(OUT/(tile+'-overview-nearest.png'))
    draw=ImageDraw.Draw(view)
    for n in range(1,4):
        draw.line((224*n,0,224*n,895),fill='magenta',width=2)
        draw.line((0,224*n,895,224*n),fill='magenta',width=2)
    for r in range(4):
        for c in range(4):
            draw.rectangle((c*224+3,r*224+3,c*224+43,r*224+20),fill='white')
            draw.text((c*224+6,r*224+5),f'p{r+1}{c+1}',fill='black')
    view.save(OUT/(tile+'-grid-layout-only.png'))
    prior=tile.replace('r05','r04'); version=2 if tile.endswith('10') else 3
    native=Image.open(BASE/prior/'candidate'/f'{prior}-4096-candidate-v{version}.png').convert('RGB')
    south=native.crop((0,3584,4096,4096))
    south.resize((2048,256),Image.Resampling.LANCZOS).save(OUT/(prior+'-south-context-preview.png'))
    for c in range(4): south.crop((c*1024,0,(c+1)*1024,512)).save(OUT/(prior+f'-south-c{c+1}-native.png'))
context=im.crop((790,330,1005,468)); context.resize((1075,690),Image.Resampling.NEAREST).save(OUT/'extension-overview-context-nearest.png')
print('Wrote layout-only enlarged source and unscaled actual south-edge crops into '+str(OUT))
