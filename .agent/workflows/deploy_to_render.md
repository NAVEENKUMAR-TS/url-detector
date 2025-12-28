---
description: Deploy the URL Detector Dashboard to Render using Blueprints
---

# Deploy to Render

This project is configured for **Render Blueprints**, which allows for one-click deployment configuration.

## Prerequisites
1.  A [GitHub](https://github.com/) account.
2.  A [Render](https://render.com/) account.
3.  Your `GEMINI_API_KEY` and `MONGO_URI`.

## Step 1: Push to GitHub
If you haven't already, push this project to a new GitHub repository.

```bash
git init
git add .
git commit -m "Initial commit"
# Create a new repo on GitHub, then:
git remote add origin <your-repo-url>
git push -u origin master
```

## Step 2: Create Blueprint on Render
1.  Log in to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub account if needed, then select your `url-detector` repository.
4.  Render will automatically read the `render.yaml` file.

## Step 3: Configure Environment
Render will ask you to provide values for the environment variables defined in `render.yaml`:

*   **MONGO_URI**: Your MongoDB connection string (e.g., from MongoDB Atlas).
*   **GEMINI_API_KEY**: Your Google Gemini API Key.

## Step 4: Deploy
1.  Click **Apply**.
2.  Render will build the backend, install Python dependencies, and start the server.
3.  Once finished, you will get a URL (e.g., `https://url-detector-backend.onrender.com`).
4.  Open that URL to use your app!
