from pathlib import Path
import base64, hashlib, json, math, re
from datetime import datetime, timezone
from PIL import Image

OUT = Path(__file__).resolve().parent
CLIENT = Path('D:/work/mmorpg-client')
ART = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
paint_path = CLIENT/'Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs'
text = paint_path.read_text(encoding='utf-8-sig')
encoded = re.search(r'private const string WalkMaskBase64\s*=([\s\S]+?);', text).group(1)
raw = base64.b64decode(''.join(re.findall(r'"([A-Za-z0-9+/=]+)"', encoded)))
bits = [bool(raw[i >> 3] & (0x80 >> (i & 7))) for i in range(150 * 150)]
walk_cells = sum(bits)
scenarios=[]
for per_person in (16,25,36):
    for walk_fraction in (.35,.45,.60,.70):
        needed=5000*per_person*1.25
        smaller_side=math.sqrt(needed/walk_fraction)
        main_side=smaller_side/math.sqrt(.75)
        scenarios.append(dict(perPersonWorldArea=per_person,reserveMultiplier=1.25,
            requiredWalkableWorldArea=needed,assumedSmallerMapWalkableFraction=walk_fraction,
            villageIslandWorldSide=smaller_side,mainWorldSide=main_side,
            main4kGridSideAtLegacyHdDensity=math.ceil(main_side/(300/16)),
            villageIsland4kGridSideAtLegacyHdDensity=math.ceil(smaller_side/(300/16))))
contracts=[]
for name in ('main-city-game-20261009','fishing-village-game-20261009','island-game-20261009'):
    p=ART/name/'production-contract.json'; obj=json.loads(p.read_text(encoding='utf-8-sig'))
    contracts.append(dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        artCanvasPixels=obj['artCanvasPixels'],worldSize=obj['worldSize'],
        capacity5000Validated=obj['capacity5000Validated'],worldAreaRatioToMain=obj.get('worldAreaRatioToMain',1)))
samples=[]
for relative in ('QdaoOriginalRosterV13/00_reference_topright_boy/idle/S.png',
                 'QdaoOriginalRosterV13/01_ice_sword_girl/idle/S.png',
                 'QdaoOriginalRosterV14/06_thunder_caster_boy/idle/S.png',
                 'QdaoOriginalRosterV14/20_star_formation_master_girl/idle/S.png'):
    p=CLIENT/'Assets/Resources/World/Characters'/relative
    if not p.exists():
        samples.append(dict(path=p.as_posix(),exists=False)); continue
    with Image.open(p) as im:
        alpha=im.getchannel('A'); bbox=alpha.point(lambda a: 255 if a>=16 else 0).getbbox()
        ppu=104 if im.width==1024 else 52
        samples.append(dict(path=p.as_posix(),exists=True,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            dimensions=list(im.size),alphaThreshold=16,bbox=list(bbox),ppu=ppu,
            opaqueWidthWorld=(bbox[2]-bbox[0])/ppu,opaqueHeightWorld=(bbox[3]-bbox[1])/ppu,
            frameWorldHeight=im.height/ppu,footPivotYNormalized=.08,
            note='Selected stored idle frame, includes costume/weapon silhouette; not all roster maximum or runtime validation.'))
evidence=[]
for relative in ('Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs',
                 'Assets/Scripts/World/Tianyong/TianyongMapDefinition.cs',
                 'Assets/Scripts/World/Tianyong/TianyongMapConfig.cs',
                 'Assets/Resources/World/Tianyong/TianyongMapConfig.asset',
                 'Assets/Scripts/World/QdaoBoySpriteAnimator.cs',
                 'Assets/Scripts/World/QdaoCharacterCatalog.cs',
                 'Assets/Scripts/World/QdaoMixedResolutionContract.cs',
                 'Assets/Scripts/World/WorldNameplate.cs',
                 'Assets/Scripts/World/WorldLabelBillboard.cs',
                 'Assets/Scripts/World/Tianyong/CityTileStreaming.cs',
                 'Docs/CityTiles4K.md'):
    p=CLIENT/relative; evidence.append(dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
data=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),scope='Read-only planning; no client, shared production contract or images modified',
    capacity5000Validated=False,clientAgensExists=(CLIENT/'AGENTS.md').exists(),
    legacy=dict(worldRect=dict(x=50,y=0,width=300,height=300),maskResolution=150,navCellSide=2,
        walkableCells=walk_cells,walkableWorldArea=walk_cells*4,walkableFraction=walk_cells/22500,
        walkableWorldAreaPer5000=walk_cells*4/5000,meanSquarePitch=math.sqrt(walk_cells*4/5000),
        imagePixels=6144,sourcePixelsPerWorldUnit=6144/300,
        plannedHdImagePixels=65536,plannedHdPixelsPerWorldUnit=65536/300),
    actor=dict(frameWorldHeight=512/52,shadowWidth=2.9,shadowHeight=2.9*.66,
        feetRootAuthoritative=True,physicsRadius=.38,nameEmWorldHeightNormalZoom=1.25,
        nameBelowFeetDefault=.15+2.9*.66/2+1.25/2+.1,
        nameWidthUnboundedByTruncation=True,nearestZoomNameScaleAdaptive=True),
    selectedSpriteSamples=samples,contracts=contracts,scenarios=scenarios,evidence=evidence)
(OUT/'capacity-calculation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(legacy=data['legacy'],samples=samples,scenarios=scenarios),ensure_ascii=False,indent=2))
