"""Package exact existing PNG frames as APNG previews; never synthesizes frames."""
import json, hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
def main():
    records=[]
    for action,count,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
        for direction in ['E','W']:
            paths=[ROOT/'runtime'/action/direction/f'{i:02}.png' for i in range(1,count+1)]
            if not all(p.exists() for p in paths):continue
            frames=[Image.open(p).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS) for p in paths]
            for name,multiplier in [('normal',1),('quarter-speed',4)]:
                out=ROOT/'preview'/f'{action}-{direction}-{name}.apng'
                frames[0].save(out,format='PNG',save_all=True,append_images=frames[1:],duration=[ms*multiplier]*count,loop=0,disposal=0,blend=0,optimize=False)
                with Image.open(out) as check:
                    durations=[]
                    for i in range(check.n_frames):check.seek(i);durations.append(check.info.get('duration'))
                    assert check.n_frames==count and durations==[ms*multiplier]*count
                records.append({'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':f'records/{action}-{direction}/{i+1:02}.generation.json'} for i,p in enumerate(paths)],'operation':'uniform resize to 512 and ordered APNG packaging without interpolation','frames':count,'durationMs':durations,'playbackVisualStatus':'not-verified'})
    (ROOT/'preview'/'animation-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'previewFiles':len(records),'encodingChecks':'frame count and exact millisecond durations checked; not visual playback approval'}))
if __name__=='__main__':main()
