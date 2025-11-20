<div align="center">

# 🔍 **AGENT GUESSER — Rebuilt v2**

### *A high-polish SYS-themed guessing game with abilities, voice lines, leaderboards & dynamic splashes.*

A modern, fully reengineered Valorant-inspired agent guessing game built in
**Python + Tkinter + PIL**, featuring dynamic letterboxed splash art, fuzzy name matching,
combobox-driven modes, generated SFX, particle animations, and a persistent leaderboard.

</div>

---

## 🧩 **Overview**

**Agent Guesser v2** is a feature-rich game where the player must guess the Valorant agent
based on provided clues. The clues depend on the mode:

* **Abilities Mode:** Guess using randomized agent abilities
* **Voice Mode:** Guess using one of the agent's voice lines

Difficulty affects clue reveal count, fuzzy matching strictness, and scoring multipliers.

Alongside gameplay, the rebuild introduces cleaner UI, safer redraw logic, letterbox image scaling, SFX generation, leaderboards, and an SYS-inspired user interface.

---

## 🎮 **Key Features**

### 🖼️ **Letterboxed Splash Loader (No Cropping)**

* Automatically detects agent splash images in `./assets/splashes/`
* Resizes and centers images with black bars (letterboxing)
* Converts RGBA → RGB safely to avoid Tkinter alpha crashes
* Persistent image caching for smooth redraw

---

### 🔊 **Generated Sound Effects**

No bulky audio included — the game *generates WAV files on first run*:

* `correct.wav`
* `wrong.wav`
* `hint.wav`

All created using math-based sine wave synthesis.

---

### 🌀 **Particle Background System**

The left panel includes a dynamic looping particle effect using canvas animation.
Lightweight, stylized, and perfectly matches the SYS theme.

---

### 💬 **Clue Panels Based on Mode**

#### **Abilities Mode**

Shows:

* Type
* Gender
* Country
* 1–2 abilities (based on difficulty)

#### **Voice Mode**

Shows:

* A random voice line
* Optional hint revealing country

---

### 🧠 **Smart Guess Detection**

Fuzzy name recognition:

* Typo-tolerant
* Difficulty-scaled thresholds
* Includes exact match, partial match, and similarity match

---

### 🏆 **Leaderboard System**

* Stores top 50 runs
* Saves automatically on every correct guess
* Displayed in real-time
* Stored locally at `leaderboard.json`

---

### ⚙️ **SYS-Themed Interface**

Clean, modern UI featuring:

* Modular panels
* Accent borders
* Terminal readout
* Combobox difficulty selector
* Responsive layout
* Safe redraw loop (prevents Tk glitches)

---

## 📁 **Project Structure**

```
AgentGuesser/
│
├── agent_guesser_rebuilt_v2.py   # Main application
├── leaderboard.json              # Auto-generated
│
└── assets/
    ├── splashes/                 # Agent splash images (user-provided)
    └── sfx/
        ├── correct.wav           # Generated at runtime
        ├── wrong.wav
        └── hint.wav
```

---

## 🚀 **How to Run**

### 1. Install Dependencies

```bash
pip install pillow
```

### 2. Run the Game

```bash
python agent_guesser_rebuilt_v2.py
```

---

## 🎮 **Gameplay Flow**

Select Mode → Select Difficulty → Clues Appear → Enter Guess → Score → New Round

---

## 🎚️ **Difficulties**

| Difficulty | Fuzzy Match Strictness | Ability Reveals | Score Multiplier |
| ---------- | ---------------------- | --------------- | ---------------- |
| Easy       | Low                    | 2 abilities     | Medium           |
| Pro        | Medium                 | 2 abilities     | High             |
| Radiant    | High                   | 2 abilities     | Very High        |
| Omega      | Very High              | 1 ability       | Extreme          |

---

## 🔧 **Tech Used**

* Python 3.x
* Tkinter (GUI)
* Pillow (optional splash processing)
* Wave + Math (SFX generation)
* JSON (leaderboard)
* difflib (fuzzy match)
* OOP-structured GUI architecture

---

## ✨ **Highlights of the Rebuild**

✔️ No more scaling bugs
✔️ No Tk popups or DPI issues
✔️ No weird alpha crashes
✔️ Fast & safe redrawing
✔️ Clean architecture
✔️ Much more aesthetic UI

<div align="center">


</div>
