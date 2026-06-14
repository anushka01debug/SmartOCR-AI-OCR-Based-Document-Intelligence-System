# 📄 SmartOCR AI – Document Intelligence System

SmartOCR AI is an OCR-powered document intelligence platform built using Python, Streamlit, OpenCV, Tesseract OCR, and SQLite. The system automates text extraction, document classification, metadata extraction, analytics, and batch document processing for images and PDF documents.

## 🚀 Features

* OCR text extraction from Images and PDFs
* Intelligent document classification
* Metadata extraction for different document types
* Image preprocessing pipeline
* Batch document processing
* Analytics Dashboard
* SQLite database integration
* Export extracted data as TXT, JSON, and CSV
* Configurable OCR and classification settings

## 🛠️ Technologies Used

* Python
* Streamlit
* Tesseract OCR
* OpenCV
* PyMuPDF
* SQLite
* Pandas
* Matplotlib
* Pillow

---

## 📸 Project Screenshots

### SmartOCR Workspace

![Smart OCR Workspace](images/Smart%20OCR%20page.png)

### Upload & Analysis

![Upload and Analysis](images/Upload%20and%20analysis.png)

### Field Extraction

![Field Extraction](images/Field%20extraction.png)

### Saving Results to Database

![Saving to Database](images/Saving%20to%20database.png)

### Download Extracted Text

![Download Raw Text](images/Download%20Raw%20Text.png)

### Analytics Dashboard

![Analytics Dashboard](images/Analytics%20Dashboard.png)

### Batch Processing

![Batch Processing](images/Batch%20processing.png)

---

## 📂 Project Structure

```text
SmartOCR-AI/
│
├── app.py
├── classifier.py
├── database.py
├── extractor.py
├── image_processor.py
├── ocr_engine.py
├── ui_helpers.py
├── requirements.txt
├── settings.json
├── config.toml
│
├── images/
│   ├── Smart OCR page.png
│   ├── Upload and analysis.png
│   ├── Field extraction.png
│   ├── Saving to database.png
│   ├── Download Raw Text.png
│   ├── Analytics Dashboard.png
│   └── Batch processing.png
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/smartocr-ai.git
cd smartocr-ai
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Tesseract OCR

Download and install Tesseract OCR:

https://github.com/tesseract-ocr/tesseract

### Run Application

```bash
streamlit run app.py
```

---

## 📊 Supported Document Types

* Invoice
* Receipt
* Certificate
* Question Paper
* Notes

---

## 🎯 Future Enhancements

* AI-powered document extraction
* LLM-based document understanding
* Semantic search
* Multi-language OCR
* Cloud deployment
* Document chat assistant

---

## 👨‍💻 Author

Developed by Anushka Bakshi 
as an OCR and Document Intelligence project using Python, Computer Vision, and OCR technologies.
