import sys,json
from pathlib import Path
Z=Path(__file__).resolve().parent.parent
D=Z/'stair-rebuild'
stem=sys.argv[1]
p=D/(stem+'.request.json')
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['references']=[d['references'][0],d['references'][3],d['references'][4]]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=D/(stem+'.prompt.txt')
text=q.read_text(encoding='utf-8')
start=text.index('In this crop, projected nose lines')
stop=text.index('\nPreserve all old')
text='Use case: precise-object-edit. EDIT IMAGE 1 ONLY and preserve its exact composition and camera. This is a small cropped detail of a larger Chinese Daoist chibi town staircase, not a complete scene. Render a native 1254 x 1254 square. Image 1 has a crisp grey paved landing at the top and coarse stone stair guidance at the bottom. Replace ONLY the coarse stair pixels with newly painted fine native detail. Follow the exact diagonal step count and spacing shown in IMAGE 1. The upper floor must stay unchanged. Images 2 and 3 are style references only, not content or composition; copy NO objects or architecture from them. Fine painterly warm grey limestone, softly beveled rounded corners, subtle stippled grey-blue and cream surface texture, sunny soft light; natural muted grey-blue upper paving.\n'+text[start:stop]+'\nThis specific crop contains only paving, stair treads and a right-edge fragment of stone sidewall. ABSOLUTELY NO LANTERNS, NO POLE, NO HOUSE, NO FIGURES, NO SYMBOLS, NO NEW OBJECTS. Do not zoom out. Do not change crop or stone silhouette. No giant marble veins. All bottom and left-cut stair surfaces simply continue outside this image. Smoothly connect the existing fine upper landing with the new fine stair faces. Make the result a precise refinement of IMAGE 1 with high native surface detail.'
descriptions={
 'p01_02':'Upper landing of grey slabs at top and a partial existing large red lantern with gold motif at lower left. Keep this same cropped lantern silhouette, ornament and loop exactly; do not add its pole or whole lamp. The stairs occupy the lower right and continue off-frame. Preserve existing fine native overlap at the rightmost 230 pixels and make each stair nose continuous into it.',
 'p01_03':'Only grey landing, stair treads and a right-edge stone wall fragment. No lanterns or poles or new objects.',
 'p01_04':'The existing descending stone sidewall spans diagonally through the center, yellow sand at right, stair flight at far left. Preserve wall exterior and sand. Continue the leftmost 230-pixel fine native band exactly to the existing wall, with no guide material cut.',
 'p02_01':'Existing two cropped red lanterns with elaborate gold motifs and red tassels, and one original brown wood pole in the middle. Keep their exact silhouettes, colors, motifs and pixels. Rebuild only visible staircase behind them at right, with six globally coherent noses. Original left stone sidewall and sand remain. Do not replace lanterns by plain rectangular lanterns or replace wood pole with a metal pole.',
 'p02_02':'One existing cropped large red lantern at upper left and its gold bottom ring, round gold bead and long red tassel. Preserve this exact lantern. The rest is six-step staircase; continue behind the lantern without introducing extra treads. Preserve newly detailed top and right 230-pixel neighbor strips and connect all steps smoothly.',
 'p02_03':'Close-cropped stair flight across the whole upper part, with lowest steps and the lower grey paved road toward bottom right if present in Image 1. No lantern, no pole, no new objects. Preserve corrected native top neighbor strip and continue every nose exactly.',
 'p02_04':'Bottom of the existing descending stone sidewall at upper right and central right, broad grey road toward bottom, stair ends at left. No new objects, no new post. Preserve corrected native top and left neighbor overlap. Connect each stair continuously to the original wall inner face; keep the outer wall silhouette and lower road boundary.',
 'p03_01':'Original large brown wooden lamp pole and dark stone foot in the center, warm sandy ground around it, and bottom-left ends of the staircase at upper right. Preserve exact pole, foot and sand. Do not add a freestanding stone post. Correct only existing exposed lowest stair ends at upper right, matching the six-step structure. Keep the road and sand footprint.',
 'p03_02':'Lowest staircase ends occupy top and left, grey paved road below/right, yellow sandy ground at lower left if visible. No new post, no pole and no lantern. Preserve original sand/road footprint. Correct any old extra stair stubs into one coherent bottom riser and then clear lower road.',
 'p03_03':'Grey paved lower road with the very lowest stair edge near top if shown. No extra stair, no new object, no lantern. Connect corrected top and left overlap precisely and keep ground slab joints quiet and natural.'}
patch=d['patch']
start=text.index('This specific crop contains')
text=text[:start]+'THIS PATCH CONTENT AND PRESERVATION: '+descriptions[patch]+' Do not zoom out or change crop. No new architecture, figures, text or symbols. Preserve all clean native neighboring overlap bands in the exact Image 1 positions, and keep all objects outside the stair flight unchanged. Remove ONLY the low-resolution guide texture and any accidental rectangular guide-paste cut by painting newly detailed stone, without preserving wrong old stair subdivisions.'
q.write_text(text+'\n',encoding='utf-8')
print(json.dumps({'stem':stem,'refs':[r['path'] for r in d['references']],'prompt':text},ensure_ascii=False))
