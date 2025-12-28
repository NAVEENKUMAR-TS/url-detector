import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini: {e}")

def get_gemini_analysis(url: str, prediction_label: str, confidence: float):
    if not GEMINI_API_KEY:
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
    1. Independently verify if the URL is "Safe", "Malicious", or "Adversarial".
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
        # Use the standard model name
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Request JSON output
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        try:
            data = json.loads(response.text)
            return data
        except json.JSONDecodeError:
            # Fallback for parsing error
            return {
                "verdict": prediction_label,
                "confidence_score": confidence,
                "reasoning": "Gemini response format error.",
                "adversarial_technique": None
            }

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "verdict": prediction_label,
            "confidence_score": confidence,
            "reasoning": f"AI Verification failed: {str(e)}",
            "adversarial_technique": None
        }
