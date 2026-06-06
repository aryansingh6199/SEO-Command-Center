"""
fixer.py — logic for generating SEO fixes.
"""
from __future__ import annotations
import difflib

def generate_redirect_map(rows: list[dict]) -> list[dict]:
    """Find closest 200 OK indexable target for each 4xx page."""
    targets = [r["Address"] for r in rows if (r.get("Status Code") or "0") == "200"
               and (r.get("Indexability", "") or "").strip().lower() == "indexable"]

    broken = [r["Address"] for r in rows if "400" <= (r.get("Status Code") or "0") < "500"]

    redirects = []
    for b in broken:
        # Find closest match based on path similarity
        matches = difflib.get_close_matches(b, targets, n=1, cutoff=0.3)
        if matches:
            redirects.append({"from": b, "to": matches[0], "reason": "Closest structural match"})
        else:
            # Fallback to root if no match
            redirects.append({"from": b, "to": "/", "reason": "No close match, redirect to home"})

    return redirects

def generate_content_fixes(rows: list[dict], issues: list[dict]) -> dict:
    """Generate basic fixes for titles and metas using H1 as a seed."""
    fixes = {"titles": [], "metas": [], "redirect_map": []}

    # Create a lookup for H1s
    h1_map = {r["Address"]: (r.get("H1-1", "") or "").strip() for r in rows}

    for issue in issues:
        if issue["type"] in ("missing_title", "title_too_long", "title_too_short"):
            for url in issue["affected_urls"]:
                h1 = h1_map.get(url, "Home Page")
                old = "Missing/Bad"
                new = f"{h1} | SEO Optimized"[:60]
                fixes["titles"].append({"url": url, "old": old, "new": new})

        if issue["type"] in ("missing_meta_description", "meta_description_too_long"):
            for url in issue["affected_urls"]:
                h1 = h1_map.get(url, "Professional SEO Services")
                old = "Missing/Bad"
                new = f"Expert solutions for {h1}. Improve your online visibility with our proven strategies."[:155]
                fixes["metas"].append({"url": url, "old": old, "new": new})

    return fixes
