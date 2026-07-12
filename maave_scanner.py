import ast
import easyocr
import pandas as pd


class MaaveScanner:

    def __init__(self, database_path, genai_client):

        # Load OCR reader
         if self.reader is None:
            self.reader = easyocr.Reader(["en"])

        # Load ingredient database
        self.maave_knowledge_base = pd.read_excel(database_path)
        self.maave_knowledge_base.columns = (
            self.maave_knowledge_base.columns.str.strip()
        )

        # Standardize ingredient names
        self.maave_knowledge_base["ingredient_name"] = (
            self.maave_knowledge_base["ingredient_name"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        # Gemini client
        self.client = genai_client

    # ---------------------------------------------------------
    # OCR
    # ---------------------------------------------------------

    def extract_text(self, image_path):

        results = self.reader.readtext(image_path)

        text = " ".join(
            [result[1] for result in results]
        )

        return text

    # ---------------------------------------------------------
    # CLEAN OCR TEXT
    # ---------------------------------------------------------

    def clean_text(self, raw_text):

        ingredients = [

            ingredient.strip().lower()

            for ingredient in raw_text.split(",")

            if ingredient.strip()

        ]

        return ingredients

    # ---------------------------------------------------------
    # GEMINI OCR CORRECTION
    # ---------------------------------------------------------

    def ai_correct_ingredients(self, ingredients):

        prompt = f"""
You are an expert in cosmetic INCI ingredient names.

Correct ONLY OCR spelling mistakes.

Rules

- Do not invent ingredients.
- Do not remove ingredients.
- Do not add ingredients.
- Preserve order.
- If unsure keep the original.
- Return ONLY a Python list.

Example

["glycerin","fragrance"]

Ingredients

{ingredients}
"""

        response = self.client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )

        corrected_text = response.text.strip()

        corrected_text = corrected_text.replace(
            "```python",
            ""
        )

        corrected_text = corrected_text.replace(
            "```",
            ""
        )

        corrected_text = corrected_text.strip()

        corrected = ast.literal_eval(
            corrected_text
        )

        corrected = [

            ingredient.lower().strip()

            for ingredient in corrected

        ]

        return corrected

    # ---------------------------------------------------------
    # DATABASE LOOKUP
    # ---------------------------------------------------------

    def lookup_database(self, ingredients):

        scan_results = []

        for ingredient in ingredients:

            match = self.maave_knowledge_base[

                self.maave_knowledge_base["ingredient_name"]

                == ingredient

            ]

            if not match.empty:

                row = match.iloc[0]

                scan_results.append({

                    "ingredient": row["ingredient_name"],

                    "safety rating": row["Safety Rating"]

                })

            else:

                scan_results.append({

                    "ingredient": ingredient,

                    "safety rating": "Unknown"

                })

        return scan_results

    # ---------------------------------------------------------
    # OVERALL VERDICT
    # ---------------------------------------------------------

    def overall_verdict(self, scan_results):

        overall = "Safe"

        for result in scan_results:

            rating = result["safety rating"].lower()

            if rating == "unsafe":

                return "Unsafe"

            elif rating == "caution":

                overall = "Use with Caution"

            elif rating == "unknown":

                if overall == "Safe":

                    overall = "Needs Review"

        return overall

    # ---------------------------------------------------------
    # AI EXPLANATION
    # ---------------------------------------------------------

    def generate_ai_response(

        self,

        overall_verdict,

        scan_results

    ):

        prompt = f"""
You are Maave.

You help parents understand baby product ingredients.

Overall Verdict

{overall_verdict}

Ingredients

{scan_results}

Rules

- Explain in simple language.
- Be warm and supportive.
- Mention only ingredients found.
- Explain why the verdict was reached.
- If Safe reassure the parent.
- If Use with Caution explain what to monitor.
- If Unsafe explain why.
- If Needs Review explain that some ingredients were not recognised.
- Keep the response below 150 words.
"""

        response = self.client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )

        return response.text

    # ---------------------------------------------------------
    # COMPLETE SCAN PIPELINE
    # ---------------------------------------------------------

    def scan(self, image_path):

        raw_text = self.extract_text(image_path)

        ingredients = self.clean_text(raw_text)

        corrected = self.ai_correct_ingredients(
            ingredients
        )

        scan_results = self.lookup_database(
            corrected
        )

        overall = self.overall_verdict(
            scan_results
        )

        explanation = self.generate_ai_response(
            overall,
            scan_results
        )

        return {

            "ocr_text": raw_text,

            "corrected_ingredients": corrected,

            "overall_verdict": overall,

            "scan_results": scan_results,

            "ai_explanation": explanation

        }
