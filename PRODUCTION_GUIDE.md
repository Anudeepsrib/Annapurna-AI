# Production Deployment Guide: Annapurna-AI

This guide outlines the steps to deploy the Annapurna-AI application to production using a zero/low-cost strategy.

## Deployment Checklist (To-Do List)

- [ ] **Configure USDA API Key**: Obtain a key or decide to use the demo key.
- [ ] **Deploy Backend to Render**:
    - [ ] Create New Component on Render (Web Service).
    - [ ] Set Build Command: `pip install -r backend/requirements.txt`.
    - [ ] Set Start Command: `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`.
    - [ ] Add Environment Variable `PYTHON_VERSION`: `3.11.0`.
    - [ ] (Optional) Add `USDA_API_KEY`.
- [ ] **Deploy Frontend to Vercel**:
    - [ ] Import Repository to Vercel.
    - [ ] Set Environment Variable `BACKEND_URL` to your Render URL (no trailing slash).
    - [ ] Deploy.
- [ ] **Verify**:
    - [ ] Visit Vercel URL.
    - [ ] Generate a plan and ensure it loads.

## Architecture Overview

The application is split into two parts:
1.  **Frontend**: Next.js application (hosted on **Vercel** - Free Tier).
2.  **Backend**: Python FastAPI application (hosted on **Render** - Free Tier).

Communication between frontend and backend is handled via Next.js Rewrites, which simplifies CORS configuration and keeps API calls clean.

---

## Prerequisites

1.  **GitHub Account**: Ensure this repository is pushed to your GitHub account.
2.  **Render Account**: Sign up at [render.com](https://render.com).
3.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
4.  (Optional) **USDA API Key**: Get a free API key from [USDA FoodData Central](https://fdc.nal.usda.gov/api-key-signup.html) for better rate limits.

---

## Step 0: Setup Authentication (Clerk)

Before deploying, you must configure Clerk:
1.  **Clerk Dashboard**: Create a new application (if not already done).
2.  **API Keys**: Go to **API Keys** in the sidebar.
    -   Copy `Publishable Key` (e.g., `pk_test_...`)
    -   Copy `Secret Key` (e.g., `sk_test_...`)
3.  **PEM Public Key**: Go to **API Keys -> Advanced** (bottom).
    -   Copy the **PEM Public Key** (starts with `-----BEGIN PUBLIC KEY-----`).

---

## Step 1: Deploy Backend (Render)

We will use Render to host the Python backend.

### Option A: Using `render.yaml` (Blueprint)

1.  Log in to the **Render Dashboard**.
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub repository `Annapurna-AI`.
4.  Render will verify the configuration.
5.  **Environment Variables**: You MUST add the following secrets manually (Render might prompt):
    -   `OPENAI_API_KEY` (Required for AI features).
    -   `CLERK_PEM_PUBLIC_KEY`: Paste the full PEM key from Step 0.
    -   `PYTHON_VERSION`: `3.11.0`
6.  Click **Apply**.

### Option B: Manual Setup (If Blueprint fails)

1.  Click **New +** -> **Web Service**.
2.  Connect your repository.
3.  **Name**: `annapurna-backend` (or similar).
4.  **Runtime**: `Python 3`.
5.  **Build Command**: `pip install -r backend/requirements.txt`
6.  **Start Command**: `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
7.  **Environment Variables**:
    -   `PYTHON_VERSION`: `3.11.0`
    -   `USDA_API_KEY`: `Your_USDA_Key` (Optional).
    -   `OPENAI_API_KEY`: `sk-...` (Required for AI).
    -   `CLERK_PEM_PUBLIC_KEY`: `-----BEGIN PUBLIC KEY-----\n...` (Paste full key).

### Verification
Once deployed, Render will provide a URL (e.g., `https://annapurna-backend.onrender.com`).
-   Visit it -> Should return `{"status": "ok", ...}`.

---

## Step 2: Deploy Frontend (Vercel)

We will use Vercel to host the Next.js frontend.

1.  Log in to the **Vercel Dashboard**.
2.  Click **Add New...** -> **Project**.
3.  Import your `Annapurna-AI` GitHub repository.
4.  **Environment Variables**:
    -   `BACKEND_URL`: The Render Backend URL (e.g., `https://annapurna-backend.onrender.com`).
    -   `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Paste from Step 0.
    -   `CLERK_SECRET_KEY`: Paste from Step 0.
5.  Click **Deploy**.

---

## Step 3: Final Verification

1.  Visit your new Vercel URL.
2.  **Sign In**: Use the Clerk Sign-In button (create a test account).
3.  **Generate Plan**: Go to Profile -> Generate.
    -   This confirms: Auth flow -> Frontend -> Proxy -> Backend -> Auth Verification -> LLM -> Response.

## Observability & Monitoring (New)

We have integrated **LiteLLM**, **Clerk**, and **Structlog**.

### 1. Application Logs
Check Render Logs for structured JSON output.

### 2. LLM Tracing
Add `LITELLM_CALLBACK="langfuse"` and Langfuse keys to Render to track AI usage.


