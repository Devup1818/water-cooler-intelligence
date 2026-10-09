# 🚀 Production Deployment Guide: Git, Supabase & Vercel
## Cool Home (India) / Fresco Casa · Tender Command Center

This guide gives you the exact, copy-paste steps to take the Water Cooler Tender Intelligence Command Center live on the internet with **GitHub**, **Supabase (Cloud Database)**, and **Vercel (Live Web Dashboard)**.

---

### 📦 Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │             GitHub Repository                │
                      │        (Source Code & Intelligence)          │
                      └──────────────┬───────────────────────────────┘
                                     │ Auto-Deploy on Git Push
                                     ▼
┌─────────────────────────┐                     ┌──────────────────────────────┐
│    Supabase (Cloud)     │ ◄───────────────────┤        Vercel (Live)         │
│  PostgreSQL Master DB   │  Real-time Bids API │   Field Notes Web Dashboard  │
│  776 Bids, 23 Awards    │                     │ https://coolhome.vercel.app  │
└─────────────────────────┘                     └──────────────────────────────┘
```

---

## 🛠️ Step 1: Push Code to Git & GitHub

Open your Mac terminal in `/Users/deveshupadhyay/Water cool` and run these 3 commands:

```bash
# 1. Initialize git and stage all intelligence files (PDFs excluded via .gitignore)
git init
git add .
git commit -m "feat: complete water cooler tender command center with 4 subagents, Supabase schema & Vercel config"

# 2. Create and push to a new GitHub repository (using GitHub CLI)
gh repo create water-cooler-intelligence --public --source=. --remote=origin --push

# (Alternative if not using gh CLI: create repo manually on github.com and run):
# git remote add origin https://github.com/<your-username>/water-cooler-intelligence.git
# git branch -M main
# git push -u origin main
```

---

## 🗄️ Step 2: Set Up Supabase (Free Cloud Database)

1. Go to **[supabase.com](https://supabase.com)** and sign in / sign up (free tier).
2. Click **New Project** and name it `coolhome-tenders` (select region `South Asia (Mumbai)` for fastest speeds in India).
3. Open the **SQL Editor** in your Supabase dashboard (left sidebar icon `>_`):
   * Click **New query**.
   * Copy and paste the entire contents of **[`supabase/schema.sql`](supabase/schema.sql)** and click **Run**.
     *(This creates the `bids`, `bid_docs`, `sellers`, `awards`, and `runs` tables with security policies and search indexes).*
   * Click **New query** again.
   * Copy and paste the entire contents of **[`supabase/seed.sql`](supabase/seed.sql)** and click **Run**.
     *(This inserts all 8 tracked competitor profiles and 23 verified historical contracts).*
4. Under **Project Settings -> API**, note down:
   * **Project URL** (e.g., `https://xyzcompany.supabase.co`)
   * **Anon / Public Key** (e.g., `eyJhbGciOi...`)
   * **Service Role Key** (for backend automated ingestion)

*(Optional: To sync all 776 bids automatically from SQLite to Supabase via Python, run:)*
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
python3 intel/export_supabase.py --sync
```

---

## 🌐 Step 3: Deploy Live on Vercel (1-Click)

1. Go to **[vercel.com](https://vercel.com)** and sign in with your GitHub account.
2. Click **Add New... -> Project**.
3. Select your GitHub repository (`water-cooler-intelligence`).
4. Keep all default build settings (Framework: `Other`, Root Directory: `./`).
5. Click **Deploy**.

Vercel will build and assign you a permanent live HTTPS link in under 30 seconds (e.g. `https://coolhome-tenders.vercel.app`):
* The homepage immediately serves the **Field Notes Web Command Center**.
* Clean URLs and security headers are handled automatically by **[`vercel.json`](vercel.json)**.
* Share the link with your factory, sales team, or bidding partners on their mobile phones and laptops!

---

## 🔄 Daily Live Sync on Autopilot

Whenever you run a fresh scrape on your Mac:
```bash
# 1-click autonomous sync: sweeps GeM + state portals & updates preview
./intel/auto_sync.sh

# Commit and push updates to live Vercel dashboard:
git commit -am "chore: sync fresh daily tenders" && git push
```
*(Vercel automatically redeploys your updated live dashboard in seconds!)*
