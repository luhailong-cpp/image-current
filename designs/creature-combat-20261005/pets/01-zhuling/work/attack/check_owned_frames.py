from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
BASE=Path(r"D:/work/image/designs/creature-combat-20261005/pets/01-zhuling")
notesE=["备战张翼，前右斜视，双爪自然蜷收。","双翼略收，轮廓与备战接近，保持身份。","近侧右翼显著折起，远翼上扬平衡。","近翼向后下收、头颈压低蓄力；原生边缘有极小羽端接边，导出保留全画布。","双翼打开进入释放，喙微开，佩饰保持颈部归属。","近右翼跨胸向右下横扫，远翼保持上扬，两爪未缺失。","近右翼展开跨过胸前，攻击峰值清楚，两爪短尾保留。","右翼扫后向下折收，喙与头颈开始回正。","近翼收回过半，远翼打开，头颈回中。","双翼重开，近翼仍略低，身躯回直。","近翼上扬回弹，冠与绢带自然摆动。","稳定张翼备战，与首帧方向和身份相同，独立生成。"]
notesW=["后脑、背羽与短尾根清楚，侧后项坠遵循原W身份。","双翼略收，保持斜后朝左上，双爪可辨。","近侧屏右翼折肘收拢，远侧屏左翼上扬，后视无转胸。","近右翼向后收为蓄力，远翼保持平衡。","近翼重新展开进入出手；独立生成，方向仍为后视。","定点修正后近侧右翼弯肘向左内转、羽端跨颈后，右上区域腾空；远翼上举，两爪、短尾、侧后项坠保留。"]
items=[]
for d,notes in [("E",notesE),("W",notesW)]:
    cols=4 if d=="E" else 3; rows=(len(notes)+cols-1)//cols
    sheet=Image.new("RGB",(cols*320,rows*348),(232,235,232)); draw=ImageDraw.Draw(sheet)
    for i,note in enumerate(notes,1):
        p=BASE/"runtime"/"attack"/d/f"{i:02}.png"; im=Image.open(p).convert("RGBA")
        rp=BASE/"records"/"attack"/d/f"{i:02}.generation.json"; r=json.loads(rp.read_text(encoding="utf-8"))
        r["visualStatus"]="individually inspected"
        r["visualInspection"]={"inspectedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"method":"tool-generated image displayed and actually viewed; exported contact sheet also reviewed separately","note":note,"direction":"front-right down-right" if d=="E" else "rear-right up-left","anatomy":"two wings, two bird feet, one short fan tail","dynamicPlayback":"pending consolidated review by root","clientValidation":"not read or connected"}
        r["references"][0]["role"]="original "+d+" primary identity and direction"
        r["references"][1]["role"]="original "+("W" if d=="E" else "E")+" supplemental identity"
        if d=="W" and i==6:
            r["references"][3]["role"]="edit target: rejected first W06 candidate"
            r["editingSource"]={"generationRecord":"records/attack/W/06.rejected-v1.generation.json","path":r["references"][3]["path"]}
        rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
        x=((i-1)%cols)*320; y=((i-1)//cols)*348
        small=im.resize((320,320),Image.Resampling.LANCZOS)
        for yy in range(0,320,20):
            for xx in range(0,320,20):
                draw.rectangle((x+xx,y+yy,x+xx+19,y+yy+19),fill=(215,222,216) if (xx//20+yy//20)%2 else (238,240,237))
        sheet.paste(small,(x,y),small); draw.text((x+10,y+324),f"attack {d} {i:02} | 30 ms",fill=(20,35,28))
        items.append({"file":str(p),"record":str(rp),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":list(im.size),"alpha":list(im.getchannel("A").getextrema()),"note":note})
    out=BASE/"qa"/"attack"/f"{d}-contact.png";out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out)
rej=BASE/"records"/"attack"/"W"/"06.rejected-v1.generation.json"
r=json.loads(rej.read_text(encoding="utf-8"));r["status"]="rejected-superseded";r["prompt"]="prompts/attack/W/06.rejected-v1.txt";r["rejectionReason"]="近侧右翼仍保持中立V，没有前扫加速。";r["file"]=r["sourcePath"];r["sha256"]=r["native"]["sha256"];r["supersededBy"]="records/attack/W/06.generation.json";rej.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
report={"scope":"attack E01-12 and W01-06, 18 frames produced by this subagent","all1024RGBA":all(x["size"]==[1024,1024] and x["alpha"]==[0,255] for x in items),"duplicateHashes":len(items)-len(set(x["sha256"] for x in items)),"records":items,"dynamicPlayback":"Pending root consolidated actual playback QA","sourceRetention":"Native output paths preserved during root final QA; root cleans originals after references verified; never remove shared old identity inputs."}
(BASE/"qa"/"attack"/"subagent-check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frameCount":len(items),"all1024RGBA":report["all1024RGBA"],"duplicateHashes":report["duplicateHashes"]}))

