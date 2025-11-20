#!/usr/bin/env python3
"""
Agent Guesser — Clean Rebuild v2 (Letterboxed splash, safe redraw, robust loader)

Save as: agent_guesser_rebuilt_v2.py
Run: python agent_guesser_rebuilt_v2.py

Features:
- Letterboxed splash scaling (no cropping)
- Robust image loader: converts RGBA->RGB, resizes safely using PIL, falls back to tk.PhotoImage
- Safe redraw loop (no Configure race conditions)
- Single Tk root (no stray popup)
- Mode & Difficulty comboboxes wired to start new rounds immediately
- Particle background, SYS-themed panels
- Small generated WAV SFX saved at runtime (no bulky base64 embedded)
- Local leaderboard saved to leaderboard.json
- Uses local assets folder: ./assets/splashes/
"""

import os, sys, time, json, random, platform, subprocess, math, wave, struct
from pathlib import Path

# Optional Pillow
try:
    from PIL import Image, ImageTk, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

import tkinter as tk
from tkinter import ttk, messagebox

# Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(APP_DIR, "assets")
SPLASH_DIR = os.path.join(ASSETS_DIR, "splashes")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
LEADERBOARD_FILE = os.path.join(APP_DIR, "leaderboard.json")

os.makedirs(SPLASH_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)

# Theme
THEME = {
    "bg": "#0B1216",
    "panel": "#0F1A1E",
    "accent": "#FF4655",
    "muted": "#9EB0BA",
    "text": "#E6EEF2",
    "corner": "#FF8FA0",
    "panel_border": "#132026"
}

# --- Agents dataset ---
AGENTS = [
    {"name":"Jett","type":"Duelist","gender":"Female","country":"South Korea","abilities":["Cloudburst","Updraft","Tailwind","Blade Storm"]},
    {"name":"Phoenix","type":"Duelist","gender":"Male","country":"United Kingdom","abilities":["Curveball","Blaze","Hot Hands","Run It Back"]},
    {"name":"Sage","type":"Sentinel","gender":"Female","country":"China","abilities":["Barrier Orb","Slow Orb","Healing Orb","Resurrection"]},
    {"name":"Sova","type":"Initiator","gender":"Male","country":"Russia","abilities":["Shock Bolt","Recon Bolt","Owl Drone","Hunter's Fury"]},
    {"name":"Raze","type":"Duelist","gender":"Female","country":"Brazil","abilities":["Boom Bot","Blast Pack","Paint Shells","Showstopper"]},
    {"name":"Viper","type":"Controller","gender":"Female","country":"United States","abilities":["Snake Bite","Poison Cloud","Toxic Screen","Viper's Pit"]},
    {"name":"Neon","type":"Duelist","gender":"Female","country":"Philippines","abilities":["Relay Bolt","High Gear","Fast Lane","Overdrive"]},
    {"name":"Skye","type":"Initiator","gender":"Female","country":"Australia","abilities":["Regrowth","Trailblazer","Guiding Light","Seekers"]},
    {"name":"Reyna","type":"Duelist","gender":"Female","country":"Mexico","abilities":["Leer","Devour","Dismiss","Empress"]},
    {"name":"Killjoy","type":"Sentinel","gender":"Female","country":"Germany","abilities":["Turret","Nanoswarm","Alarmbot","Lockdown"]},
    {"name":"Brimstone","type":"Controller","gender":"Male","country":"United States","abilities":["Incendiary","Stim Beacon","Sky Smoke","Orbital Strike"]},
    {"name":"Yoru","type":"Duelist","gender":"Male","country":"Japan","abilities":["Fakeout","Gatecrash","Blindside","Dimensional Drift"]},
    {"name":"Fade","type":"Initiator","gender":"Female","country":"Turkey","abilities":["Prowler","Seize","Haunt","Nightfall"]},
    {"name":"Chamber","type":"Sentinel","gender":"Male","country":"France","abilities":["Trademark","Headhunter","Rendezvous","Tour De Force"]},
    {"name":"Cypher","type":"Sentinel","gender":"Male","country":"Morocco","abilities":["Trapwire","Cyber Cage","Spycam","Neural Theft"]},
    {"name":"Astra","type":"Controller","gender":"Female","country":"Ghana","abilities":["Gravity Well","Nova Pulse","Nebula","Astral Form"]},
    {"name":"Omen","type":"Controller","gender":"Male","country":"Unknown","abilities":["Shrouded Step","Paranoia","Dark Cover","From the Shadows"]},
]

VOICE_LINES = [
    {"agent":"Jett","line":"Let's go! I'm ready."},
    {"agent":"Phoenix","line":"I got your back."},
    {"agent":"Sage","line":"I've got you."},
    {"agent":"Sova","line":"I will reveal your secrets."},
    {"agent":"Raze","line":"Time to paint the town red!"},
]

AGENTS_BY_NAME = {a["name"].lower(): a for a in AGENTS}

# --- Utilities ---
def fuzzy_match(guess, real, cutoff=0.75):
    import difflib
    g = guess.strip().lower()
    r = real.strip().lower()
    if not g: return False
    if g == r or g in r or r in g: return True
    return len(difflib.get_close_matches(g, [r], n=1, cutoff=cutoff)) > 0

# --- SFX generation (small sine WAVs) ---
def generate_sine_wav(path, freq=440.0, duration=0.18, volume=0.6, samplerate=22050):
    n = int(duration * samplerate)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        for i in range(n):
            sample = volume * math.sin(2 * math.pi * freq * i / samplerate)
            wf.writeframes(struct.pack("<h", int(sample * 32767)))

def ensure_sfx_files():
    files = {
        "correct.wav": (780.0, 0.20),
        "wrong.wav": (180.0, 0.28),
        "hint.wav": (1200.0, 0.12)
    }
    for name,(freq,dur) in files.items():
        path = os.path.join(SFX_DIR, name)
        if not os.path.isfile(path):
            try:
                generate_sine_wav(path, freq=freq, duration=dur)
            except Exception:
                # fallback silence: write an empty file to avoid crashes
                try:
                    open(path, "wb").close()
                except:
                    pass

def play_sound(path):
    if not os.path.isfile(path):
        return
    try:
        sysname = platform.system()
        if sysname == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_FILENAME)
        elif sysname == "Darwin":
            subprocess.Popen(["afplay", path])
        else:
            subprocess.Popen(["aplay", path])
    except Exception:
        pass

ensure_sfx_files()

# --- Tkinter helpers ---
# Use a temporary hidden root for DPI scaling so no popup is shown
try:
    _tmp = tk.Tk(); _tmp.withdraw()
    sc = _tmp.tk.call("tk", "scaling")
    if float(sc) < 1.25:
        _tmp.tk.call("tk", "scaling", 1.25)
    _tmp.destroy()
except Exception:
    pass

# SysPanel and ParticleCanvas
class SysPanel(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=THEME["panel"], bd=1, relief="solid", **kwargs)
        header = tk.Frame(self, bg=THEME["panel"])
        header.pack(fill="x")
        tk.Label(header, text=title, bg=THEME["panel"], fg=THEME["muted"], font=("Consolas",10)).pack(side="left", padx=8, pady=6)
        c = tk.Canvas(header, width=32, height=28, bg=THEME["panel"], highlightthickness=0)
        c.pack(side="right", padx=6)
        c.create_line(6,6,26,6, fill=THEME["corner"], width=2)
        c.create_line(6,6,6,26, fill=THEME["corner"], width=2)

class ParticleCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=THEME["panel"], highlightthickness=0, **kwargs)
        self.particles = [[random.uniform(0,1000), random.uniform(0,800), random.uniform(-0.6,0.6), random.uniform(-0.6,0.6)] for _ in range(26)]
        self.after(80, self._loop)
    def _loop(self):
        try:
            self.delete("p")
            w = self.winfo_width() or 600; h = self.winfo_height() or 400
            for p in self.particles:
                p[0] += p[2]*4; p[1] += p[3]*4
                if p[0] < -40: p[0] = w + 40
                if p[0] > w + 40: p[0] = -40
                if p[1] < -40: p[1] = h + 40
                if p[1] > h + 40: p[1] = -40
                self.create_oval(p[0]-6, p[1]-3, p[0]+6, p[1]+3, fill=THEME["accent"], outline="", tags="p")
        except Exception:
            pass
        self.after(80, self._loop)

# --- Robust splash loader with letterbox scaling ---
def load_letterboxed_photoimage(path, maxsize=(800,600), bgcolor=(11,18,22)):
    """
    Load image from path and return a Tk PhotoImage with letterbox sizing.
    Returns PhotoImage or None.
    """
    try:
        if not PIL_AVAILABLE:
            # fallback tk.PhotoImage (works for PNG/GIF)
            return tk.PhotoImage(file=path)
        img = Image.open(path)
        # ensure RGB (avoid RGBA issues)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            # composite against background to avoid alpha issues
            bg = Image.new("RGBA", img.size, (bgcolor[0],bgcolor[1],bgcolor[2],255))
            bg.paste(img, (0,0), img)
            img = bg.convert("RGB")
        else:
            img = img.convert("RGB")
        # compute letterbox size preserving aspect ratio
        target_w, target_h = maxsize
        iw, ih = img.size
        ratio = min(target_w/iw, target_h/ih)
        new_w, new_h = max(1, int(iw*ratio)), max(1, int(ih*ratio))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # paste onto background to create letterbox
        canvas = Image.new("RGB", (target_w, target_h), bgcolor)
        ox = (target_w - new_w)//2
        oy = (target_h - new_h)//2
        canvas.paste(img, (ox, oy))
        return ImageTk.PhotoImage(canvas)
    except Exception:
        return None

# --- Leaderboard helpers ---
def load_leaderboard():
    try:
        if os.path.isfile(LEADERBOARD_FILE):
            return json.load(open(LEADERBOARD_FILE, "r", encoding="utf-8"))
    except Exception:
        pass
    return []

def save_leaderboard(data):
    try:
        json.dump(data, open(LEADERBOARD_FILE, "w", encoding="utf-8"), indent=2)
    except Exception:
        pass

def add_leaderboard(name, score, mode, diff):
    lb = load_leaderboard()
    lb.append({"name":name,"score":score,"mode":mode,"diff":diff,"ts":time.time()})
    lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:50]
    save_leaderboard(lb)

# --- Main App ---
class AgentGuesserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Guesser")
        self.root.configure(bg=THEME["bg"])
        self.root.geometry("1220x780")
        # state
        self.mode = "Abilities"
        self.diff = "Easy"
        self.score = 0
        self.attempts = 4
        self.current_agent = None
        self.revealed = []
        self.splash_cache = {}  # persistent PhotoImage refs
        # Build UI
        self.build_header()
        self.build_main()
        # Start safe redraw loop
        self.root.after(160, self.safe_redraw_loop)
        # start first round after UI ready
        self.root.after(200, lambda: self.prepare_new_round())

    def build_header(self):
        header = tk.Frame(self.root, bg=THEME["panel"], height=90)
        header.pack(fill="x", padx=12, pady=12)
        left = tk.Frame(header, bg=THEME["panel"]); left.pack(side="left", padx=18)
        tk.Label(left, text="AGENT GUESSER", font=("Bahnschrift",28,"bold"), fg=THEME["accent"], bg=THEME["panel"]).pack(anchor="w")
        tk.Label(left, text="SYSTEM READY", font=("Consolas",10), fg=THEME["muted"], bg=THEME["panel"]).pack(anchor="w")
        right = tk.Frame(header, bg=THEME["panel"]); right.pack(side="right", padx=18)
        tk.Label(right, text="Mode:", bg=THEME["panel"], fg=THEME["muted"]).grid(row=0, column=0, padx=4)
        self.mode_var = tk.StringVar(value=self.mode)
        self.mode_cb = ttk.Combobox(right, values=["Abilities","Voice"], textvariable=self.mode_var, state="readonly", width=12)
        self.mode_cb.grid(row=0, column=1, padx=4)
        self.mode_cb.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())
        tk.Label(right, text="Difficulty:", bg=THEME["panel"], fg=THEME["muted"]).grid(row=1, column=0, padx=4)
        self.diff_var = tk.StringVar(value=self.diff)
        self.diff_cb = ttk.Combobox(right, values=["Easy","Pro","Radiant","Omega"], textvariable=self.diff_var, state="readonly", width=12)
        self.diff_cb.grid(row=1, column=1, padx=4)
        self.diff_cb.bind("<<ComboboxSelected>>", lambda e: self.on_diff_change())

    def build_main(self):
        main = tk.Frame(self.root, bg=THEME["bg"]); main.pack(fill="both", expand=True, padx=12, pady=(0,12))
        # left splash
        self.left_canvas = ParticleCanvas(main); self.left_canvas.pack(side="left", fill="both", expand=True, padx=(0,12), pady=6)
        # right stack panels
        side = tk.Frame(main, bg=THEME["bg"], width=420); side.pack(side="right", fill="y", pady=6)
        self.clue_panel = SysPanel(side, "CLUES"); self.clue_panel.pack(fill="x", padx=8, pady=8)
        self.input_panel = SysPanel(side, "GUESS"); self.input_panel.pack(fill="x", padx=8, pady=8)
        self.score_panel = SysPanel(side, "SCORE"); self.score_panel.pack(fill="x", padx=8, pady=8)
        self.leader_panel = SysPanel(side, "LEADERBOARD"); self.leader_panel.pack(fill="both", expand=True, padx=8, pady=8)
        self.term_panel = SysPanel(side, "TERMINAL"); self.term_panel.pack(fill="x", padx=8, pady=8)

        # clues layout
        self.type_lbl = tk.Label(self.clue_panel, text="Type: —", font=("Consolas",12), fg=THEME["muted"], bg=THEME["panel"]); self.type_lbl.pack(anchor="w", padx=10, pady=2)
        self.gender_lbl = tk.Label(self.clue_panel, text="Gender: —", font=("Consolas",12), fg=THEME["muted"], bg=THEME["panel"]); self.gender_lbl.pack(anchor="w", padx=10, pady=2)
        self.country_lbl = tk.Label(self.clue_panel, text="Country: —", font=("Consolas",12), fg=THEME["muted"], bg=THEME["panel"]); self.country_lbl.pack(anchor="w", padx=10, pady=2)
        self.ability_lbl = tk.Label(self.clue_panel, text="Abilities: —", font=("Consolas",12), fg=THEME["text"], bg=THEME["panel"], wraplength=360, justify="left"); self.ability_lbl.pack(anchor="w", padx=10, pady=6)

        # input
        self.guess_entry = tk.Entry(self.input_panel, font=("Consolas",14), bg="#0B1518", fg=THEME["text"], insertbackground=THEME["text"]); self.guess_entry.pack(fill="x", padx=10, pady=(10,6))
        btnrow = tk.Frame(self.input_panel, bg=THEME["panel"]); btnrow.pack(fill="x", padx=10)
        tk.Button(btnrow, text="Submit Guess", bg=THEME["accent"], fg="#081014", command=self.submit_guess).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(btnrow, text="Hint (-pts)", bg="#1B262A", fg=THEME["text"], command=self.use_hint).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(self.input_panel, text="Skip", bg="#141A1C", fg=THEME["muted"], command=self.skip_agent).pack(fill="x", padx=10, pady=8)
        self.guess_entry.bind("<Return>", lambda e: self.submit_guess())

        # score
        self.score_lbl = tk.Label(self.score_panel, text="0000", font=("Bahnschrift",24,"bold"), fg=THEME["text"], bg=THEME["panel"]); self.score_lbl.pack(anchor="e", padx=10, pady=2)
        self.attempts_lbl = tk.Label(self.score_panel, text="Attempts: 4", font=("Consolas",12), fg=THEME["muted"], bg=THEME["panel"]); self.attempts_lbl.pack(anchor="w", padx=10, pady=2)

        # leaderboard & terminal
        self.lb_text = tk.Text(self.leader_panel, height=8, bg="#081015", fg=THEME["muted"], bd=0); self.lb_text.pack(fill="both", expand=True, padx=10, pady=6)
        self.term_lbl = tk.Label(self.term_panel, text=">_ READY", font=("Consolas",10), fg="#27C6A6", bg=THEME["panel"]); self.term_lbl.pack(anchor="w", padx=10, pady=6)

    # --- Round management ---
    def prepare_new_round(self):
        self.mode = self.mode_var.get() if hasattr(self, "mode_var") else self.mode
        self.diff = self.diff_var.get() if hasattr(self, "diff_var") else self.diff
        if self.mode == "Abilities":
            self.current_agent = random.choice(AGENTS)
            abs_ = self.current_agent["abilities"][:]; random.shuffle(abs_)
            self.revealed = abs_[:2] if self.diff != "Omega" else abs_[:1]
        else:
            v = random.choice(VOICE_LINES)
            self.current_agent = AGENTS_BY_NAME.get(v["agent"].lower(), {"name":v["agent"], "type":"—", "gender":"—", "country":"—", "abilities":[]})
            self.revealed = [v["line"]]
        self.attempts = 4
        self.update_clue_panel()
        self.update_score_panel()

    def update_clue_panel(self):
        a = self.current_agent or {"type":"—","gender":"—","country":"—","abilities":[]}
        self.type_lbl.config(text=f"Type: {a.get('type','—')}")
        self.gender_lbl.config(text=f"Gender: {a.get('gender','—')}")
        self.country_lbl.config(text=f"Country: {a.get('country','—')}")
        if self.mode == "Abilities":
            self.ability_lbl.config(text="Abilities: " + ", ".join(self.revealed))
        else:
            self.ability_lbl.config(text="Voice: " + (self.revealed[0] if self.revealed else "—"))

    def update_score_panel(self):
        self.score_lbl.config(text=str(self.score).zfill(4))
        self.attempts_lbl.config(text=f"Attempts: {self.attempts}")
        self.refresh_leaderboard_view()

    # --- Splash handling (letterbox) ---
    def get_splash_for_agent(self, agent_name, maxsize=(900,700)):
        if not agent_name:
            return None
        key = agent_name.lower().replace(" ", "_")
        candidate = None
        for fn in os.listdir(SPLASH_DIR):
            if key in fn.lower():
                candidate = os.path.join(SPLASH_DIR, fn)
                break
        if not candidate:
            return None
        # Attempt to load robustly
        try:
            return load_letterboxed_photoimage(candidate, maxsize=maxsize)
        except Exception:
            return None

    # --- Safe redraw loop ---
    def safe_redraw_loop(self):
        try:
            self.redraw_left_panel()
        except Exception:
            pass
        self.root.after(200, self.safe_redraw_loop)

    def redraw_left_panel(self):
        c = self.left_canvas
        w = c.winfo_width() or 400; h = c.winfo_height() or 400
        if w < 120 or h < 120: 
            return
        if not self.current_agent:
            return
        name = self.current_agent["name"]
        # cache PhotoImage references persistently
        if name not in self.splash_cache or not self.splash_cache.get(name):
            img = self.get_splash_for_agent(name, maxsize=(w-80, h-200))
            self.splash_cache[name] = img
        img = self.splash_cache.get(name)
        # clear only tags we use so particles remain
        c.delete("splash_img"); c.delete("splash_text")
        if img:
            c.create_image(w//2, h//2 - 20, image=img, tags="splash_img")
            # hold reference on canvas to avoid GC
            c._img_ref = img
        else:
            c.create_text(w//2, h//2 - 20, text=name, font=("Bahnschrift",48,"bold"), fill=THEME["accent"], tags="splash_text")

    # --- Game actions ---
    def submit_guess(self):
        guess = self.guess_entry.get().strip()
        if not guess:
            return
        cutoff = {"Easy":0.68,"Pro":0.78,"Radiant":0.88,"Omega":0.93}.get(self.diff, 0.75)
        real = self.current_agent["name"]
        if fuzzy_match(guess, real, cutoff=cutoff):
            base = {"Easy":80,"Pro":110,"Radiant":150,"Omega":220}.get(self.diff, 80)
            gained = base + (self.attempts - 1) * 10
            self.score += gained
            play_sound(os.path.join(SFX_DIR, "correct.wav"))
            self.term_lbl.config(text=f">_ Correct! It was {real} (+{gained} pts)")
            # auto-save with timestamp name
            try:
                add_leaderboard(f"You_{int(time.time())}", self.score, self.mode, self.diff)
            except Exception:
                pass
            self.prepare_new_round()
            self.guess_entry.delete(0, "end")
        else:
            self.attempts -= 1
            play_sound(os.path.join(SFX_DIR, "wrong.wav"))
            if self.attempts <= 0:
                self.term_lbl.config(text=f">_ Out of attempts. It was {real}")
                self.prepare_new_round()
                self.guess_entry.delete(0, "end")
            else:
                self.term_lbl.config(text=f">_ Wrong. Attempts left: {self.attempts}")
        self.update_score_panel()

    def use_hint(self):
        penalty = {"Easy":10,"Pro":25,"Radiant":40,"Omega":60}.get(self.diff, 25)
        play_sound(os.path.join(SFX_DIR, "hint.wav"))
        if self.mode == "Abilities":
            available = [a for a in self.current_agent["abilities"] if a not in self.revealed]
            if available:
                self.revealed.append(random.choice(available))
                self.score = max(0, self.score - penalty)
                self.update_clue_panel(); self.update_score_panel()
            else:
                self.term_lbl.config(text=">_ No more abilities to reveal.")
        else:
            self.term_lbl.config(text=f">_ Hint: Country = {self.current_agent.get('country','—')}")
            self.score = max(0, self.score - penalty)
            self.update_score_panel()

    def skip_agent(self):
        self.term_lbl.config(text=f">_ Skipped. It was {self.current_agent['name']}")
        self.prepare_new_round()
        self.guess_entry.delete(0, "end")

    def on_mode_change(self):
        self.mode = self.mode_var.get()
        self.prepare_new_round()

    def on_diff_change(self):
        self.diff = self.diff_var.get()
        self.prepare_new_round()

    # --- Leaderboard UI ---
    def refresh_leaderboard_view(self):
        try:
            data = load_leaderboard()
        except Exception:
            data = []
        self.lb_text.config(state="normal"); self.lb_text.delete("1.0", "end")
        for i,e in enumerate(data[:10], start=1):
            ts = time.strftime("%Y-%m-%d", time.localtime(e.get("ts", time.time())))
            self.lb_text.insert("end", f"{i}. {e.get('name')} — {e.get('score')} pts [{e.get('mode')}/{e.get('diff')}] {ts}\n")
        self.lb_text.config(state="disabled")

# --- Run ---
def main():
    root = tk.Tk()
    app = AgentGuesserApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
