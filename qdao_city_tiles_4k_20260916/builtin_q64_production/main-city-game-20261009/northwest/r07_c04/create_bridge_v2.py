from pathlib import Path
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c04')
s=(p/'native_bridges_v1.py').read_text(encoding='utf-8')
s=s.replace("  pixels[y:y2,x:x2][mask]=b[mask]", "  for ex in item.get('excludedRectangles',[]):\n   a,c,e,f=ex;assert 0<=a<e<=1254 and 0<=c<f<=1254\n   mask[c:f,a:e]=False\n  pixels[y:y2,x:x2][mask]=b[mask]")
s=s.replace("changedPixels=int(mask.sum()),border=w,paths=", "changedPixels=int(mask.sum()),border=w,excludedRectangles=item.get('excludedRectangles',[]),paths=")
assert not (p/'native_bridges_v2.py').exists()
(p/'native_bridges_v2.py').write_text(s,encoding='utf-8')

