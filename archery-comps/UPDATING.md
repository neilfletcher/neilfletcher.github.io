# Comp Finder: weekly update playbook

Live site: https://neilfletcher.github.io/archery-comps/
Repo: neilfletcher/neilfletcher.github.io, folder `archery-comps/`. Push straight to `main` (no pull requests).

The weekly scheduled task follows these steps. A person can follow them too.

## 1. Find competitions

Goal: every open archery competition (target, field, clout, 3D, flight) from today to about 12 months ahead whose
venue is within 3 hours' drive of Northampton (driveMins <= 180). Roughly: all of the Midlands, East Anglia,
London and the Home Counties, the south coast from Kent to Dorset, Bristol and south Wales to Cardiff and
Llantrisant, north Wales to Rhyl, Cheshire, Lancashire to Preston, and Yorkshire to Leeds and Huddersfield.
Out of range: Scotland, Northern Ireland, Cumbria, the North East, Devon and Cornwall, the Isle of Wight.

The two diaries below cover most of the country in one page each; read them in full every week first, then fill
gaps from the county sites and searches.

Check, at least:
- Archery GB Find a Competition: https://archerygb.org/competitions/find-a-competition (and individual listings at /competitions/find-a-competition/NNNNN)
- Brighton Bowmen Tournament Diary (has a County column): https://www.brightonbowmen.net/tournament-diary/
- HL Outdoors archery diary: https://www.hl-outdoors.co.uk/events/type/indoor/ (and /events/type/outdoor/ if it exists)
- NCAS: https://www.ncasarchery.org.uk/
- Bedfordshire CAA: https://www.archerybeds.com/
- Buckinghamshire AA: https://www.bucksarcheryassociation.org.uk/
- Leicestershire and Rutland CAA, Warwickshire / CWAA, Cambridgeshire AA, EMAS (East Midlands), SCAS (Southern Counties)
- EFAA shoot calendar: https://efaafieldarcher.com/shoot-calendar (mark these "EFAA members only")
- NFAS shoot dates: https://nfas.net/clubs/shoot-dates (mark "NFAS members only")
- Club pages: Archers of Raunds, Targetcraft, Towcester, Kettering Archers, WOAC, Long Buckby, Nene Bowmen, The Foxes, Bowmen of Glen, Kestrels, Clophill, Dunstable Bowmen, Eagle Bowmen of Bedford
- Web searches such as "archery tournament <month> <year> <county>", "Portsmouth tournament <year> <town>", "clout open <year> Northamptonshire"

Skip: university-only leagues (BUCS, TOUCAN), club-internal shoots, online/postal shoots, and anything you can't date.

## 2. Edit `data/competitions.json`

One object per competition. Fields:

| field | notes |
|---|---|
| id | lowercase-hyphenated, unique and stable, e.g. `aor-48th-indoor-2027` |
| name, host | as the organiser writes them |
| date / endDate | `YYYY-MM-DD`; endDate only for multi-day events |
| venue, town, county | venue may say "check the prospectus" if unconfirmed |
| lat, lng | venue coordinates, 4 decimal places |
| approxLocation | `true` if lat/lng is only the town or county (field clubs often don't publish their ground) |
| driveMins | estimated drive from central Northampton (52.2405, -0.9027), rounded to 5. Rule of thumb: road miles = straight-line miles x 1.25, at 45 mph under 30 road miles, 52 mph under 80, 58 mph beyond, plus 8 minutes |
| environment | `indoor` or `outdoor` |
| discipline | `Target`, `Field`, `Clout`, `3D`, `Flight` or `Other` |
| rounds | e.g. `["Portsmouth"]`, `["WA 18m"]`, `["York", "Hereford"]` |
| status | `UKRS`, `WRS` or `""` |
| eligibility | `""` if open to all AGB members, else e.g. `"EFAA members only"`, `"Juniors only"` |
| url | a page that actually shows this comp and how to enter. Check it lists the comp; a club homepage that doesn't mention it is no good. If entry is only via Archery GB, use the AGB listing (find-a-competition/NNNNN if you can find the ID, otherwise https://archerygb.org/competitions/find-a-competition) |
| source | where you found it |
| added | today's date, ONLY for comps not already in the file. Never change `added` on existing entries |
| notes | one or two short, useful sentences, or `""` |

Update existing entries if details changed (date, venue, entry link). Don't duplicate: match on host, date and name.
British English. No em dashes anywhere (the build script rejects them).
Set `meta.lastChecked` to today.

## 3. Build and push

```
cd archery-comps
python3 scripts/build_feeds.py --new-since <today>
git add -A && git commit -m "Comp Finder weekly update <today>" && git push origin main
```

The script validates the data, removes comps that finished more than two weeks ago, regenerates
`competitions.ics` and `feed.xml`, and prints the comps added today for the email.

## 4. Email alerts (Gmail)

Each subscriber picks their own drive-time limit on the site. They sign up by emailing
`neil.fletcher+comps@gmail.com` with subject `Archery comps: subscribe (N min)`, where N is 30 to 180
(or `Archery comps: unsubscribe`). There is no stored list: work it out each week.

1. Gmail search `to:neil.fletcher+comps@gmail.com subject:"Archery comps"` (go back as far as results allow).
2. For each sender, their latest subscribe/unsubscribe message decides whether they're on the list, and the
   number in their latest subscribe subject is their limit. No number means 90.
3. The build script's NEW SINCE list puts `[N min]` at the start of each line. For each distinct limit among
   subscribers, take the new comps with N <= that limit. If there are any, send ONE email for that group:
   - To: neil.fletcher@gmail.com, Bcc: everyone in that group (never put subscribers in To or Cc)
   - Subject: `New archery comps within <limit as e.g. 1 hr 30> of Northampton (<n> found)`
   - Body: a short friendly intro line, the matching comps (date, name, town, indoor/outdoor, drive time, link),
     then the site link and "To change your range, subscribe again from the site. To stop, reply with the
     subject Archery comps: unsubscribe".
4. Any "Archery comps: missing comp" emails: research the comp and add it in step 2.
5. Don't send anything to a group with nothing new in range.

The calendar feeds (`calendars/within-N.ics`) are rebuilt by the script, so calendar subscribers need nothing doing.

## 5. Report

Finish with a short summary: how many comps were added, updated and removed, whether an alert email went out
and to how many people, and any sources that couldn't be reached.
