# Adobe India Hackathon 2025 - Round 1A: PDF Structure Extractor

## 🚀 Challenge Theme: Connecting the Dots Through Docs

This project extracts a **structured outline** from a given PDF document, including:

- **Document Title**
- **Headings** categorized into **H1**, **H2**, and **H3**
- **Page numbers** associated with each heading

The extracted information is output in a clean JSON format and serves as the foundation for further intelligent document analysis.

---

## 📁 Directory Structure

├── input/            # Input folder containing PDF files (e.g., sample.pdf)
├── output_jsons/     # Output folder with corresponding structured JSONs
├── Dockerfile        # Container setup for offline execution
├── process_pdf.py    # Main script for processing PDFs
├── requirements.txt  # Python dependencies
└── README.md         # This documentation


---

## ⚙️ How It Works

### ✅ Inputs

Accepts PDF files (max 50 pages each) from the `/app/input` directory inside the Docker container.

### 🧠 Processing Logic

1.  The script analyzes the **font size, style, and layout** to determine the hierarchy of headings.
2.  Extracts:
    - `title` (first largest heading on page 1)
    - All relevant headings with corresponding levels (`H1`, `H2`, `H3`)
    - Page numbers for each heading
3.  Outputs a valid JSON file per PDF to `/app/output`, e.g.,:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
🐳 Docker Instructions
🏗️ Build Docker Image
Bash

docker build --platform linux/amd64 -t pdf-outline-extractor:<unique_tag> .
▶️ Run Container
Bash

docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output_jsons:/app/output \
  --network none \
  pdf-outline-extractor:<unique_tag>
This will process all .pdf files in the input/ folder and generate .json output files in output_jsons/.

---

## 📦 Dependencies & Design

### Key Libraries

-   **PyMuPDF (fitz)** for PDF parsing
-   **re** and **collections** for heading structure detection

### Design Considerations

-   **No internet access**: All models and libraries are bundled locally.
-   **Model size constraint**: No model exceeds the 200MB limit.
-   **Execution speed**: Processes a 50-page PDF in < 10 seconds.
-   **Avoids font-size-only heuristics**: Uses a combination of size, position, and hierarchy logic.

---
✅ Compliance
Requirement	Status
Docker + AMD64	✅
No Internet Calls	✅
CPU-only	✅
<200MB Models	✅
Executes in <10s	✅

Export to Sheets
📝 Notes
Modular structure ensures easy extension for Round 1B.

Works with multilingual PDFs (basic testing done with Hindi/Japanese content).

🔒 Disclaimer
This repository is private as per competition rules. It will be made public post-deadline.