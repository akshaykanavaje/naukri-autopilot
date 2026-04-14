# ============================================================
#  applier.py  —  Core automation logic
# ============================================================

import re
import time
import random
from urllib.parse import urlencode
from playwright.sync_api import Page, TimeoutError as PWTimeout
import config
from logger import already_applied, log_application, log_manual, log_questions

def _is_relevant(title: str) -> bool:
    """Check if job title contains any relevant keyword from config."""
    t = title.lower()
    return any(kw.lower() in t for kw in config.RELEVANT_KEYWORDS)


# ── Helpers ──────────────────────────────────────────────────

def _delay(lo: float = 1.5, hi: float = 3.2) -> None:
    time.sleep(random.uniform(lo, hi))


def _parse_url_meta(job_url: str) -> tuple:
    """
    Extract experience and city from Naukri job URL.
    Much more reliable than scraping card HTML.
    Example URL: .../job-listings-data-analyst-stanza-living-mumbai-2-to-6-years-140426015397
    Returns: (exp_text, city)
    """
    # Experience: pattern like "2-to-6-years"
    exp_match = re.search(r'(\d+)-to-(\d+)-years', job_url)
    exp = f"{exp_match.group(1)}-{exp_match.group(2)} Yrs" if exp_match else "?"

    # City: word just before experience pattern, after removing job id
    url_clean = re.sub(r'-\d{12,}$', '', job_url)
    url_no_exp = re.sub(r'-\d+-to-\d+-years.*$', '', url_clean)
    slug = url_no_exp.split('job-listings-')[-1]
    parts = slug.split('-')
    city = parts[-1].title() if parts else "?"

    return exp, city


# ── Login ─────────────────────────────────────────────────────

def login(page: Page) -> None:
    print("\n🔐 Logging in to Naukri…")
    page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded")
    _delay(2, 3)

    page.fill("#usernameField", config.NAUKRI_EMAIL)
    _delay(0.5, 1)
    page.fill("#passwordField", config.NAUKRI_PASSWORD)
    _delay(0.5, 1)
    page.click("button[type='submit']")
    _delay(4, 6)

    # Wait up to 8 seconds for redirect to homepage
    for _ in range(8):
        if "mnjuser" in page.url or ("naukri.com" in page.url and "login" not in page.url):
            print("✅ Login successful!")
            return
        time.sleep(1)

    # Still on login page — likely OTP or CAPTCHA
    print("⚠️  Please complete login manually in the browser window.")
    print("   (OTP / CAPTCHA / any prompt — handle it there)")
    input("   Once you see the Naukri homepage, press ENTER here to continue…")


# ── URL Builder (#8 — sort by date) ──────────────────────────

def _build_search_url(k: str, slug: str, page_num: int = 1) -> str:
    """
    Build Naukri search URL matching exact format from manual working search.
    jobAge=15 handles freshness directly in URL — no side panel click needed.
    Uses %20 encoding to match Naukri's own URL format.
    """
    from urllib.parse import quote
    k_encoded = quote(k)
    l_encoded = quote(config.LOCATION_STRING)
    return (
        f"https://www.naukri.com/{slug}"
        f"?k={k_encoded}"
        f"&l={l_encoded}"
        f"&experience={config.EXP_MIN}"
        f"&jobAge=15"
        f"&pageNo={page_num}"
        f"&nignbevent_src=jobsearchDeskGNB"
    )


# ── Job Cards ─────────────────────────────────────────────────

def _get_job_cards(page: Page) -> list:
    try:
        page.wait_for_selector("div.srp-jobtuple-wrapper", timeout=10000)
        return page.query_selector_all("div.srp-jobtuple-wrapper")
    except PWTimeout:
        return []


def _extract_card_meta(card) -> dict:
    try:
        job_id     = card.get_attribute("data-job-id") or ""
        title_el   = card.query_selector("div.row1 a")
        company_el = card.query_selector("div.row2 a") or card.query_selector("div.row2")

        # Confirmed selectors from HTML inspection
        exp_el = card.query_selector("span.exp-wrap")
        loc_el = card.query_selector("span.loc-wrap")

        job_url = title_el.get_attribute("href") if title_el else ""

        # Clean up exp text — remove icon text, keep just "2-4 Yrs"
        exp_text = exp_el.inner_text().strip() if exp_el else ""
        # Clean up location — remove icon text, keep just city name
        loc_text = loc_el.inner_text().strip() if loc_el else ""

        return {
            "job_id":   job_id,
            "title":    title_el.inner_text().strip()   if title_el   else "Unknown",
            "company":  company_el.inner_text().strip() if company_el else "Unknown",
            "location": loc_text,
            "exp_text": exp_text,
            "job_url":  job_url,
        }
    except Exception:
        return {}


# ── Detect questions on apply page ───────────────────────────

def _has_questions(detail: Page) -> bool:
    """Check if the apply flow has a questions form."""
    question_signals = [
        "div.question",
        "div[class*='question']",
        "form.applyForm",
        "div.chatbot",
        "div[class*='chatbot']",
        "textarea",
        "input[type='text']:not([type='hidden'])",
    ]
    for sel in question_signals:
        try:
            el = detail.query_selector(sel)
            if el and el.is_visible():
                return True
        except Exception:
            pass
    return False


# ── Apply ─────────────────────────────────────────────────────

def _try_easy_apply(page: Page, card, meta: dict, label: str) -> bool:
    """
    Open job detail, apply if Easy Apply with no questions.
    Saves portal jobs and question jobs to separate CSVs.
    Only logs to applied_jobs.csv after confirmed apply.
    Returns True if successfully applied.
    """
    job_id  = meta.get("job_id",   "")
    title   = meta.get("title",    "?")
    company = meta.get("company",  "?")
    job_url = meta.get("job_url",  "")

    # Parse experience and city from URL — reliable, no HTML scraping
    exp, loc = _parse_url_meta(job_url)

    if not job_id:
        return False

    # ── Relevance check ──────────────────────────────────────
    if not _is_relevant(title):
        print(f"  🚫 Irrelevant → {title} @ {company}")
        return False

    # ── Blocked company check ─────────────────────────────────
    if any(b.lower() in company.lower() for b in config.BLOCKED_COMPANIES):
        return False  # silent skip

    # ── Experience check using parsed URL data ───────────────
    if exp and exp != "?":
        nums = re.findall(r'\d+', exp)
        if nums and int(nums[0]) > 4:
            print(f"  📅 Exp mismatch ({exp}) → {title} @ {company}")
            return False

    # ── #4 Duplicate check — silent skip, no terminal noise ──
    if already_applied(job_id):
        return False

    # Open detail in new tab
    try:
        title_link = card.query_selector("div.row1 a")
        if not title_link:
            return False
        with page.context.expect_page(timeout=10000) as new_page_info:
            title_link.click()
        detail = new_page_info.value
        detail.wait_for_load_state("domcontentloaded")
        _delay(2, 3)
        # Wait for either apply button or company-site button to appear
        try:
            detail.wait_for_selector(
                "button#apply-button, button#company-site-button",
                timeout=8000
            )
        except PWTimeout:
            pass  # will handle below if neither found
    except Exception as e:
        print(f"  ⚠️  Could not open detail page: {e}")
        return False

    try:
        # ── #5 Check for portal button FIRST (separate button id) ─
        # Naukri uses button#company-site-button for portal jobs
        # and button#apply-button for Easy Apply — they are different buttons
        company_btn = detail.query_selector("button#company-site-button")
        if company_btn:
            log_manual(job_id, title, company, exp, loc, job_url, label)
            print(f"  🌐 Saved for manual → {title} @ {company}")
            detail.close()
            return False

        # ── Check for Easy Apply button ───────────────────────
        apply_btn = detail.query_selector("button#apply-button")
        if not apply_btn:
            print(f"  🔒 No Apply button → {title} @ {company}")
            detail.close()
            return False

        # Click Apply
        apply_btn.click()

        # Wait 3 seconds for page to settle after click/refresh
        _delay(3, 4)

        # ── Step 1: Check for success page FIRST ─────────────
        # Confirmed selector from HTML: div.applied-job-content
        try:
            success = detail.query_selector("div.applied-job-content")
            if success:
                log_application(job_id, title, company, exp, loc, label)
                print(f"  ✅ Applied → {title} @ {company} | {loc}")
                detail.close()
                return True
        except Exception:
            pass

        # ── Step 2: Check for questions form ─────────────────
        if _has_questions(detail):
            log_questions(job_id, title, company, exp, loc, job_url, label)
            print(f"  ❓ Has questions — saved for manual → {title} @ {company}")
            try:
                close_btn = (detail.query_selector("button[class*='close']")
                             or detail.query_selector("button:has-text('Cancel')")
                             or detail.query_selector("button:has-text('Close')"))
                if close_btn:
                    close_btn.click()
                    _delay(1, 2)
            except Exception:
                pass
            detail.close()
            return False

        # ── Step 3: Neither success nor questions — uncertain ─
        print(f"  ⚠️  Uncertain result — not logged → {title} @ {company}")
        detail.close()
        return False

    except Exception as e:
        print(f"  ⚠️  Error during apply: {title} — {e}")
        try:
            detail.close()
        except Exception:
            pass
        return False


# ── Main Search Runner (#3 — 2 pages) ────────────────────────

def run_search(page: Page, group: dict, session_counter: list) -> None:
    if session_counter[0] >= config.MAX_APPLY_PER_SESSION:
        return

    label = group["label"]

    for page_num in range(1, config.PAGES_PER_GROUP + 1):
        if session_counter[0] >= config.MAX_APPLY_PER_SESSION:
            break

        url = _build_search_url(group["k"], group["slug"], page_num)

        print(f"\n{'='*55}")
        print(f"🔍 {label}  —  Page {page_num}")
        print(f"   {url}")
        print(f"{'='*55}")

        page.goto(url, wait_until="domcontentloaded")
        _delay(3, 5)

        # ── Dismiss location popup if it appears ─────────────
        try:
            deny_btn = page.query_selector("button:has-text('Never allow')")
            if deny_btn and deny_btn.is_visible():
                deny_btn.click()
                print("   📍 Dismissed location popup")
                _delay(1, 2)
        except Exception:
            pass

        # Sort by Recommended (default) — date sort causes page overlap duplicates

        # Freshness handled via jobAge=15 in URL — no click needed

        cards = _get_job_cards(page)
        if not cards:
            print(f"   ⚠️  No listings found. Page title: {page.title()}")
            break

        print(f"   📋 Found {len(cards)} listings")

        for card in cards:
            if session_counter[0] >= config.MAX_APPLY_PER_SESSION:
                print(f"\n🛑 Session cap of {config.MAX_APPLY_PER_SESSION} reached. Stopping.")
                return

            meta = _extract_card_meta(card)
            if not meta or not meta.get("job_id"):
                continue

            applied = _try_easy_apply(page, card, meta, label)
            if applied:
                session_counter[0] += 1

            _delay(1.5, 3)