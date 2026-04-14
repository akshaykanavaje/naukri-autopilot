# 🚀 Naukri Auto-Applier — Setup Guide

## What This Does
Automatically applies to Easy Apply jobs on Naukri based on your job titles,
experience level (2–3 years), and preferred locations. Skips portal redirects.
Logs every application to `applied_jobs.csv` so it never double-applies.

---

## 📁 Files
```
naukri_auto_apply/
├── main.py          ← Run this
├── config.py        ← Your settings (edit this first)
├── applier.py       ← Core automation (don't touch)
├── logger.py        ← CSV logging (don't touch)
└── applied_jobs.csv ← Auto-created after first run
```

---

## ⚙️ One-Time Setup

### 1. Install Python 3.8+
Download from https://www.python.org/downloads/

### 2. Install dependencies
Open terminal/command prompt in this folder and run:
```bash
pip install playwright
playwright install chromium
```

### 3. Edit config.py
Open `config.py` and fill in:
```python
NAUKRI_EMAIL    = "your_email@gmail.com"
NAUKRI_PASSWORD = "your_password"
```
Everything else (job titles, locations, experience) is already set for you.

---

## ▶️ Running the Script

```bash
python main.py
```

A Chrome window will open. You'll see it:
1. Log into Naukri
2. Search each job title in each city
3. Click Apply on Easy Apply jobs
4. Log each application

---

## 🛡️ Tips

| Tip | Why |
|---|---|
| Run once per day | Avoids triggering Naukri's bot detection |
| Keep `MAX_APPLY_PER_SESSION = 40` | Safe daily limit |
| Use home WiFi, not VPN | Consistent IP = less suspicion |
| Watch the first run | Solve any CAPTCHA manually if it appears |

---

## 📊 Checking Your Applications
Open `applied_jobs.csv` in Excel anytime to see:
- Every job you applied to
- Company name, location, date & time

---

## ⚠️ Troubleshooting

**Login fails / CAPTCHA appears**
→ The browser window stays open. Solve it manually, then press ENTER in terminal.

**"No listings found" for all searches**
→ Naukri may have changed their HTML. Check the URL printed in terminal manually.

**Script applies 0 jobs**
→ Your filters may be too strict, or Naukri updated their button selectors.
   Open an issue or tweak `applier.py` → `_try_easy_apply()`.
