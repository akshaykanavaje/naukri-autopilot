# 🚀 Naukri Autopilot

> An intelligent job application bot that automatically applies to relevant jobs on Naukri.com — so you can focus on preparing for interviews instead of copy-pasting applications.


## 📌 What is This?

Job hunting is repetitive. You search the same roles every day, click Apply on 20+ listings, and most of them take 10 seconds each. That's hours of mindless clicking every week.

**Naukri Autopilot** automates that entire process. It logs into your Naukri account, searches for relevant jobs based on your profile, and applies to Easy Apply listings automatically — using your already-uploaded Naukri resume and profile.

---

## ✨ Features

- 🔐 **Auto Login** — logs into your Naukri account automatically
- 🔍 **Smart Search** — searches using your custom job titles across multiple cities
- ✅ **Easy Apply** — applies to one-click jobs instantly using your Naukri profile
- 🌐 **Portal Detection** — detects "Apply on Company Site" jobs and saves them for manual review
- ❓ **Question Detection** — detects jobs with application questions and saves them for manual review
- 📅 **Freshness Filter** — only searches jobs posted in the last 15 days
- 💼 **Experience Filter** — skips jobs outside your experience range
- 🚫 **Relevance Filter** — skips irrelevant job titles automatically
- 🏢 **Company Blocklist** — block spammy companies from cluttering your results
- 📊 **3 CSV Logs** — tracks every application, portal job, and question job separately
- 🔄 **Duplicate Prevention** — never applies to the same job twice across sessions

---

## 📁 Project Structure

```
naukri-autopilot/
├── main.py              ← Entry point — run this
├── config.py            ← Your settings (edit this only)
├── applier.py           ← Core automation logic
├── logger.py            ← CSV logging system
├── applied_jobs.csv     ← Auto-created: jobs you applied to
├── manual_apply.csv     ← Auto-created: portal jobs to apply manually
└── questions_jobs.csv   ← Auto-created: jobs with questions to answer manually
```

---

## ⚙️ How It Works

```
Login to Naukri
      ↓
Search jobs (your titles + cities + experience + last 15 days)
      ↓
For each listing:
  ├── Irrelevant title?        → 🚫 Skip
  ├── Experience too high?     → 📅 Skip
  ├── Already applied?         → ⏭️  Skip
  ├── Apply on Company Site?   → 🌐 Save to manual_apply.csv
  ├── Has questions?           → ❓ Save to questions_jobs.csv
  └── Easy Apply?              → ✅ Apply + Save to applied_jobs.csv
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.8+** | Core language |
| **Playwright** | Browser automation |
| **CSV** | Application logging |
| **Regex** | URL parsing for experience & location |

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/naukri-autopilot.git
cd naukri-autopilot
```

### 2. Install dependencies
```bash
pip install playwright
python -m playwright install chromium
```

### 3. Configure your settings
Open `config.py` and fill in your details:

```python
NAUKRI_EMAIL    = "your_email@gmail.com"
NAUKRI_PASSWORD = "your_password"
```

### 4. Run the bot
```bash
python main.py
```

---

## 🔧 Configuration

All settings are in `config.py` — you never need to touch any other file.

```python
# How many jobs to apply per session
MAX_APPLY_PER_SESSION = 40

# How many pages to search per group (20 jobs per page)
PAGES_PER_GROUP = 2

# Your experience level
EXP_MIN = 3

# Cities to search in
LOCATION_STRING = "mumbai (all areas), bangalore, bengaluru, hyderabad, pune, noida, gurugram"

# Job titles to search for
SEARCH_GROUPS = [
    {
        "label": "All Data / Analyst / Business Roles",
        "slug":  "data-analyst-data-scientist-business-analyst...",
        "k":     "data analyst data analysis data scientist...",
    }
]

# Companies to block (spammy recruiters)
BLOCKED_COMPANIES = ["eclerx"]
```

---

## 📊 Output — 3 CSV Files

### `applied_jobs.csv` ✅
Jobs the bot automatically applied to.
| job_id | title | company | experience | location | applied_at |
|---|---|---|---|---|---|
| 010426915284 | Data Scientist | ABB | 2-7 Yrs | Bengaluru | 2026-04-14 15:04 |

### `manual_apply.csv` 🌐
Jobs that redirect to company portals — apply manually with direct links.
| job_id | title | company | experience | location | job_url | saved_at |
|---|---|---|---|---|---|---|
| 020426927005 | Data Analyst | Optum | 3-8 Yrs | Gurugram | https://... | 2026-04-14 15:04 |

### `questions_jobs.csv` ❓
Jobs that have application questions — answer and apply manually.
| job_id | title | company | experience | location | job_url | saved_at |
|---|---|---|---|---|---|---|
| 090426009084 | Data Analyst | AB InBev | 2-4 Yrs | Bengaluru | https://... | 2026-04-14 15:05 |

---

## 📈 Typical Session Results

Out of ~40 jobs scanned per session:
- ✅ **8-15 auto-applied** directly
- 🌐 **10-15 saved** for manual portal applications
- ❓ **5-8 saved** with questions for manual review

---

## ⚠️ Important Notes

- Make sure your **Naukri profile is 100% complete** and resume is uploaded before running
- Run **once per day** — running too frequently may trigger Naukri's bot detection
- Keep `MAX_APPLY_PER_SESSION ≤ 40` per run for safety
- First run may ask you to solve a CAPTCHA manually in the browser window

---

## 🗺️ Roadmap

- [ ] AI-powered cover letter generation per application
- [ ] Stage 3 support — auto-answer common questions using GPT/Claude
- [ ] Email/WhatsApp notification after each session
- [ ] Dashboard to track application stats over time
- [ ] Support for LinkedIn Easy Apply

---

## 👤 Author

Built by **Akshay Kanavaje** — a data scientist who got tired of manually applying to jobs and decided to automate the problem away.


*If this project helped you, consider giving it a ⭐ on GitHub!*
