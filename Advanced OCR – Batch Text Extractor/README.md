<div align="center">

# 📄 **Advanced OCR – Batch Text Extractor**
### A powerful multi-image OCR tool with preprocessing, language selection, and batch processing.

A desktop application built with **Python, Tkinter, Tesseract OCR, OpenCV, and PIL**  
designed to extract text from **multiple images at once** with high accuracy.

</div>

---

## ✨ **Overview**

This application allows you to load multiple images, preprocess them with OpenCV,  
extract readable text using Tesseract OCR, and save the results—all inside a clean,  
responsive Tkinter GUI.

Perfect for:

- Converting scanned documents  
- Extracting text from screenshots  
- OCR automation tasks  
- Translating text from images  
- Batch document processing  

---

## 🚀 **Key Features**

### 📁 **Batch Processing**
- Add multiple images at once  
- Displays all queued images  
- Processes each image sequentially with a progress bar

---

### 🧠 **Advanced Preprocessing Mode**
Uses computer vision enhancements to dramatically improve OCR accuracy:
- Noise reduction  
- CLAHE contrast enhancement  
- Adaptive thresholding  
- Morphological closing  

Toggleable with **Enhanced Processing** checkbox.

---

### 🌐 **Multi-Language OCR Support**
Choose between:

| Language Code | Language |
|---------------|----------|
| `eng` | English |
| `spa` | Spanish |
| `fra` | French |
| `deu` | German |
| `chi_sim` | Chinese (Simplified) |
| `ara` | Arabic |
| `hin` | Hindi |

Requires corresponding Tesseract language packs installed.

---

### 💬 **Real-Time Results View**
A built-in scrollable text window outputs the extracted content as each image is processed.

---

### 💾 **Save Output**
Export all extracted text to a `.txt` file with one click.

---

### ⚡ **Threaded Processing**
- UI stays responsive while processing heavy images  
- Background threads handle long-running tasks  

---

## 🛠️ **Tech Stack**

- **Python 3.x**  
- **Tkinter** for GUI  
- **Tesseract OCR (pytesseract)**  
- **OpenCV (cv2)** for preprocessing  
- **Pillow (PIL)** for image handling  
- **Threading** for non-blocking operations  

---

## 📁 **Project Structure**

Advanced-OCR/
│
├── ocr_app.py # Main application
├── requirements.txt # Dependency list (optional)
├── README.md # This file
└── extracted/ # (Optional) Saved text output

yaml
Copy code

---

## ⚙️ **Installation**

### 1. Install Tesseract OCR

#### **Windows**
Download and install:
https://github.com/UB-Mannheim/tesseract/wiki

Then update this line in the script if needed:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
Mac
bash
Copy code
brew install tesseract
Linux
bash
Copy code
sudo apt install tesseract-ocr
2. Install Python Dependencies
bash
Copy code
pip install pytesseract opencv-python pillow
▶️ Running the Program
bash
Copy code
python ocr_app.py
The GUI will launch with:

Image Queue (Left)

Extracted Text Viewer (Right)

Buttons for Add, Clear, Process, Save

Language selector

Enhanced Processing toggle

🖼️ Using the Application
1. Add Images
Click 📁 Add Images → choose one or more images.

Accepted formats:
.png, .jpg, .jpeg, .bmp, .gif, .tiff

2. Choose Language
Use the dropdown to select the OCR language.

3. (Optional) Enable Enhanced Processing
Improves OCR accuracy but may increase processing time.

4. Process Images
Click ▶️ Process All to begin extraction.

The results appear live in the text viewer.

5. Save Results
Click 💾 Save Results to export all extracted text.

🧪 OCR Preprocessing Pipeline
If Enhanced Processing is ON:

objectivec
Copy code
Image
 ↓
Grayscale
 ↓
Denoising (fastNlMeans)
 ↓
CLAHE contrast boost
 ↓
Adaptive Gaussian thresholding
 ↓
Morphological closing
 ↓
Tesseract OCR
Provides significantly cleaner text extraction for:

Low-quality scans

Shadowed documents

Screenshots

Text with noise

❗ Troubleshooting
❓ Tesseract Not Found
Ensure the correct path is set:

python
Copy code
pytesseract.pytesseract.tesseract_cmd = r"..."
❓ Arabic/Chinese/Hindi Not Working
Install corresponding Tesseract language packs.

❓ Poor Accuracy
Enable Enhanced Processing.

📜 License
This project is free to use and modify.

<div align="center">
💡 Need a better UI theme, custom icon set, or installer version?
Just ask — I can generate it.

</div> ```