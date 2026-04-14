# ============================================================
#  config.py  —  Your personal settings. Edit this only.
# ============================================================

# ---------- Naukri Login ----------
NAUKRI_EMAIL    = "your_email@gmail.com"
NAUKRI_PASSWORD = "your_password"

# ---------- Experience ----------
EXP_MIN = 3

# ---------- Safety ----------
MAX_APPLY_PER_SESSION = 40  # change to 5 for testing
PAGES_PER_GROUP = 2
HEADLESS = False

# ---------- Locations ----------
LOCATION_STRING = "mumbai (all areas), bangalore, bengaluru, hyderabad, pune, noida, gurugram"

# ---------- Search ----------
SEARCH_GROUPS = [
    {
        "label": "All Data / Analyst / Business Roles",
        "slug":  "data-analyst-data-analysis-data-scientist-data-science-business-analyst-business-analytics-supply-chain-analyst-power-bi-jobs-in-mumbai-all-areas",
        "k":     "data analyst data analysis data scientist data science business analyst business analytics supply chain analyst power bi",
    },
]

# ---------- Title relevance filter ----------
RELEVANT_KEYWORDS = [
    "data analyst", "data analysis", "data scientist", "data science",
    "business analyst", "business analytics", "supply chain analyst",
    "power bi", "mis analyst", "reporting analyst", "bi analyst",
    "operations analyst", "procurement analyst", "inventory analyst",
    "dashboard analyst", "analytics analyst", "junior data scientist",
]

# ---------- Blocked companies ----------
BLOCKED_COMPANIES = [
    "eclerx",
]