from pathlib import Path
import json
T=Path(__file__).resolve().parent
p=T/'local-content.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update({
 'p01_03':'Calm turquoise pond, existing broad green lotus leaf cropped across lower-right, tiny pre-existing pink petal fragment entering far-right. Existing gold corner-tower finial TIP enters from bottom near x400, only its upper tip is visible; do not fit the whole finial or roof into this patch. Preserve exact silhouettes and quiet water between these partial objects. Existing pale timber-base sliver upper-left belongs to the same support in native left anchor. No new flowers, posts, leaves, fish, boat, architecture or complete object.',
 'p02_02':'Continue the existing large pale pink/cream lotus cropped at left, existing green leaf cropped top, and the single approved gold upper roof scroll/ridge occupying bottom and right. Its upturned curl sits near lower-left of the gold ridge; the central finial base is beyond far-right. Quiet turquoise pond remains central. Match native flower and leaf silhouettes at top/left anchors. This is an enlarged detail of one corner-tower roof, not an entire roof or building; no extra decoration, petals, leaf, rooftop tier or object.',
 'p03_01':'Existing single lower gold roof eave curls upward around x600 y400 then sweeps to far-right, with a slim gold rib descending near x650 and blue tiled roof cropped at lower-right. Pond fills upper/left background, existing lotus fragment touches upper-left and existing soft green foliage hugs lower-left beside the tower. Preserve this exact partial eave silhouette; no extra curl, rooftop tier, freestanding plant, flower, fish or other architecture. Rounded hand-painted gold, quiet cyan water and densely resolved teal roof tiles.'
})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'updated':list(d),'count':len(d)}))
