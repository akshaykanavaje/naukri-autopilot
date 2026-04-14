# ============================================================
#  main.py  —  Entry point. Run: python main.py
# ============================================================

import os
from playwright.sync_api import sync_playwright
import config
from applier import login, run_search


def _count_rows(filepath: str) -> int:
    if not os.path.exists(filepath):
        return 0
    with open(filepath, encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)  # subtract header


def main() -> None:
    print("=" * 55)
    print("  🚀 Naukri Auto-Applier  —  Easy Apply Only")
    print(f"  📍 Locations : {config.LOCATION_STRING}")
    print(f"  💼 Experience: {config.EXP_MIN} years")
    print(f"  🎯 Groups    : {len(config.SEARCH_GROUPS)}")
    print(f"  📄 Pages/group: {config.PAGES_PER_GROUP}  |  Freshness: Last 15 days (jobAge=15)")
    print("=" * 55)

    session_counter = [0]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=config.HEADLESS)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            # Block location permission popup permanently
            permissions=[],
            geolocation=None,
        )
        page = context.new_page()

        login(page)

        for group in config.SEARCH_GROUPS:
            run_search(page, group, session_counter)
            if session_counter[0] >= config.MAX_APPLY_PER_SESSION:
                break

        browser.close()

    print("\n" + "=" * 55)
    print(f"  🎉 Session complete!")
    print(f"  ✅ Auto-applied      : {session_counter[0]} jobs  →  applied_jobs.csv")
    print(f"  🌐 Manual (portal)   : {_count_rows('manual_apply.csv')} jobs  →  manual_apply.csv")
    print(f"  ❓ Manual (questions): {_count_rows('questions_jobs.csv')} jobs  →  questions_jobs.csv")
    print("=" * 55)


if __name__ == "__main__":
    main()