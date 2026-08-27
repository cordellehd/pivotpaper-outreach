# PivotPaper Cold Email Outreach System

Automated cold email outreach, follow-up, and reply monitoring system for [PivotPaper](https://pivotpaper.us).

## Files
- `outreach.py` — Sends Email 1 to prospects from prospects.csv
- `followup.py` — Auto follow-ups on Days 3, 7, 14
- `monitor.py` — IMAP reply monitor, notifies on replies
- `templates.py` — 20 email templates across 5 audience segments
- `prospects.csv` — Your lead list (not committed — add locally)

## Setup
```bash
export SMTP_PASSWORD=your_password
python3 outreach.py
python3 followup.py
python3 monitor.py
```

## Cron Schedule
```
0 8 * * 1-5 python3 outreach.py
0 9 * * 1-5 python3 followup.py
*/15 * * * * python3 monitor.py
```

## Segments
- `open_to_work` — Currently job searching
- `career_changer` — Switching industries
- `recent_grad` — New graduate
- `mid_career` — 5-10 years experience
- `laid_off` — Recently laid off

## Notes
- Never commit prospects.csv or outreach.db (contains PII)
- Credentials are read from environment variables only
- Daily limit: 50 emails/day with 30-90s random delays
