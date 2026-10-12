from native_work import *

out = ZONE / 'qa/cross-zone-20261011'
review = read(out / 'review.json')
paths = [Path(review['records'][0]['upper']['file']), Path(review['records'][1]['upper']['file']), ZONE/'tiles/r03_c13.png', ZONE/'tiles/r03_c14.png']
canvas = Image.new('RGB', (1024, 1024))
boxes = [(3584,3584,4096,4096),(0,3584,512,4096),(3584,0,4096,512),(0,0,512,512)]
positions = [(0,0),(512,0),(0,512),(512,512)]
sources = []
for path, box, pos in zip(paths, boxes, positions):
    with Image.open(path) as im:
        assert im.size == (4096,4096)
        canvas.paste(im.crop(box),pos)
    sources.append({'file':path.as_posix(),'sha256':sha(path),'crop':list(box),'paste':list(pos)})
target = out/'r02-r03_c13-c14-cross-100pct.png'
canvas.save(target)
write(target.with_suffix('.png.derivation.json'),{'file':target.as_posix(),'sha256':sha(target),'sources':sources,'operation':'exact 512px corner crops and paste; no resizing or feathering','formalAccepted':False})
print(target.as_posix())
