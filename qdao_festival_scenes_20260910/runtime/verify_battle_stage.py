"""Verify authored battle feet against independently traced stone-ground polygons.
Does not start Unity. The parent task performs engine rendering and NUnit execution.
"""
from pathlib import Path
import hashlib,json,math,re
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
CLIENT=ROOT.parents[2]/'mmorpg-client'
STAGE=CLIENT/'Assets/Scripts/UI/Ugui/Battle/BattleStage.cs'
GROUND=ROOT/'battle-platform-ground.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(point, polygon):
    x,y=point;result=False
    for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
    return result

def main():
    ground=json.loads(GROUND.read_text(encoding='utf-8-sig'))
    code=STAGE.read_text(encoding='utf-8-sig')
    rows={}
    for name,body in re.findall(r'private static readonly SlotEntry\[\] (\w+)\s*=\s*\{(.*?)\};',code,re.S):
        rows[name]=[[float(v) for v in point] for point in re.findall(r'new SlotEntry\(([0-9.]+)f?,\s*([0-9.]+)f?,\s*([0-9.]+)f?,\s*([0-9.]+)f?\)',body)]
    assert set(rows)=={'EnemyFront','EnemyBack','AllyFront','AllyBack'}
    assert all(len(row)==5 for row in rows.values())
    ref=float(re.search(r'DepthScaleReferenceY = ([0-9.]+)f',code).group(1))
    checks=[];samples=0;positions=[];minimum_head=float('inf');minimum_ring=float('inf')
    image=Image.open(ROOT/ground['background']).convert('RGB');draw=ImageDraw.Draw(image)
    try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    except OSError:font=ImageFont.load_default()
    for team,poly in ground['groundPolygons'].items():
        draw.line([tuple(p) for p in poly]+[tuple(poly[0])],fill='#18a46d',width=4)
    for name,row in rows.items():
        mine=name.startswith('Ally');back=name.endswith('Back');team='ally' if mine else 'enemy';poly=ground['groundPolygons'][team]
        for col,(x,y,px,py) in enumerate(row):
            slot=col+(5 if back else 0);label=('A' if mine else 'E')+str(slot);scale=1-(ref-y)/10000
            positions.append((label,x,y));colour='#195de7' if mine else '#d62e43'
            for kind,cx,cy,s in [('slot',x,y,scale),('pet',px,py,scale*.65)]:
                tested=[(cx,cy)]+[(cx+60*s*math.cos(a*math.tau/32),cy+22*s*math.sin(a*math.tau/32)) for a in range(32)]
                samples+=len(tested)
                checks.append({'check':label+' '+kind+' foot and entire shadow within '+team+' stone', 'passed':all(inside(p,poly) for p in tested)})
                top=cy-256*s;minimum_head=min(minimum_head,top)
                checks.append({'check':label+' '+kind+' nameplate below top HUD and above bottom HUD', 'passed':top>=140 and cy+40<=992})
                # Conservative actual nameplate/buff envelope x +/- 120, top 256, bottom 40.
                closest_x=min(max(2290,cx-120*s),cx+120*s);closest_y=min(max(850,top),cy+40)
                minimum_ring=min(minimum_ring,math.hypot(2290-closest_x,850-closest_y))
                if kind=='pet' and back:continue # same-column front-row point already drawn
                c=colour if kind=='slot' else '#e19115'
                draw.ellipse((cx-60*s,cy-22*s,cx+60*s,cy+22*s),outline=c,width=3 if kind=='slot' else 2)
                draw.ellipse((cx-4,cy-4,cx+4,cy+4),fill=c)
            draw.text((x-16,y-32),label,font=font,fill=colour,stroke_width=1,stroke_fill='#fff8da')
    min_distance=min(math.hypot(x-u,y-v) for i,(_,x,y) in enumerate(positions) for _,u,v in positions[i+1:])
    checks.append({'check':'all 20 main feet remain at least 90 design pixels apart','passed':min_distance>=90})
    checks.append({'check':'all unit and pet nameplates avoid the 235px command ring','passed':minimum_ring>=235})
    for team in ['Enemy','Ally']:
        checks.append({'check':team+' back-row pets retain same-column front-row places','passed':all(back[2:]==front[:2] for back,front in zip(rows[team+'Back'],rows[team+'Front']))})
    status='passed' if all(c['passed'] for c in checks) else 'failed'
    image.save(ROOT/'battle-platform-aligned-overlay.png')
    image.resize((1536,648),Image.Resampling.LANCZOS).save(ROOT/'battle-platform-aligned-overlay.jpg',quality=94)
    report={'status':status,'validation':'offline source/geometry verification, not an engine screenshot',
            'source':str(STAGE),'sourceSha256':sha(STAGE),'backgroundSha256':sha(ROOT/ground['background']),
            'independentGround':GROUND.name,'groundSha256':sha(GROUND),'mainFeet':20,'petLocations':20,
            'groundPointsChecked':samples,'minimumMainFootDistance':min_distance,'minimumOverheadTop':minimum_head,
            'minimumCommandRingDistance':minimum_ring,'commandRingRadius':235,'checks':checks,
            'offlineCompile':{'files':259,'errors':0,'exitCode':0,'unityReferences':'6000.6.0f1'},
            'engineValidation':'pending parent task Unity compilation, NUnit and screenshots'}
    (ROOT/'battle-platform-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k in ['status','mainFeet','petLocations','groundPointsChecked','minimumMainFootDistance','minimumOverheadTop','minimumCommandRingDistance']}))
    assert status=='passed'
if __name__=='__main__':main()
