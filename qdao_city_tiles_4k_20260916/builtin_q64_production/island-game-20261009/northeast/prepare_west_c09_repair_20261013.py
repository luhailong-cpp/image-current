from native_work import *
import sys
base,ident=sys.argv[1:3]
assert base.startswith('r04_c09_') and ident.startswith(base+'_v')
source=ZONE/'native'/f'{base}.png';refs=read(ZONE/'prompts'/f'{base}.inputs.json')
ref=[{'file':source.as_posix(),'sha256':sha(source),'role':'edit target: native image requiring removal of one horizontal surface-material boundary'},*refs[2:]]
ip=ZONE/'prompts'/f'{ident}.inputs.json';fp=ZONE/'prompts'/f'{ident}.prompt.txt';assert not ip.exists() and not fp.exists()
write(ip,ref)
fp.write_text('Use case: precise-object-edit. Edit image1, keep its exact 1254x1254 framing and every stone grout contour and slab position unchanged. Fix only the straight horizontal surface-texture cutoff at y230 across the upper-left and upper-middle: the tiny-grid stone texture above it and natural mottling below it currently end on a ruler-straight line. Repaint stone FACE TEXTURE across this cutoff into a smooth, natural, hand-painted stone material transition following whole slab faces, extending irregular subtle mineral mottling through the boundary so no straight horizontal division is visible. Preserve existing outer115px edge colors and geometry exactly for adjoining map tiles. Keep the RIGHT strip aligned, all grout junctions fixed, all stone scales unchanged, all perspective and daylight unchanged. Do not add or remove any stone grout lines or moss. No objects, text, UI, decorations, blur or reframing. Images2-4 are approved layout and Daoist painting references only. Return one opaque native square1254x1254.',encoding='utf-8')
p=source.with_suffix('.png.generation.json');v=read(p);v.update(status='unselected_requires_local_material_repair',internalSeams='visible horizontal surface-texture cutoff at native y230');write(p,v)
print(json.dumps({'id':ident,'prompt':fp.read_text(encoding='utf-8'),'references':[r['file'] for r in ref]}))
