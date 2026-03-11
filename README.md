# BW Migration Intelligence Platform — Streamlit Deployment

## What's in this folder

| File | Purpose |
|---|---|
| `app.py` | Streamlit host — login, user management, shared storage |
| `bw_platform.html` | Your BW platform HTML app ← **you add this** |
| `requirements.txt` | Python dependencies (just streamlit) |
| `data/` | Created automatically — stores users + BW state |

---

## Step 1 — Add your HTML file

Copy your `BW_Migration_Intelligence_Platform_v3.html` into this folder and rename it:

```
bw_platform.html
```

---

## Step 2 — Create a GitHub repo

1. Go to **github.com** → click **New repository**
2. Name it e.g. `bw-migration-platform`
3. Set it to **Private** (recommended — contains your BW data)
4. **Don't** initialise with README (you already have files)
5. Click **Create repository**

GitHub will show you commands. Run these in this folder:

```bash
git init
git add .
git commit -m "Initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bw-migration-platform.git
git push -u origin main
```

---

## Step 3 — Deploy to Streamlit Cloud

1. Go to **share.streamlit.io**
2. Sign in with your GitHub account
3. Click **New app**
4. Select your repo: `bw-migration-platform`
5. Branch: `main`
6. Main file path: `app.py`
7. Click **Deploy**

Streamlit Cloud will build and deploy. Takes ~2 minutes.
You'll get a URL like: `https://your-app-name.streamlit.app`

---

## Step 4 — Share the URL

Send the URL to your team. That's it.

- **Admin** logs in → uploads BW ZIP data → clicks 💾 Save → data stored on server
- **Analyst** logs in → stored data loads automatically → full analysis available
- **Guest** logs in → uploads their own ZIP → isolated session

---

## Managing Users

Log in as Admin → click **⚙ Users** in the top bar to:
- Add unlimited Analyst and Guest accounts
- Change passwords
- Delete users

Changes take effect immediately for all users.

---

## Default Credentials (change after first login!)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Analyst | `analyst` | `bw2024` |
| Guest | `guest` | `guest123` |

---

## Data Persistence on Streamlit Cloud

Streamlit Cloud **resets the filesystem on every redeploy**. To keep your data:

**Option A (Simple):** Commit the `data/` folder to your GitHub repo after saving data.
```bash
git add data/
git commit -m "Update BW state"
git push
```

**Option B (Better for production):** Use Streamlit Secrets + an external store.
Ask your IT team to set up a simple cloud storage bucket (AWS S3, Azure Blob, or Google Cloud Storage) — I can add the integration code if needed.

---

## Running Locally (for testing)

```bash
pip install streamlit
streamlit run app.py
```

Opens at `http://localhost:8501`
