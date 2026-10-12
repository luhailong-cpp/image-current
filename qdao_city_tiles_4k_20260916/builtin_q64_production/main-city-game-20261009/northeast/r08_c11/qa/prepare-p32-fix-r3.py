from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]
req=json.loads((p/'prompts/p32-v20261013-r2.request.json').read_text())
req['referenced_image_paths'][0]=str(p/'native/p32-v20261013-r2.png')
req['prompt']='Use case: precise-object-edit. Edit only the upper 1024 pixels of Image1, a 1254x1254 native paving patch. Keep the entire bottom230-pixel strip perfectly fixed. The upper painting has the WRONG small slab layout and texture. Replace that upper field by extending the EXACT very large limestone slabs visible at the bottom upward, making one continuous surface. At y1024 the ascending diagonal seam comes from x350 and must continue up-right toward x1254 around y490. The descending diagonal seam comes from x1030 and must extend up-left toward x0 around y280. These two main seams cross around x680 y830, with the same rounded deep blue-gray bevel as the fixed bottom. Continue their surrounding large slabs at the same scale; no small repeating diamond grid. Match the bottom stones pale gray intricate mineral texture and fine irregular warm micro-cracks across the entire upper area. Absolutely no horizontal transition at y1024: stone geometry and texture flow seamlessly across it. Preserve scale, camera, canvas1254x1254, daylight, fixed bottom stones and original ground-only layout. References2/3/4 support approved style only. No new objects, props, plants, stripes, text, frame, blur or resizing.'
ver='p32-v20261013-r3fix1'
for suffix,content in [('prompt.txt',req['prompt']),('request.json',json.dumps(req,indent=2))]:
 out=p/'prompts'/f'{ver}.{suffix}';assert not out.exists();out.write_text(content,encoding='utf-8')
print(json.dumps(req))
