# Deploying to Vercel

This application is built with Python (Flask) for the backend and pure HTML/JS for the frontend. Because of this, we can deploy the backend APIs seamlessly using **Vercel's Serverless Python Functions**.

This repository is already properly configured for Vercel deployment via the included `vercel.json` file.

## Prerequisites
1. A [GitHub](https://github.com/) account.
2. A [Vercel](https://vercel.com/) account (you can log in using GitHub).

## Deployment Steps

### 1. Push to GitHub
Ensure all your latest changes (including `vercel.json` and `app.py`) have been pushed to your GitHub repository.

### 2. Import to Vercel
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click the **Add New...** button and select **Project**.
3. Under the **"Import Git Repository"** section, find `virtualization_paging-segmentation` and click **Import**.

### 3. Vercel Configuration
Vercel should automatically detect most settings, but verify the following:
- **Framework Preset**: Other
- **Root Directory**: `./` (leave default)

**Environment Variables:**
There are no required environment variables for this simulator, meaning you can skip this section entirely.

### 4. Deploy
1. Click the **Deploy** button.
2. Vercel will install the dependencies defined in `requirements.txt` and package `app.py` as a serverless Python function.
3. Once the build finishes (usually takes less than 2 minutes), you'll be given a live production URL!

---

## Technical Details: How it Works

Vercel uses the `@vercel/python` builder defined in `vercel.json` to turn `app.py` into a serverless function. 
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ]
}
```
Vercel's Python runtime strictly looks for a variable named `app` in the main entry file. Because our internal Flask instance was originally named `flask_app`, the bottom of `app.py` was updated to explicitly export `app = flask_app` for compatibility. All traffic is then routed precisely to this `app` instance using the route configuration.
