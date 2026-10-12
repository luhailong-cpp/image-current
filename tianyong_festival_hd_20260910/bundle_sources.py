from pathlib import Path
import ast, shutil
root=Path(r'E:\work\image\tianyong_festival_hd_20260910')
source=Path(r'E:\work\mmorpg-client\tools\tianyong_tile_pipeline.py')
text=source.read_text(encoding='utf-8-sig')
tree=ast.parse(text)
lines=text.splitlines()
names={'_channel_stats','_match_color','_minimum_vertical_seam','_append_with_minimum_seam'}
blocks=['"""Local copy of existing mechanical seam/color helpers; no art generation."""','import numpy as np','from PIL import Image, ImageStat, ImageFilter','']
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in names:
        blocks.append('\n'.join(lines[node.lineno-1:node.end_lineno]))
(root/'seam_helpers.py').write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
build=root/'build_hd_city.py'
code=build.read_text(encoding='utf-8-sig')
code=code.replace('SOURCE = Path(r"E:\\work\\image\\tianyong_festival_stylematch_20260910\\tianyong-jade-gold-main-city-native.png")','SOURCE = ROOT / "layout-source-native.png"')
code=code.replace('PIPELINE = Path(r"E:\\work\\mmorpg-client\\tools\\tianyong_tile_pipeline.py")','PIPELINE = ROOT / "seam_helpers.py"')
code=code.replace('if not prompt:\n', 'if len(prompt) < 200 or prompt.lower() in ("undefined", "null", "none"):\n')
build.write_text(code,encoding='utf-8')
shutil.copyfile(Path(r'E:\work\image\tianyong_festival_stylematch_20260910\tianyong-jade-gold-main-city-native.png'),root/'layout-source-native.png')
shutil.copyfile(Path(r'E:\work\image\tianyong_festival_stylematch_20260910\character-ui-style-reference.png'),root/'character-ui-style-reference.png')
(root/'requirements.txt').write_text('Pillow>=10\nnumpy>=1.24\n',encoding='utf-8')
ast.parse(code)
ast.parse((root/'seam_helpers.py').read_text())
print('Standalone mechanical helpers and references saved; prompt guard rejects placeholder strings.')
