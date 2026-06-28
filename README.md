# 🏙️ Community Hero — Hyperlocal Problem Solver for Kolkata

A full-stack web platform for Kolkata citizens to report, track, and resolve community issues — potholes, water leakages, streetlights, garbage, and more.

---

## 🗂 Project Structure

```
community-hero/
├── app.py                    # ← MAIN ENTRY POINT
├── seed_admin.py             # Run once to create first admin
├── requirements.txt          # Python dependencies
├── render.yaml               # One-click Render deployment
├── Procfile
├── .env.example              # Copy to .env and fill in values
│
├── backend/
│   └── app/
│       ├── main.py           # FastAPI app
│       ├── api/
│       │   ├── auth.py       # Register / Login
│       │   ├── otp.py        # Phone OTP verification + pincodes
│       │   ├── issues.py     # Create, list, upvote, comment
│       │   ├── admin.py      # Admin: status change, proof upload
│       │   └── users.py      # Profile, avatar, my issues
│       ├── core/
│       │   ├── config.py     # Settings from env vars
│       │   └── security.py   # JWT, password hashing
│       ├── db/
│       │   ├── database.py   # PostgreSQL connection
│       │   └── models.py     # All DB models + 80 Kolkata pincodes
│       └── services/
│           └── otp_service.py  # Twilio / MSG91 SMS
│
└── frontend/
    └── src/
        ├── App.jsx           # Router
        ├── api.js            # Axios client
        ├── hooks/useAuth.jsx # Auth context
        └── pages/
            ├── Landing.jsx   # Public landing page
            ├── Login.jsx     # Login
            ├── Register.jsx  # Register + OTP + pincode selector
            ├── Feed.jsx      # News feed (Facebook-style)
            ├── IssueDetail.jsx
            ├── CreateIssue.jsx
            ├── Profile.jsx
            ├── AdminDashboard.jsx    # Police station admin
            └── AdminIssueDetail.jsx  # Resolve with proof upload
```

---

## ⚡ Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL running locally

### 2. Clone & Setup
```bash
cd community-hero
cp .env.example .env
# Edit .env — set DATABASE_URL and optionally SMS credentials
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Build the React frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Seed the first super admin
```bash
python seed_admin.py
# Creates: admin@communityhero.in / Admin@1234
```

### 6. Run the app
```bash
python app.py
# Opens at http://localhost:8000
```

---

## 🚀 Deploy to Render (Recommended)

### Option A — render.yaml (one-click)
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repo — Render reads `render.yaml` automatically
4. Add SMS credentials in the Render dashboard → Environment
5. After deploy, run `python seed_admin.py` in the Render Shell

### Option B — Manual
1. Create a **PostgreSQL** database on Render → copy the connection string
2. Create a **Web Service** → Python → set:
   - Build: `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - Start: `python app.py`
   - Add all env vars from `.env.example`

---

## 👥 User Roles

| Role | What they can do |
|------|-----------------|
| **Citizen** | Register, post issues with photos/video, upvote, comment |
| **Police Admin** | See issues only for their assigned pincode, update status, upload resolution proof |
| **Super Admin** | Everything + create police admins, view all pincodes |

---

## 📱 Key Features

- **80+ Kolkata pincodes** with police station mapping
- **Phone OTP verification** via Twilio or MSG91
- **Facebook-style news feed** — post text, images, videos
- **Issue routing** — auto-assigned to the correct police station by pincode
- **🔴 Pending / 🟡 In Progress / 🟢 Resolved** status with coloured badges
- **Admin proof upload** — police upload photos when resolving
- **Community upvotes** — push urgent issues to top
- **Gamification** — citizens earn points for reporting
- **User profiles** with avatar, bio, stats

---

## 🔑 First Login

After running `seed_admin.py`:

| Field | Value |
|-------|-------|
| Email | `admin@communityhero.in` |
| Password | `Admin@1234` |

Go to `/admin` to create police station admins per pincode.

---

## 📲 SMS Setup

**Dev mode** (no credentials needed): OTP is printed to the console.

**Twilio** (recommended):
1. Sign up at twilio.com → get Account SID, Auth Token, Phone Number
2. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` in `.env`

**MSG91** (Indian provider, cheaper):
1. Sign up at msg91.com → get Auth Key + create OTP template
2. Set `SMS_PROVIDER=msg91`, `MSG91_AUTH_KEY`, `MSG91_TEMPLATE_ID` in `.env`

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Auth | JWT + bcrypt |
| SMS | Twilio / MSG91 |
| Frontend | React 18, React Router, Axios |
| Styling | Vanilla CSS (no framework) |
| Build | Vite |
| Deploy | Render |
