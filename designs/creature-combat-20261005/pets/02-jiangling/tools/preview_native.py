"""Offline PNG-only native preview. No browser, network, image edits or interpolation.

Default is read-only. --record qa/native-playback-session.json records rendering,
not a visual acceptance result. Requires the existing Python, Pillow and Tk.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
SIZE = 448


def utc():
    return datetime.now(timezone.utc).isoformat()


class Preview:
    def __init__(self, record=None):
        self.record = record
        self.window = tk.Tk()
        self.window.title("Jiangling - Native Animation Review")
        self.window.geometry("980x650")
        self.window.configure(bg="#f3eddf")
        self.action, self.speed, self.playing = "hit", 1, True
        self.tick_index, self.last_key = 0, None
        self.images, self.sources = {}, []
        self.events, self.display_log = [], []
        self.coverage = defaultdict(lambda: {"framesSeen": set(), "displayCount": 0, "maxCycle": 0})
        self.session_start = utc()
        self.started = time.perf_counter()
        self.last_saved = self.started
        self.closed = False
        tk.Label(self.window, text="绛铃 · 原生离线预览 / E 与 W 同步", font=("Microsoft YaHei", 18, "bold"), bg="#194f47", fg="#fff6df", pady=10).pack(fill="x")
        bar = tk.Frame(self.window, bg="#f3eddf")
        bar.pack(pady=8)
        for key, label, action in [("1", "受击", "hit"), ("2", "普攻", "attack"), ("3", "施法", "cast")]:
            tk.Button(bar, text=f"{key}  {label}", width=10, command=lambda a=action: self.select_action(a)).pack(side="left", padx=3)
            self.window.bind(key, lambda event, a=action: self.select_action(a))
        for key, label, speed in [("n", "N  正常 1×", 1), ("s", "S  慢放 0.25×", .25)]:
            tk.Button(bar, text=label, width=15, command=lambda s=speed: self.select_speed(s)).pack(side="left", padx=3)
            self.window.bind(key, lambda event, s=speed: self.select_speed(s))
        tk.Button(bar, text="空格 播放/暂停", command=self.toggle).pack(side="left", padx=3)
        self.status = tk.StringVar()
        tk.Label(self.window, textvariable=self.status, font=("Consolas", 13, "bold"), bg="#f3eddf", fg="#194f47").pack()
        panels = tk.Frame(self.window, bg="#f3eddf")
        panels.pack(pady=5)
        self.canvases, self.items = {}, {}
        for direction, label in [("E", "E · 斜前朝右下"), ("W", "W · 真正斜后朝左上")]:
            panel = tk.Frame(panels, bg="#f3eddf")
            panel.pack(side="left", padx=10)
            tk.Label(panel, text=label, font=("Microsoft YaHei", 12), bg="#f3eddf").pack()
            canvas = tk.Canvas(panel, width=SIZE, height=SIZE, highlightthickness=0)
            canvas.pack()
            self.canvases[direction] = canvas
            self.items[direction] = canvas.create_image(0, 0, anchor="nw")
        tk.Label(self.window, text="← / → 逐帧并暂停   空格继续   Esc退出 | 固定画布缩放；不对齐脚底、不插值、不改正式PNG", bg="#f3eddf", fg="#675e4d").pack(pady=6)
        self.window.bind("<space>", lambda event: self.toggle())
        self.window.bind("<Left>", lambda event: self.step(-1))
        self.window.bind("<Right>", lambda event: self.step(1))
        self.window.bind("<Escape>", lambda event: self.close())
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        checker = Image.new("RGBA", (SIZE, SIZE), "#e7e4db")
        draw = ImageDraw.Draw(checker)
        for y in range(0, SIZE, 28):
            for x in range(0, SIZE, 28):
                if (x // 28 + y // 28) % 2:
                    draw.rectangle((x, y, x + 27, y + 27), fill="#cfcec6")
        for action, (count, _) in ACTIONS.items():
            for direction in ("E", "W"):
                self.images[action, direction] = []
                for n in range(1, count + 1):
                    path = ROOT / "runtime" / action / direction / f"{n:02d}.png"
                    self.sources.append({"file": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                    with Image.open(path) as original:
                        assert original.size == (1024, 1024) and original.mode == "RGBA", str(path)
                        display = checker.copy()
                        display.alpha_composite(original.resize((SIZE, SIZE), Image.Resampling.LANCZOS))
                    self.images[action, direction].append(ImageTk.PhotoImage(display))
        self.started = time.perf_counter()
        self.event("start")
        self.window.after(0, self.update)

    def event(self, kind):
        self.events.append({"at": utc(), "kind": kind, "action": self.action, "speed": self.speed, "playing": self.playing})

    def reset(self):
        self.tick_index, self.last_key = 0, None
        self.started = time.perf_counter()
        self.playing = True

    def select_action(self, action):
        self.action = action
        self.reset()
        self.event("action")

    def select_speed(self, speed):
        self.speed = speed
        self.reset()
        self.event("speed")

    def toggle(self):
        self.playing = not self.playing
        self.started = time.perf_counter() - self.tick_index * ACTIONS[self.action][1] / (1000 * self.speed)
        self.last_key = None
        self.event("play" if self.playing else "pause")

    def step(self, delta):
        self.playing = False
        self.tick_index = (self.tick_index + delta) % ACTIONS[self.action][0]
        self.last_key = None
        self.event("step")

    def update(self):
        count, ms = ACTIONS[self.action]
        now = time.perf_counter()
        if self.playing:
            self.tick_index = int((now - self.started) * 1000 * self.speed / ms)
        index, cycle = self.tick_index % count, self.tick_index // count + 1
        key = (self.action, self.speed, index, cycle, self.playing)
        if key != self.last_key:
            for direction in ("E", "W"):
                self.canvases[direction].itemconfigure(self.items[direction], image=self.images[self.action, direction][index])
            self.status.set(f"{self.action.upper()} | {'PLAYING' if self.playing else 'PAUSED'} | {self.speed:g}x | Frame {index + 1:02}/{count:02} | Cycle {cycle} | {ms / self.speed:g} ms/frame")
            self.last_key = key
            row = {"at": utc(), "action": self.action, "speed": self.speed, "frame": index + 1, "cycle": cycle, "playing": self.playing}
            self.display_log.append(row)
            self.display_log = self.display_log[-6000:]
            if self.playing:
                c = self.coverage[f"{self.action}:{self.speed:g}"]
                c["framesSeen"].add(index + 1)
                c["displayCount"] += 1
                c["maxCycle"] = max(c["maxCycle"], cycle)
                c.setdefault("firstAt", row["at"])
                c["lastAt"] = row["at"]
        if self.record and now - self.last_saved >= 2:
            self.save()
            self.last_saved = now
        self.window.after(5, self.update)

    def save(self):
        if not self.record:
            return
        report = {"startedAt": self.session_start, "savedAt": utc(), "closed": self.closed,
                  "tool": "Python Tk/Pillow offline PNG-only renderer", "sourceFrames": self.sources,
                  "operation": "1024-to-448 uniform full-canvas display over checkerboard; original PNGs unchanged; no interpolated frames",
                  "visualAcceptance": "not_automatically_assessed; rendering logs do not establish a human/model visual review",
                  "events": self.events, "coverage": {k: {**v, "framesSeen": sorted(v["framesSeen"])} for k, v in self.coverage.items()},
                  "displayLogLimit": 6000, "displayLog": self.display_log}
        self.record.parent.mkdir(parents=True, exist_ok=True)
        temp = self.record.with_suffix(".json.tmp")
        temp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.record)

    def close(self):
        self.closed = True
        self.event("close")
        self.save()
        self.window.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", help="Optional log path within this pet directory. Omit for read-only preview.")
    args = parser.parse_args()
    record = (ROOT / args.record).resolve() if args.record else None
    if record and (ROOT not in record.parents or record.suffix.lower() != ".json"):
        parser.error("The optional record must be a JSON path within this pet directory.")
    Preview(record).window.mainloop()
