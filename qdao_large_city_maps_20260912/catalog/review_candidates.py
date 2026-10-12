from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,base64,io
files=[
r'E:\work\image\tianyong_festival_gptimage2_20260910\tianyong-festival-main-city-native.png',
r'E:\work\image\tianyong_festival_stylematch_20260910\tianyong-jade-gold-main-city-native.png',
r'E:\work\image\tianyong_festival_hd_20260910\tianyong_city_master_preview_2048.png',
r'E:\work\image\tianyong_city_6x6\Previews\tianyong_city_master_preview_2048.png',
r'E:\work\output\imagegen\qdao_city_v2_20260908\qdao_city_preview_1536.png',
r'E:\work\image\qdao_main_city_chibi_v1.png',
r'E:\work\image\qdao_gpt_image2_refresh_v7\scenes\main-city.raw.png',
r'E:\work\image\qdao_chibi_game_pack_v4\main-city_2560x1080.png',
r'E:\work\image\tianyong_city_6x6\Previews\tianyong_city_master_source_wide_1254.png']
sheet=Image.new('RGB',(1200,1320),'#f3eedf');d=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB'); size=im.size;im.thumbnail((390,390));x=(i%3)*400+(400-im.width)//2;y=(i//3)*440;sheet.paste(im,(x,y));d.text(((i%3)*400+10,y+395),f'{i+1}: {Path(p).name[:45]}',fill='black');d.text(((i%3)*400+10,y+413),str(size),fill='black');print(i+1,p,size)
p=Path(r'E:\work\image\qdao_large_city_maps_20260912\catalog\candidate-review.jpg');sheet.save(p,quality=90)
