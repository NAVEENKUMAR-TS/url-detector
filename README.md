# URL Detector Dashboard

AI-Powered URL Safety Analysis Dashboard using Deep Learning and Google Gemini.

## Features
*   **No-Build Frontend**: Uses a single HTML file with CDN libraries (React, Tailwind). Fast and simple.
*   **Dual-Engine Detection**: Checks URLs with a local TensorFlow model AND Google Gemini API.
*   **History & Stats**: Persists scan results to MongoDB.

## Local Setup

1.  **Backend Setup**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Run Application**:
    ```bash
    # Ensure you have your ENV variables ready or in a .env file
    # export GEMINI_API_KEY=...
    # export MONGO_URI=...

    uvicorn main:app --reload
    ```

3.  **Access**:
    Open `http://localhost:8000` in your browser.

## Deployment (Render)

This project includes a `render.yaml` Blueprint.

1.  Push this code to **GitHub**.
2.  Go to **Render Dashboard** -> **New Blueprint**.
3.  Select your repository.
4.  Enter your `GEMINI_API_KEY` and `MONGO_URI` when prompted.
5.  Deploy!
