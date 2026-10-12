from pathlib import Path
import json
T=Path(__file__).resolve().parent
p=T/'local-content.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update({
 'p02_03':'Single existing gold pointed finial descends from top near x400 to its existing broad rounded base near x400 y600, joining the plain gold curved upper roof ridge across bottom. Native TOP already contains its exact tip; continue ONE identical tapered finial body, never add a second tip or neck. Native LEFT carries same gold ridge. Quiet pond occupies upper-right with cropped green leaf along top. Small teal roof wedge below ridge continues past bottom. No extra crown, knot, ornament, water petal, leaf or architecture; exact target partial framing.',
 'p03_02':'Only blue/teal tiled roof planes and existing plain gold ribs. One rib curves from top near x400 toward x850 y750 then descends toward x750 bottom; another thin gold line enters top-right and meets it around x950 y750. Existing lower curved gold ridge enters left around y500. Match all native top/left gold edges and tile row directions. Roof planes continue beyond every crop edge where shown: no terminal tile end caps, complete building, finial, new tier, ornament, vegetation or pond within the blue roof area. Keep exact U-like gold rib network of guide.',
 'p04_01':'Existing blue tiled roof occupies upper-right; thin golden outside edge descends from top near x650 and curves toward far-right around y650. Existing vermilion corner-tower wall/column is cropped along right and bottom-right, with the small existing pale grey-tan post fragment at lower-middle. Existing green pond foliage/large lotus leaf occupies left, inherited from native top/left. Keep local silhouettes exact and the narrow water gaps. No new flower, extra leaf cluster, tree, window, separate building, tier or gold ornament; preserve cropped framing.'
})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
