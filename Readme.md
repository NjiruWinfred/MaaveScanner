# Maave Ingredient Scanner API

## Overview

Maave Scanner is an AI-powered API that scans ingredient labels from baby products using OCR and Gemini AI.

The system:

- extracts text from product images
- corrects OCR mistakes using Gemini
- compares ingredients against the Maave Knowledge Base
- determines the overall safety rating
- generates an easy-to-understand explanation for parents

---

## Tech Stack

- FastAPI
- EasyOCR
- Google Gemini
- Pandas
- OpenCV

---

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Maave-Scanner.git
```

Install packages

```bash
pip install -r requirements.txt
```

Create an environment variable

Windows

```bash
set GEMINI_API_KEY=YOUR_API_KEY
```

Mac/Linux

```bash
export GEMINI_API_KEY=YOUR_API_KEY
```

Run the API

```bash
uvicorn app:app --reload
```

---

## API Endpoints

### Home

GET /

Returns API status.

---

### Health Check

GET /health

Returns API health.

---

### Scan Product

POST /scan

Accepts an uploaded product image.

Example response

```json
{
  "status": "success",
  "results": {
    "overall_verdict": "Safe",
    "ingredients": [
      {
        "ingredient": "glycerin",
        "safety rating": "Safe"
      }
    ],
    "explanation": "This product appears safe for most babies..."
  }
}
```

---

## Deployment

Deploy using Render as a Python Web Service.

Build Command

```bash
pip install -r requirements.txt
```

Start Command

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```
