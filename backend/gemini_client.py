import os
import google.genai as genai
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
        return "Gemini API Key not configured. Unable to fetch detailed explanation."

    prompt = f"""
    Analyze this URL: {url}
    
    Our local deep learning model prediction:
    - Status: {prediction_label}
    - Confidence: {confidence:.4f}

    Please provide a concise security analysis. 
    1. Confirm if this looks safe or malicious.
    2. Explain why (e.g., suspicious TLD, typo-squatting, known phishing pattern, or legitimate domain).
    3. If it's adversarial (tricky), mention the technique used.
    
    Keep the response short (under 3 sentences per point) and professional.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Updated to a widely available model, or use 1.5-flash if preferred
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"[Gemini Error]: {str(e)}"
