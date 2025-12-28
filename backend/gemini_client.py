import os
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")

def get_gemini_analysis(url: str, prediction_label: str, confidence: float):
    if not client:
        return {
            "verdict": prediction_label,
            "confidence_score": confidence,
            "reasoning": "Gemini API Key missing.",
            "adversarial_technique": None
        }

    prompt = f"""
    You are a cybersecurity expert. Analyze this URL for safety: "{url}"
    
    Context:
    - Local Deep Learning Model Prediction: {prediction_label}
    - Local Model Confidence: {confidence:.2f}

    Your Task:
    1. Independently verify if the URL is "Safe", "Malicious", or "Adversarial" (phishing, evasion techniques, etc.).
    2. If the local model is wrong, OVERRIDE it.
    3. Provide a reasoning summary strictly limited to 3 lines.
    4. If Adversarial, identify the specific technique/pattern.

    Output MUST be valid JSON only:
    {{
        "verdict": "Safe" | "Malicious" | "Adversarial",
        "confidence_score": <float between 0.0 and 1.0>,
        "reasoning": "<string, max 3 lines>",
        "adversarial_technique": "<string or null>"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Parse JSON
        import json
        try:
            data = json.loads(response.text)
            return data
        except json.JSONDecodeError:
            # Fallback if raw text
            return {
                "verdict": prediction_label,
                "confidence_score": confidence,
                "reasoning": "Gemini analysis format error.",
                "adversarial_technique": None
            }

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "verdict": prediction_label,
            "confidence_score": confidence,
            "reasoning": "AI Verification unavailable.",
            "adversarial_technique": None
        }
