# Comp Finder: weekly update playbook

Live site: https://neilfletcher.github.io/archery-comps/
Repo: neilfletcher/neilfletcher.github.io, folder `archery-comps/`. Push straight to `main` (no pull requests).

The weekly scheduled task follows these steps. A person can follow them too.

## 1. Find competitions

Goal: every archery competition (target, field, clout, 3D, flight) from today to about 12 months ahead whose
venue is within roughly 75 minutes' drive of Northampton. That covers Northamptonshire, Bedfordshire,
Leicestershire and Rutland, Buckinghamshire (Milton Keynes and the north), Warwickshire and Coventry,
Cambridgeshire (Cambridge, Huntingdon, Peterborough), north Hertfordshire, and the edges of Oxfordshire.

Check, at least:
- Archery GB Find a Competition: https://archerygb.org/competitions/find-a-competition (and individual listings at /competitions/find-a-competition/NNNNN)
- Brighton Bowmen Tournament Diary (has a County column): https://www.brightonbowmen.net/tournament-diary/
- HL Outdoors archery diary: https://www.hl-outdoors.co.uk/events/type/indoor/ (and the outdoor equivalent)
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
| driveMins | estimated drive from central Northampton (52.2405, -0.9027) |
| environment | `indoor` or `outdoor` |
| discipline | `Target`, `Field`, `Clout`, `3D`, `Flight` or `Other` |
| rounds | e.g. `["Portsmouth"]`, `["WA 18m"]`, `["York", "Hereford"]` |
| status | `UKRS`, `WRS` or `""` |
| eligibility | `""` if open to all AGB members, else e.g. `"EFAA members only"`, `"Juniors only"` |
| url | the best page for details and entry |
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

Subscribers sign up by emailing `neil.fletcher+comps@gmail.com` with subject "Archery comps: subscribe"
(or "unsubscribe"). There is no stored list: work it out each week.

1. Gmail search `to:neil.fletcher+comps@gmail.com subject:"Archery comps"` (go back as far as results allow).
2. For each sender, their latest subscribe/unsubscribe message decides whether they're on the list.
3. If at least one comp was added today and there is at least one subscriber, send ONE email from Neil's Gmail:
   - To: neil.fletcher@gmail.com, Bcc: all subscribers (never put subscribers in To or Cc)
   - Subject: `New archery comps near Northampton (<n> found)`
   - Body: a short friendly intro line, the list printed by the build script (date, name, town, indoor/outdoor,
     drive time, link), then the site link and "To stop these, reply with the subject Archery comps: unsubscribe".
4. Any "Archery comps: missing comp" emails: research the comp and add it in step 2.
5. Don't send anything if nothing new was found.

## 5. Report

Finish with a short summary: how many comps were added, updated and removed, whether an alert email went out
and to how many people, and any sources that couldn't be reached.
