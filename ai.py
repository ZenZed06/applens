import os
import time
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT = """
You are an expert fruit quality inspector.

Analyze this apple image and return output in this EXACT format, nothing else:

🍎 Apple Inspection Report

Stage: [Write ONLY one of these exactly: 1-Fresh, 2-Slightly Aged, 3-Deteriorating, 4-Rotten]
Freshness: [0-100]%
Edible: [Yes / No]

Reason:
[One or two sentences in simple words explaining your assessment]

Important: If the image does not contain an apple, do not follow the above format. Instead, respond with only this: "🧠 I'm smart enough to know that's not an apple. Please upload an actual apple image for inspection."
"""

def analyze_apple(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type not in ("image/jpeg", "image/png", "image/webp"):
        raise ValueError(f"Unsupported image type: {mime_type}")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    max_retries = 3
    wait_seconds = 10

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=[
                    PROMPT,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                ]
            )
            return response.text

        except Exception as e:
            error_msg = str(e).lower()

            if "429" in error_msg or "quota" in error_msg or "rate" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(wait_seconds)
                    wait_seconds *= 2  # wait longer each retry: 10s → 20s → 40s
                else:
                    raise Exception("Too many requests. Please wait a moment and try again.")
            else:
                raise  # not a rate limit error, raise immediately


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "appletest.jpg"

    try:
        result = analyze_apple(path)
        print(result)
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"API Error: {e}")