# ⚡ CyberScore Benchmark Suite
**A Cyberpunk × Valorant-styled system performance benchmark built with PyQt5**

Neon UI • GPU Stress Test • CPU Hashing Benchmark • RAM Bandwidth • Disk R/W • Network Throughput  
Multi-threaded • Glitch FX • Futuristic HUD • Single-file, self-contained application

---

## 🚀 Overview

**CyberScore** is a fully-animated, neon-themed benchmark tool designed to test and visualize system performance:

- **CPU performance** — parallel SHA256 hashing
- **GPU performance** — QOpenGLWidget renderer with a Painter fallback
- **RAM bandwidth** — numpy-enabled or Python fallback
- **Disk speed** — write/read temporary file
- **Network throughput** — repeated download iterations

Everything is packaged into **one Python file** with a Valorant-inspired UI: glowing progress bars, glitch effects, animated GPU preview, and a dramatic final score reveal.

---

## ✨ Key Features

### 🔥 Multi-Threaded CPU Benchmark
- Parallel SHA256 hashing loops
- Real-time progress updates
- Reports total hashes, elapsed time, and hashes/sec

### 🎨 GPU Benchmark (automatic mode detection)
- **If PyOpenGL is available**: runs a high-intensity triangle renderer using `QOpenGLWidget`
- **If PyOpenGL is not available**: falls back to a Painter-based animation (rotating shapes + stress loops)
- Both modes measure real-time FPS and average FPS over the test window

### 🧠 RAM Benchmark
- **numpy-enabled mode**: allocates and writes large `float32` arrays for realistic memory bandwidth
- **Fallback mode**: Python list fill + read passes
- Measures read+write throughput (MB/s) and elapsed time

### 💾 Disk Benchmark
- Writes configured MB of random data to a temporary file
- Reads it back
- Computes write/read MB/s and cleans up the temp file automatically

### 🌐 Network Benchmark
- Repeated `GET` requests (via `urllib`) to measure:
  - Latency
  - Throughput (MB/s)
  - Total MB downloaded
- Default test file: `http://ipv4.download.thinkbroadband.com/5MB.zip`
  - (Configurable in-app)

### 🧩 Dynamic Neon UI
- Inline Qt stylesheet for neon look (magenta / cyan palette)
- Glowing buttons and gradient progress bars
- Glitched text effects and animated GPU preview
- Smooth real-time logs and a pulsing final score reveal

---

## 📊 Final “CyberScore”

Results are combined and normalized to a **0–1000 score**:

| Test    | Metric        | Contribution |
|---------|---------------|--------------|
| CPU     | Hashes/sec    | Up to 250 pts |
| GPU     | Avg FPS       | Up to 250 pts |
| RAM     | MB/s          | Up to 250 pts |
| Disk    | (R+W)/2 MB/s  | Up to 250 pts |
| Network | Download MB/s | Up to 250 pts |
| **Raw Max** |           | 1250 → normalized to 0–1000 |

**Ranks**
- **900+** → Masterclass — *System Dominator*  
- **750+** → Legend — *Elite Performance*  
- **500+** → Pro — *Strong*  
- **250+** → Competent — *Average*  
- **Below 250** → Starter — *Needs Upgrade*

---

## 🧱 Architecture (single-file)

Implemented with a clean, modular structure inside one Python file:

- `BenchmarkThread` base class (signals, progress, abort)
- Specialized threads:
  - `CpuBenchmarkThread`
  - `GpuBenchmarkThread` (and fallback renderer)
  - `RamBenchmarkThread`
  - `DiskBenchmarkThread`
  - `NetworkBenchmarkThread`
- `CyberScoreApp` — main `QMainWindow` with all UI panels
- QOpenGLWidget when available, painter fallback otherwise
- PyQt5 signals for thread → UI communication

---

## 🔧 Requirements

### Python
- Python **3.7+**

### Python packages
Install the minimum dependency:
```bash
pip install PyQt5
