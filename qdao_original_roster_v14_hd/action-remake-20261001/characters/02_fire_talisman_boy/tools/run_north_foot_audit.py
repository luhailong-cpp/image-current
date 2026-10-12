"""Read-only sprite review compositions, written only beneath this character."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
for direction in ("W","N","NW"):
    panel=Image.new("RGB",(1664,1056),"#d9dce0")
    draw=ImageDraw.Draw(panel)
    for f in range(1,17):
        p=ROOT/f"frames/run/{direction}/{f:02}.png"
        im=Image.open(p).convert("RGBA")
        tile=im.crop((128,544,960,1024)).resize((416,240),Image.Resampling.LANCZOS)
        x=((f-1)%4)*416;y=((f-1)//4)*264
        panel.paste(tile,(x,y),tile)
        draw.rectangle((x,y+240,x+416,y+264),fill="#253540")
        draw.text((x+8,y+245),f"{direction} {f:02} / fixed crop diagnostic",fill="white")
    dest=ROOT/f"work/run-{direction}/foot-direction-contact.png"
    panel.save(dest)
    print(dest)

