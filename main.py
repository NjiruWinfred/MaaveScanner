from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os
from google import genai
from maave_scanner import MaaveScanner

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------

app = FastAPI(
    title="Maave Scanner API",
    description="AI-powered baby product ingredient scanner",
    version="1.0.0"
)

# -------------------------------------------------
# Gemini API
# -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# -------------------------------------------------
# Knowledge Base
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "maave_ingredient_database.xlsx"
)

scanner = None

global scanner

if scanner is None:
    scanner = MaaveScanner(
        DATABASE_PATH,
        client
    )

# -------------------------------------------------
# Home Endpoint
# -------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "success",
        "message": "Welcome to the Maave Scanner API"
    }

# -------------------------------------------------
# Health Endpoint
# -------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

# -------------------------------------------------
# Scan Endpoint
# -------------------------------------------------

@app.post("/scan")
async def scan_product(
    file: UploadFile = File(...)
):

    try:

        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix= ".jpg"
        ) as temp:

            shutil.copyfileobj(
                file.file,
                temp
            )

            image_path = temp.name

        raw_text = scanner.extract_text(image_path)

        ingredients = scanner.clean_text(raw_text)

        corrected = scanner.ai_correct_ingredients(
            ingredients
        )

        scan_results = scanner.lookup_database(
            corrected
        )

        overall = scanner.overall_verdict(
            scan_results
        )

        explanation = scanner.generate_ai_response(
            overall,
            scan_results
        )

        os.remove(image_path)

        return JSONResponse(

            status_code=200,

            content={

                "status": "success",

                "ocr_text": raw_text,

                "corrected_ingredients": corrected,

                "overall_verdict": overall,

                "scan_results": scan_results,

                "ai_explanation": explanation

            }

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
