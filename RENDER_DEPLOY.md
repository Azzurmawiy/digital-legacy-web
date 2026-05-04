# 🚀 Render + Vercel Deployment Guide
## Digital Legacy Platform

This guide explains how to deploy your project using **Vercel** (for the React Frontend) and **Render** (for the Django Backend + PostgreSQL).

---

## 1. Frontend (Vercel)
Vercel is the best home for your React UI.

1.  Push your code to **GitHub**.
2.  Log in to [Vercel](https://vercel.com/) and click **"Add New" -> "Project"**.
3.  Import your `digital-legacy-web` repository.
4.  **Framework Preset:** Vite.
5.  **Root Directory:** `frontend` (Important!)
6.  **Environment Variables:**
    *   `VITE_API_URL`: Set this to your Render backend URL (e.g., `https://digital-legacy-api.onrender.com/api/v1`)
7.  Click **Deploy**.

---

## 2. Backend (Render)
Render will host your Django API and your Database.

### Step A: Create a PostgreSQL Database
1.  On the [Render Dashboard](https://dashboard.render.com/), click **"New" -> "PostgreSQL"**.
2.  Name: `digital-legacy-db`.
3.  Plan: **Free**.
4.  Click **Create**. Copy the **Internal Database URL** once it's ready.

### Step B: Create the Web Service (Django)
1.  Click **"New" -> "Web Service"**.
2.  Connect your GitHub repository.
3.  **Name:** `digital-legacy-api`.
4.  **Language:** `Python`.
5.  **Build Command:** `./render-build.sh` (We will create this file below).
6.  **Start Command:** `gunicorn config.wsgi:application`.
7.  **Environment Variables:**
    *   `PYTHON_VERSION`: `3.12.3`
    *   `DEBUG`: `False`
    *   `DATABASE_URL`: (Paste your Render Postgres URL)
    *   `SECRET_KEY`: (Generate a random string)
    *   `ALLOWED_HOSTS`: `digital-legacy-api.onrender.com`
    *   `CORS_ALLOWED_ORIGINS`: (Your Vercel URL)
    *   `ENCRYPTION_KEY`: (Generate a random 64-char hex string)

---

## 3. Necessary Code Changes for Render
Render needs a small script to install dependencies and run migrations.

### Create `render-build.sh` in the root:
```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py migrate
```

---

## 💡 Comparison: Render vs AWS
| Feature | Render + Vercel | AWS EC2 (Free Tier) |
| :--- | :--- | :--- |
| **Ease of Use** | ⭐⭐⭐⭐⭐ (Very Easy) | ⭐⭐ (Manual Setup) |
| **Maintenance** | None (Automatic) | Manual updates required |
| **Performance** | Great (Vercel Edge) | Dependent on t2.micro |
| **Celery Support** | Paid / Complex on Free | Free (runs on the same server) |
| **Cold Starts** | Yes (15-30s wake up) | No (Always on) |

---

*© 2026 Digital Legacy Project — ABU Zaria Computer Engineering*
