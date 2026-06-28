# Community Hero — Kolkata

A hyperlocal civic-issue reporting platform scoped to **Kolkata pincodes only**.
Citizens post problems (image/video/text + exact pincode) to a public news
feed; each pincode has exactly one police-station admin login that sees that
pincode's tickets as **Pending** (red) or **Resolved** (green), resolves them
with photo proof, and the reporting citizen earns reward points automatically.

> **Stack note:** your brief mentioned Node.js + React *and* a single
> `app.py`. Those are two different runtimes, so this build picks the Python
> path you explicitly asked for: **Flask (`app.py`) + PostgreSQL + server-rendered
> HTML/CSS/vanilla JS**, deployable as one Render web service. If you actually
> want a separate React/Node frontend talking to a Python API, say so and I'll
> split it into two services — just flag which one wins.

---

## 1. What's built vs. what's a stretch goal

| Brief feature | Status |
|---|---|
| Public registration (name, phone, email, password) | ✅ |
| Pincode dropdown (Kolkata only) on every post | ✅ |
| Image/video/text posting, Facebook-style feed | ✅ |
| One admin per pincode (police station) | ✅ (seed script, see below) |
| Pending (red) / Resolved (green) ticket states | ✅ |
| Resolve with photo proof | ✅ |
| Reward points on resolution | ✅ (flat +10 pts/resolution, see `Config.REWARD_POINTS_PER_RESOLUTION`) |
| Community verification | ✅ simple "I see this too" counter |
| Gamification | ✅ basic top-contributors leaderboard |
| Impact dashboard | ✅ basic pending/resolved counters |
| AI-powered categorisation | ✅ **keyword-based** auto-suggestion (no API key needed) — see "Upgrading to real AI" below |
| Geo-location & mapping, predictive insights | ⛔ not built — these need a maps API key and historical data volume the MVP doesn't have yet. Hooks are noted below so you can add them. |

---

## 2. Project layout

```
community-hero/
├── app.py                 # the one Flask entrypoint — all routes live here
├── config.py              # env-driven configuration
├── extensions.py          # the shared db = SQLAlchemy() instance
├── models.py              # User, PoliceAdmin, Issue, IssueVerification
├── kolkata_data.py        # pincode -> area -> indicative police station list
├── seed.py                # creates tables + one admin account per pincode
├── requirements.txt
├── Procfile                # gunicorn start command (Render/Heroku-style)
├── render.yaml             # Render Blueprint: web service + Postgres in one go
├── .env.example
├── templates/              # Jinja2 HTML (base, index, register, login, dashboard, admin_*)
└── static/
    ├── css/style.css
    ├── js/main.js
    └── uploads/             # uploaded photos/videos land here at runtime
```

## 3. Run it locally

```bash
cd community-hero
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

createdb community_hero   # or use any Postgres instance you have
export DATABASE_URL=postgresql://localhost:5432/community_hero
export SECRET_KEY=dev-secret

python seed.py     # creates tables + one police-admin per pincode
python app.py      # http://localhost:5000
```

`seed.py` writes `admin_credentials.csv` (pincode, police station, username,
password) — open it to log in as any police station. **Don't commit this
file** (it's already in `.gitignore`).

## 4. Deploy on Render

**Easiest path — Blueprint:**
1. Push this folder to a GitHub repo.
2. In Render: **New → Blueprint**, point at the repo. `render.yaml` provisions
   both the Postgres database and the web service, and wires `DATABASE_URL`
   automatically.
3. Once it's live, open the Render **Shell** for the web service and run:
   ```bash
   python seed.py
   ```
   to create the police-admin accounts. Download `admin_credentials.csv` from
   the shell (or print it and copy it — Render's free-tier disk doesn't
   persist between deploys, so grab it before redeploying).

**Manual path:** create a Postgres instance + a Python web service by hand,
set `DATABASE_URL` and `SECRET_KEY` env vars, build command
`pip install -r requirements.txt`, start command `gunicorn app:app`.

### ⚠️ Uploaded media on Render's free tier
Render's free web-service filesystem is **ephemeral** — it's wiped on every
redeploy or restart, so photos/videos saved by `save_media()` in `app.py`
will disappear. For anything beyond a demo, swap `save_media()` for an
upload to S3 / Cloudinary / Google Cloud Storage and store the returned URL
instead of a local filename. That's a single function to change.

## 5. Kolkata pincode + police station data — please verify

`kolkata_data.py` lists ~70 Kolkata pincodes with an area name and an
**indicative** police-station label, so every pincode has exactly one admin
to route tickets to. The area names come from public pincode directories;
the police-station labels are real Kolkata Police station names assigned by
area, but **the exact pincode-to-jurisdiction boundaries have not been
verified against an official source.** Before any real-world use, check and
correct this list against the official Kolkata Police jurisdiction map and
treat the file as a seed, not ground truth. The list also isn't exhaustive
(Kolkata has ~150 postal pincodes) — add any missing ones the same way.

## 6. Upgrading the keyword categoriser to real AI

`suggest_category()` in `app.py` is a simple keyword matcher so the app runs
with zero API keys. To upgrade it to genuine AI-powered categorisation (as
named in the original brief), replace its body with a call to an LLM/vision
API of your choice, e.g.:

```python
def suggest_category(description, location_text=""):
    # Call e.g. the Anthropic or OpenAI API here, pass `description`
    # (and the uploaded image, if you want vision-based classification),
    # ask for one of CATEGORIES back, and return it.
    ...
```

Keep it returning a plain string from `CATEGORIES` and nothing else changes.

## 7. Security notes before going live

- Rotate `SECRET_KEY` and never commit it.
- Add a "change password" flow for admins — they currently can't change the
  password `seed.py` generated for them.
- Add rate limiting / CAPTCHA to `/register` and `/login` to deter abuse.
- Validate phone numbers more strictly than "non-empty" if this goes public.
