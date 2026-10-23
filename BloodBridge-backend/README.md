# BloodBridge Backend (FastAPI + Supabase)

High-performance emergency blood donation coordination backend for Pakistan, powered by **FastAPI**, **Supabase (PostgreSQL + Auth)**, and **Geodesic Haversine Proximity Matching**.

---

## 🚀 Quickstart

### 1. Activate the Virtual Environment
The virtual environment is already initialized in `.venv/`:

```bash
cd bloodridge-backend
source .venv/bin/activate
```

*(If you ever need to reinstall dependencies: `pip install -r requirements.txt`)*

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Run the Database Migrations
Go to your **Supabase Dashboard** -> **SQL Editor** -> Click **New Query**.  
Paste the contents of [`sql/schema.sql`](./sql/schema.sql) and click **Run**.  
This creates:
- `profiles`: Blood requesters with phone auth.
- `standby_donors`: Standby donors with GPS coordinates and blood compatibility indexes.
- `blood_requests`: Emergency search cases with status tracking.
- `donor_dispatches`: Real-time WhatsApp dispatch and acceptance audit logs.
- Row Level Security (RLS) policies.

### 4. Start the FastAPI Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 API Endpoints Overview

### 1. Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/signup` | Register requester with Phone & Password |
| `POST` | `/api/v1/auth/login` | Authenticate requester and return session token |

### 2. Blood Requests (`/api/v1/requests`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/requests` | Create emergency blood request, generate Case Reference (e.g. `BB-KHI-4819`), and trigger donor dispatch |
| `GET` | `/api/v1/requests` | List nationwide requests with optional `city` and `status` filters |
| `PATCH` | `/api/v1/requests/{id}/status` | Update case status (`donor_matched`, `fulfilled`, `cancelled`) |

### 3. Standby Donors (`/api/v1/donors`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/donors` | Register voluntary standby donor with live coordinates |
| `GET` | `/api/v1/donors/match` | Find nearest compatible donors by blood group & distance |

### 4. Hospital Blood Banks (`/api/v1/blood-banks`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/blood-banks` | Return verified 24/7 facilities sorted by geodesic proximity (km) |

### 5. WhatsApp Dispatch & Simulation (`/api/v1/whatsapp`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/whatsapp/dispatch-status` | Real-time progress ticker for active dispatches |
| `POST` | `/api/v1/whatsapp/simulate-accept` | Simulates immediate WhatsApp donor acceptance (for UI testing) |
| `POST` | `/api/v1/whatsapp/webhook` | Meta WhatsApp Cloud API incoming webhook receiver |

---

## 🏗️ Project Architecture

```
bloodridge-backend/
├── app/
│   ├── main.py                  # FastAPI initialization & CORS
│   ├── core/
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   └── supabase.py          # Supabase client singleton with fallback mode
│   ├── schemas/
│   │   ├── auth.py              # Auth request & response schemas
│   │   ├── request.py           # Blood request schemas
│   │   └── donor.py             # Standby donor & matching schemas
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Centralized v1 router
│   │       └── endpoints/       # Route handlers
│   └── services/
│       ├── matching.py          # Geodesic Haversine algorithm & blood compatibility matrix
│       └── whatsapp_service.py  # WhatsApp notification template & dispatch
├── sql/
│   └── schema.sql               # Ready-to-run Supabase PostgreSQL schema
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
