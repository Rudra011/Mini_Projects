import pytesseract
from PIL import Image
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path

# Uncomment and modify the path below if on Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced OCR - Batch Text Extractor")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        self.image_queue = []
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 Advanced OCR Text Extractor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Add buttons
        self.add_files_btn = ttk.Button(button_frame, text="📁 Add Images", 
                                        command=self.add_files, width=15)
        self.add_files_btn.grid(row=0, column=0, padx=5)
        
        self.clear_queue_btn = ttk.Button(button_frame, text="🗑️ Clear Queue", 
                                          command=self.clear_queue, width=15)
        self.clear_queue_btn.grid(row=0, column=1, padx=5)
        
        self.process_btn = ttk.Button(button_frame, text="▶️ Process All", 
                                      command=self.start_processing, width=15)
        self.process_btn.grid(row=0, column=2, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save Results", 
                                   command=self.save_results, width=15)
        self.save_btn.grid(row=0, column=3, padx=5)
        
        # Language selection
        lang_frame = ttk.Frame(button_frame)
        lang_frame.grid(row=0, column=4, padx=20)
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value="eng")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                  values=["eng", "spa", "fra", "deu", "chi_sim", "ara", "hin"], 
                                  width=10, state="readonly")
        lang_combo.pack(side=tk.LEFT)
        
        # Preprocessing option
        self.preprocess_var = tk.BooleanVar(value=True)
        preprocess_check = ttk.Checkbutton(button_frame, text="Enhanced Processing", 
                                          variable=self.preprocess_var)
        preprocess_check.grid(row=0, column=5, padx=10)
        
        # Content frame with two panes
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)
        
        # Left pane - Queue
        queue_frame = ttk.LabelFrame(content_frame, text="Image Queue", padding="5")
        queue_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        
        # Queue listbox with scrollbar
        queue_scroll = ttk.Scrollbar(queue_frame)
        queue_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.queue_listbox = tk.Listbox(queue_frame, yscrollcommand=queue_scroll.set, 
                                        height=15, font=("Courier", 9))
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        queue_scroll.config(command=self.queue_listbox.yview)
        
        self.queue_count_label = ttk.Label(queue_frame, text="Queue: 0 images")
        self.queue_count_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Right pane - Results
        results_frame = ttk.LabelFrame(content_frame, text="Extracted Text", padding="5")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                      font=("Arial", 10), height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.tiff *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            for file in files:
                if file not in self.image_queue:
                    self.image_queue.append(file)
                    self.queue_listbox.insert(tk.END, os.path.basename(file))
            
            self.update_queue_count()
            self.status_var.set(f"Added {len(files)} image(s) to queue")
    
    def clear_queue(self):
        self.image_queue.clear()
        self.queue_listbox.delete(0, tk.END)
        self.update_queue_count()
        self.status_var.set("Queue cleared")
    
    def update_queue_count(self):
        count = len(self.image_queue)
        self.queue_count_label.config(text=f"Queue: {count} image(s)")
    
    def preprocess_image(self, image_path):
        """Advanced preprocessing for better OCR accuracy"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(denoised)
        thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return morph
    
    def extract_text(self, image_path):
        """Extract text from image"""
        try:
            if self.preprocess_var.get():
                preprocessed = self.preprocess_image(image_path)
                pil_image = Image.fromarray(preprocessed)
            else:
                pil_image = Image.open(image_path)
            
            lang = self.language_var.get()
            custom_config = f'--oem 3 --psm 3 -l {lang}'
            
            text = pytesseract.image_to_string(pil_image, config=custom_config)
            return text
        
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def process_images(self):
        """Process all images in queue"""
        self.processing = True
        self.results_text.delete(1.0, tk.END)
        
        total = len(self.image_queue)
        self.progress['maximum'] = total
        
        all_results = []
        
        for i, image_path in enumerate(self.image_queue):
            filename = os.path.basename(image_path)
            self.status_var.set(f"Processing {i+1}/{total}: {filename}")
            self.progress['value'] = i + 1
            self.root.update_idletasks()
            
            # Extract text
            text = self.extract_text(image_path)
            
            # Format results
            result = f"\n{'='*80}\n"
            result += f"FILE: {filename}\n"
            result += f"{'='*80}\n"
            result += text
            result += f"\n{'='*80}\n"
            
            all_results.append(result)
            
            # Update display
            self.results_text.insert(tk.END, result)
            self.results_text.see(tk.END)
            
            # Highlight processed item in queue
            self.queue_listbox.itemconfig(i, {'bg': 'light green'})
        
        self.processing = False
        self.status_var.set(f"Complete! Processed {total} image(s)")
        messagebox.showinfo("Complete", f"Successfully processed {total} image(s)!")
    
    def start_processing(self):
        """Start processing in a separate thread"""
        if not self.image_queue:
            messagebox.showwarning("No Images", "Please add images to the queue first!")
            return
        
        if self.processing:
            messagebox.showwarning("Processing", "Already processing images!")
            return
        
        # Disable buttons during processing
        self.add_files_btn.config(state='disabled')
        self.process_btn.config(state='disabled')
        self.clear_queue_btn.config(state='disabled')
        
        # Start processing thread
        thread = threading.Thread(target=self.process_with_cleanup)
        thread.daemon = True
        thread.start()
    
    def process_with_cleanup(self):
        """Process and re-enable buttons"""
        try:
            self.process_images()
        finally:
            self.add_files_btn.config(state='normal')
            self.process_btn.config(state='normal')
            self.clear_queue_btn.config(state='normal')
    
    def save_results(self):
        """Save extracted text to file"""
        content = self.results_text.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showwarning("No Results", "No text to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Results"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Results saved to:\n{file_path}")
                self.status_var.set(f"Results saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

def main():
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()