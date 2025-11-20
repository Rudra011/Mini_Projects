<div align="center">

# ⚡ **CyberScore Benchmark Suite**

### *A Cyberpunk × Valorant-styled System Performance Benchmark built with PyQt5*

Neon UI • GPU Stress Test • CPU Hashing Benchmark • RAM Bandwidth • Disk R/W • Network Throughput  
Multi-threaded • Glitch FX • Futuristic HUD • Single-file Self-contained Application

</div>

---

## 🚀 Overview

**CyberScore** is a fully animated, neon-themed benchmark tool designed to test:

- **CPU performance** (parallel SHA256 hashing)  
- **GPU performance** (OpenGL or Painter fallback renderer)  
- **RAM bandwidth** (NumPy or Python fallback)  
- **Disk speed** (read/write temporary file)  
- **Network throughput** (multiple download iterations)

Everything is packaged into a **single Python file** with a modern **Valorant-inspired UI**, glowing progress bars, glitch effects, animations, and a fully animated final score reveal.

---

## ✨ Key Features

### 🔥 **1. Multi-Threaded CPU Benchmark**
- Parallel SHA256 hashing loops  
- Real-time progress updates  
- Measures total hashes, time taken & hashes/sec  

---

### 🎨 **2. GPU Benchmark (Automatic Mode Detection)**

#### **If PyOpenGL available →**
Runs a high-intensity triangle renderer via **QOpenGLWidget**.

#### **If not available →**
Uses a custom **Painter-based animation** with rotating ellipses & stress loops.

Both modes measure:
- Real-time FPS  
- Average FPS over the test window  

---

### 💾 **3. RAM Benchmark**

Two modes depending on installed packages:

| Mode              | Description                                                     |
|-------------------|-----------------------------------------------------------------|
| **numpy-enabled** | Allocates and writes large float32 arrays for real memory tests |
| **fallback**      | Python list fill + read passes                                  |

Measures:
- Read + Write throughput (MB/s)  
- Total elapsed time  

---

### 📀 **4. Disk Benchmark**
- Writes configurable MB of random data  
- Reads it back  
- Computes read/write MB/s  
- Cleans up automatically  

---

### 🌐 **5. Network Benchmark**
- Repeated GET requests via `urllib`  
- Measures:
  - Latency  
  - Throughput  
  - Total MB downloaded  

Default test file:  
`http://ipv4.download.thinkbroadband.com/5MB.zip`

---

### 🧩 **Dynamic Neon UI**

Custom PyQt5 styling:

- Glowing neon buttons  
- Gradient progress bars  
- Glitched text effects  
- Animated GPU panel  
- Valorant-style big-score reveal  

Everything styled via **inline Qt Stylesheet** in the same file.

---

## 📊 Final “CyberScore”

After all benchmarks complete, results are transformed into a **0–1000 score**, based on:

| Test     | Metric          | Contribution          |
|----------|------------------|------------------------|
| CPU      | Hashes/sec       | Up to **250 points**   |
| GPU      | Avg FPS          | Up to **250 points**   |
| RAM      | MB/s             | Up to **250 points**   |
| Disk     | (R+W)/2 MB/s     | Up to **250 points**   |
| Network  | Download MB/s    | Up to **250 points**   |
| **Total Raw Max** | 1250 | Normalized → **0–1000** |

Ranks:

- **900+** → *Masterclass – System Dominator*  
- **750+** → *Legend – Elite Performance*  
- **500+** → *Pro – Strong*  
- **250+** → *Competent – Average*  
- **Below 250** → *Starter – Needs Upgrade*  

---

## 📁 Project Structure

