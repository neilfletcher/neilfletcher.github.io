#!/usr/bin/env python3
"""Validate competitions.json and build the calendar (ICS) and RSS feeds.

Usage:
  python3 scripts/build_feeds.py              # validate, prune old events, write feeds
  python3 scripts/build_feeds.py --new-since 2026-11-26   # also list comps added on/after a date

Run from the archery-comps folder. Standard library only.
"""
import argparse
import datetime as dt
import json
import math
import sys
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "competitions.json"
SITE = "https://neilfletcher.github.io/archery-comps/"
REQUIRED = ["id", "name", "host", "date", "town", "county", "lat", "lng",
            "environment", "discipline", "url", "added"]
ENVS = {"indoor", "outdoor"}
DISCIPLINES = {"Target", "Field", "Clout", "3D", "Flight", "Other"}
EM_DASH = "\u2014"
PRUNE_AFTER_DAYS = 14


def drive_mins(home, c):
    if c.get("driveMins"):
        return int(c["driveMins"])
    lat1, lng1, lat2, lng2 = map(math.radians, [home["lat"], home["lng"], c["lat"], c["lng"]])
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    miles = 3958.8 * 2 * math.asin(math.sqrt(a))
    return round(miles * 1.25 / 55 * 60 + 8)


def season(date_str):
    m = int(date_str[5:7])
    return "Winter (indoor season)" if m in (10, 11, 12, 1, 2, 3) else "Summer (outdoor season)"


def validate(doc):
    errors = []
    raw = json.dumps(doc, ensure_ascii=False)
    if EM_DASH in raw:
        errors.append("Em dash found in data: replace with a comma, colon or hyphen.")
    seen = set()
    for c in doc["competitions"]:
        cid = c.get("id", "?")
        for k in REQUIRED:
            if c.get(k) in (None, ""):
                errors.append(f"{cid}: missing {k}")
        if cid in seen:
            errors.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c.get("environment") not in ENVS:
            errors.append(f"{cid}: environment must be indoor or outdoor")
        if c.get("discipline") not in DISCIPLINES:
            errors.append(f"{cid}: discipline must be one of {sorted(DISCIPLINES)}")
        for k in ("date", "endDate", "added"):
            if c.get(k):
                try:
                    dt.date.fromisoformat(c[k])
                except ValueError:
                    errors.append(f"{cid}: {k} is not YYYY-MM-DD")
    return errors


def ics_escape(s):
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode("utf-8")
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b" " + b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)


def describe(c, home):
    bits = [f"Host: {c['host']}",
            f"{c['environment'].title()} {c['discipline'].lower()}, {season(c['date'])}",
            f"Rounds: {', '.join(c.get('rounds') or []) or 'see prospectus'}"]
    if c.get("status"):
        bits.append(f"Record status: {c['status']}")
    if c.get("eligibility"):
        bits.append(f"Eligibility: {c['eligibility']}")
    bits.append(f"About {drive_mins(home, c)} min drive from {home['name']}")
    if c.get("notes"):
        bits.append(c["notes"])
    bits.append(f"Details and entry: {c['url']}")
    return "\n".join(bits)


def build_ics(comps, home, now):
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Comp Finder//Archery comps near Northampton//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Archery comps near Northampton",
             "X-WR-CALDESC:Archery competitions within about an hour of Northampton. Updated weekly.",
             "X-WR-TIMEZONE:Europe/London", "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for c in comps:
        start = dt.date.fromisoformat(c["date"])
        end = dt.date.fromisoformat(c.get("endDate") or c["date"]) + dt.timedelta(days=1)
        loc = ", ".join(x for x in [c.get("venue"), c.get("town"), c.get("county")] if x)
        lines += ["BEGIN:VEVENT",
                  f"UID:{c['id']}@neilfletcher.github.io",
                  f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                  f"SUMMARY:{ics_escape(c['name'] + ' (' + c['town'] + ')')}",
                  f"LOCATION:{ics_escape(loc)}",
                  f"GEO:{c['lat']};{c['lng']}",
                  f"DESCRIPTION:{ics_escape(describe(c, home))}",
                  f"URL:{c['url']}",
                  f"CATEGORIES:{c['environment'].title()},{c['discipline']}",
                  "TRANSP:TRANSPARENT",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def build_rss(comps, home, now):
    items = sorted(comps, key=lambda c: (c["added"], c["date"]), reverse=True)[:50]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', "<channel>",
           "<title>Archery comps near Northampton</title>",
           f"<link>{SITE}</link>",
           f'<atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>',
           "<description>New archery competitions within about an hour of Northampton, checked weekly.</description>",
           "<language>en-gb</language>",
           f"<lastBuildDate>{format_datetime(now)}</lastBuildDate>"]
    for c in items:
        d = dt.date.fromisoformat(c["date"])
        when = d.strftime("%a %-d %b %Y")
        title = f"{when}: {c['name']} ({c['town']}, {c['environment']})"
        added = dt.datetime.combine(dt.date.fromisoformat(c["added"]), dt.time(7, 0), tzinfo=dt.timezone.utc)
        out += ["<item>",
                f"<title>{escape(title)}</title>",
                f"<link>{escape(c['url'])}</link>",
                f'<guid isPermaLink="false">{escape(c["id"])}</guid>',
                f"<pubDate>{format_datetime(added)}</pubDate>",
                f"<description>{escape(describe(c, home)).replace(chr(10), '&lt;br/&gt;')}</description>",
                "</item>"]
    out += ["</channel>", "</rss>"]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new-since", help="list comps added on or after YYYY-MM-DD")
    ap.add_argument("--no-prune", action="store_true")
    args = ap.parse_args()

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(doc)
    if errors:
        print("VALIDATION FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)

    today = dt.date.today()
    home = doc["meta"]["home"]
    if not args.no_prune:
        cutoff = today - dt.timedelta(days=PRUNE_AFTER_DAYS)
        before = len(doc["competitions"])
        doc["competitions"] = [c for c in doc["competitions"]
                               if dt.date.fromisoformat(c.get("endDate") or c["date"]) >= cutoff]
        pruned = before - len(doc["competitions"])
        if pruned:
            print(f"Pruned {pruned} finished competition(s).")
    doc["competitions"].sort(key=lambda c: (c["date"], c["name"]))
    DATA.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    upcoming = [c for c in doc["competitions"]
                if dt.date.fromisoformat(c.get("endDate") or c["date"]) >= today]
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    (ROOT / "competitions.ics").write_text(build_ics(upcoming, home, now), encoding="utf-8", newline="")
    (ROOT / "feed.xml").write_text(build_rss(upcoming, home, now), encoding="utf-8")
    print(f"OK: {len(upcoming)} upcoming competitions; wrote competitions.ics and feed.xml")

    if args.new_since:
        since = dt.date.fromisoformat(args.new_since)
        new = [c for c in upcoming if dt.date.fromisoformat(c["added"]) >= since]
        print(f"\nNEW SINCE {since}: {len(new)}")
        for c in new:
            d = dt.date.fromisoformat(c["date"])
            print(f"- {d:%a %-d %b %Y}: {c['name']}, {c['town']} ({c['county']}). "
                  f"{c['environment'].title()} {c['discipline'].lower()}, about {drive_mins(home, c)} min. {c['url']}")


if __name__ == "__main__":
    main()
