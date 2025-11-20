# ⚡ CyberScore Benchmark Suite

*A Cyberpunk × Valorant-styled system performance benchmark built with PyQt5*

**Neon UI • GPU Stress Test • CPU Hashing Benchmark • RAM Bandwidth • Disk R/W • Network Throughput • Multi-threaded • Glitch FX • Futuristic HUD • Single-file Application**

---

## 🚀 Overview

**CyberScore** is a fully animated, neon-themed benchmark tool designed to test:

* **CPU performance** (parallel SHA-256 hashing)
* **GPU performance** (OpenGL or painter fallback renderer)
* **RAM bandwidth** (NumPy or Python fallback)
* **Disk speed** (read/write temporary file)
* **Network throughput** (multiple download iterations)

Everything is packaged into a **single Python file** with a modern UI, glowing progress bars, glitch effects, animations, and a fully animated final score reveal.

---

## ✨ Key Features

### 🔥 1. Multi-Threaded CPU Benchmark

* Parallel SHA-256 hashing loops
* Real-time progress updates
* Measures total hashes, time taken & hashes/sec

### 🎨 2. GPU Benchmark (Automatic Mode Detection)

* **If `PyOpenGL` is available:** runs a high-intensity triangle renderer via `QOpenGLWidget`.
* **Fallback:** painter-based animation with rotating ellipses & stress loops.
* Measures:

  * Real-time FPS
  * Average FPS over the test window

### 💾 3. RAM Benchmark

Two modes depending on installed packages:

| Mode              | Description                                                                |
| ----------------- | -------------------------------------------------------------------------- |
| **numpy-enabled** | Allocates and writes large `float32` arrays for realistic memory bandwidth |
| **fallback**      | Python list fill + read passes                                             |

Measures:

* Read + write throughput (MB/s)
* Total elapsed time

### 📀 4. Disk Benchmark

* Writes configurable MB of random data
* Reads it back
* Computes read/write MB/s
* Cleans up temporary files automatically

### 🌐 5. Network Benchmark

* Repeated GET requests via `urllib`
* Measures:

  * Latency
  * Throughput
  * Total MB downloaded

**Default test file:** `http://ipv4.download.thinkbroadband.com/5MB.zip`

### 🧩 Dynamic Neon UI

* Glowing neon buttons
* Gradient progress bars
* Glitched text effects
* Animated GPU panel
* Big score reveal animation
  All styling is provided via an inline Qt stylesheet in the single file.

---

## 📊 Final “CyberScore” Calculation

After all benchmarks complete, results are transformed into a **0–1000 score** based on weighted contributions.

| Test              | Metric        | Contribution            |
| ----------------- | ------------- | ----------------------- |
| CPU               | Hashes/sec    | Up to **250 points**    |
| GPU               | Avg FPS       | Up to **250 points**    |
| RAM               | MB/s          | Up to **250 points**    |
| Disk              | (R+W)/2 MB/s  | Up to **250 points**    |
| Network           | Download MB/s | Up to **250 points**    |
| **Total Raw Max** | 1250          | Normalized → **0–1000** |

**Ranks**

* **900+** → *Masterclass – System Dominator*
* **750+** → *Legend – Elite Performance*
* **500+** → *Pro – Strong*
* **250+** → *Competent – Average*
* **Below 250** → *Starter – Needs Upgrade*

---

## 📁 Project Structure

```
CyberScore/
├── cyberscore_benchmark.py   # The entire application (single file)
└── README.md                 # This file
```

No additional assets required.

---

## 🔧 Requirements

### Python

* Python **3.7+**

### Dependencies

Install the minimum required dependency:

```bash
pip install PyQt5
```

Optional (improves GPU & RAM tests):

```bash
pip install PyOpenGL numpy
```

---

## ▶️ Running the Benchmark

```bash
python cyberscore_benchmark.py
```

The app launches a neon-styled UI with:

* **START Benchmark** / **ABORT**
* CPU/GPU/RAM/Disk/Network progress bars
* Live log window
* GPU render preview window (if available)
* Results + animated score reveal

---

## 🖥️ Screens & UI Features

* Neon glowing panels
* Magenta/cyan cyberpunk palette
* Animated GPU preview widget or painter fallback
* Flickering “glitch” effects on headers and metrics
* Smooth gradient “energy bar” progress bars
* Final score reveal with pulsing neon animation

---

## 🧱 Architecture

All logic is contained in one file and is organized into:

* `BenchmarkThread` base class
* Subclasses: `CpuBenchmarkThread`, `RamBenchmarkThread`, `DiskBenchmarkThread`, `NetworkBenchmarkThread`, etc.
* `CyberScoreApp` main window
* OpenGL (`QOpenGLWidget`) or painter-based renderer fallback
* PyQt5 signals for thread → UI communication

---

## 🛡️ Notes & Safety

* Temporary files are removed after the Disk test
* Network test handles timeouts and errors gracefully
* GPU test runs safely and falls back if necessary
* Benchmarks can be aborted mid-run

---

## 📜 License

Free to use, modify, and redistribute.

---

