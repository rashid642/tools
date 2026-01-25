# 🛠️ Tool Studio - Tools Directory

This directory contains all the individual tools available on Tool Studio. Each tool is a standalone application with its own frontend HTML and backend (if needed).

## 📋 Available Tools

### 1. 📖 README Viewer
![README Viewer](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Readme+viwer.png)

**URL:** https://toolstudio.in/tools/1/readme-viewer  
**Description:** A beautiful markdown viewer with live preview and syntax highlighting. Perfect for viewing and editing README files with real-time rendering.

**Features:**
- Live markdown preview
- Syntax highlighting for code blocks
- Dark & Light themes
- Export as HTML
- Auto-save to local storage

---

### 2. 📷 Camera Test
![Camera Test](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Camera+test.png)

**URL:** https://toolstudio.in/tools/2/camera-test  
**Description:** Test your device camera, capture photos with live preview, and download images instantly. Perfect for testing camera functionality.

**Features:**
- Live camera preview
- Switch between front/back cameras
- Capture and download photos
- Resolution info
- Works on mobile and desktop

---

### 3. 📄 PDF Page Remover
![PDF Page Remover](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/PDF+Page+remover.png)

**URL:** https://toolstudio.in/tools/3/pdf-page-remover  
**Description:** Remove specific pages from PDF files easily. Enter page numbers or ranges, and download the modified PDF instantly.

**Features:**
- Drag & drop PDF upload
- Flexible page selection (ranges, single pages)
- Instant processing
- Auto-download modified PDF
- Privacy-first (files not stored)

---

### 4. 🎤 Microphone & Speaker Test
![Microphone & Speaker Test](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Microphone+and+speaker+test.png)

**URL:** https://toolstudio.in/tools/4/microphone-speaker-test  
**Description:** Complete audio testing tool - test your microphone with live waveform visualization and test left/right speakers.

**Features:**
- Live waveform visualization
- Audio recording and playback
- Stereo channel control (L/R/Both)
- Input level monitoring
- Download recordings

---

### 5. ✨ JSON Formatter
![JSON Formatter](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/JSON+Formatter.png)

**URL:** https://toolstudio.in/tools/5/json-formatter  
**Description:** Format, validate, and beautify JSON data instantly. Minify JSON, fix formatting errors, and validate JSON syntax online.

**Features:**
- Format & beautify JSON
- Minify JSON
- Syntax validation
- Custom indentation (1-8 spaces)
- Copy & download options
- Real-time statistics

---

### 6. ✂️ PDF Splitter
![PDF Splitter](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/PDF+Splitter.png)

**URL:** https://toolstudio.in/tools/6/pdf-splitter  
**Description:** Split PDF files into multiple documents by custom page ranges. Create named splits, validate page ranges, and handle leftover pages.

**Features:**
- Upload single PDF
- Create multiple splits with custom ranges
- Custom naming for each split
- Page validation
- Unused pages detection
- Batch download as ZIP

---

### 7. 📷 QR Code Scanner
![QR Code Scanner](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/QR+Codescanner.png)

**URL:** https://toolstudio.in/tools/7/qr-code-scanner  
**Description:** Scan and decode QR codes from images or camera instantly. Extract URLs, text, contact info, WiFi credentials, and more.

**Features:**
- Image upload (drag & drop)
- Live camera scanning
- Front/back camera toggle
- Decode multiple QR codes
- Copy decoded data
- Open links directly

---

### 8. 🔍 Multi-Search Text Highlighter
![Multi-Search Text Highlighter](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Multi+search.png)

**URL:** https://toolstudio.in/tools/8/multi-search-text-highlighter  
**Description:** Search up to 5 words simultaneously with color-coded highlighting, occurrence counters, and easy navigation.

**Features:**
- Search up to 5 terms simultaneously
- Color-coded highlighting for each term
- Occurrence counter for each search
- Navigate between matches
- Case sensitive & whole word options
- 50,000 character limit

---

### 9. 📊 Text Diff Comparison
![Text Diff Comparison](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Compare+text.png)

**URL:** https://toolstudio.in/tools/9/text-diff-comparison  
**Description:** Compare two texts side-by-side with color-coded highlighting for additions, deletions, and modifications.

**Features:**
- Side-by-side comparison
- Line-by-line, word-level, and character-level modes
- Color-coded differences (additions, deletions, modifications)
- Synchronized scrolling
- Case sensitive & ignore whitespace options
- Live statistics

---

### 10. 📑 PDF Merger
![PDF Merger](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Merge+PDF.png)

**URL:** https://toolstudio.in/tools/10/pdf-merger  
**Description:** Combine multiple PDF files into a single document. Upload PDFs, reorder them with drag & drop, and merge instantly.

**Features:**
- Upload multiple PDFs
- Drag & drop reordering
- File preview with page count
- Remove files before merging
- Instant merge and download
- Privacy-first processing

---

### 11. 📝 Text Utilities
![Text Utilities](https://tool-studio.s3.ap-south-1.amazonaws.com/public/tool-images/Text+util.png)

**URL:** https://toolstudio.in/tools/11/text-utilities  
**Description:** Comprehensive text processing tool to count characters, words, lines, and more. Convert text case, find & replace, remove extra spaces.

**Features:**
- Real-time statistics (characters, words, lines, sentences, paragraphs, reading time)
- Case transformations (UPPERCASE, lowercase, Title Case, Sentence case)
- Text manipulation (reverse, remove spaces, remove line breaks)
- Find & Replace with case sensitivity
- Find & Highlight with visual highlighting
- Copy to clipboard
- Dark mode support

---

## 🏗️ Directory Structure

```
tools/
├── 1__README_Viewer/
│   └── index.html
├── 2__Camera_Test/
│   └── index.html
├── 3__PDF_Page_Remover/
│   ├── index.html
│   ├── main.py
│   └── requirements.txt
├── 4__Audio_Test/
│   └── index.html
├── 5__JSON_Formatter/
│   └── index.html
├── 6__PDF_Splitter/
│   ├── index.html
│   ├── main.py
│   └── requirements.txt
├── 7__QR_Code_Scanner/
│   ├── index.html
│   ├── main.py
│   └── requirements.txt
├── 8__Multi_Search/
│   └── index.html
├── 9__Text_Diff/
│   └── index.html
├── 10__PDF_Merger/
│   ├── index.html
│   ├── main.py
│   └── requirements.txt
├── 11__Text_Utilities/
│   └── index.html
└── README.md (this file)
```

## 🔧 Tool Types

### Client-Side Only Tools
These tools run entirely in the browser with no backend processing:
- README Viewer
- Camera Test
- Audio Test
- JSON Formatter
- Multi-Search Text Highlighter
- Text Diff Comparison
- Text Utilities

### Tools with Python Backend
These tools require server-side processing for PDF/image manipulation:
- PDF Page Remover (PyPDF2)
- PDF Splitter (PyPDF2)
- QR Code Scanner (opencv-python-headless, Pillow)
- PDF Merger (PyPDF2)

## 🚀 Development

Each tool is designed to be:
- **Standalone**: Can function independently
- **SEO-Friendly**: Proper meta tags, Open Graph, JSON-LD
- **Responsive**: Works on mobile and desktop
- **Privacy-First**: Client-side processing when possible
- **Modern UI**: Clean, intuitive interface with dark mode

## 📝 License

All tools are part of the Tool Studio project.

---

**Tool Studio** - Your one-stop solution for everyday tools!  
🌐 Visit: https://toolstudio.in
