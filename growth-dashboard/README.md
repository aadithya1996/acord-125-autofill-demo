# Insurance Growth OS

Next.js + Shadcn UI dashboard for insurance brokerages.
Replaces the Streamlit demo with a professional, scalable frontend.

## Stack

- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind CSS 4
- **UI Library:** Shadcn UI (Radix + Tailwind)
- **Charts:** Recharts
- **Backend API:** Python FastAPI (`../api.py`) for ACORD 125 PDF generation
- **Data:** In-memory mock layer (`lib/data.ts`) — swap for Supabase/Prisma in production

## Pages

| Route | Feature |
|---|---|
| `/` | Dashboard with KPIs, lead pipeline chart, ticket preview, campaign stats |
| `/leads` | Lead pipeline table, intake form, lead detail with status update, ACORD pre-fill |
| `/clients` | Client directory, policy table, 90-day renewal alerts |
| `/tickets` | Inbox with filters, priority badges, one-click resolve, create ticket |
| `/campaigns` | Campaign list, builder with templates & cron, manual execution, recipient log |
| `/acord` | JSON editor with 3 scenarios, generate & download filled ACORD 125 PDF |

## Quick Start

### 1. Start the Python API (for ACORD generation)

```bash
cd ..
python3 api.py
```

This runs on `http://localhost:8000`.

### 2. Start the Next.js app

```bash
npm install
npm run build
npm run start
```

Open **http://localhost:3000**

## Dev Mode

```bash
npm run dev
```

## Production Deployment

### Vercel (Frontend)

1. Push this repo to GitHub
2. Import in Vercel with **Root Directory** = `growth-dashboard`
3. Deploy

### Python API (Railway / Render / EC2)

Deploy `api.py` with the parent directory as the working directory so it can import `field_mapper.py` and `pdf_filler.py`.

Environment variables:
- None required for demo; add `SUPABASE_URL` + `SUPABASE_KEY` when connecting real data

## Data Model

| Entity | Purpose |
|---|---|
| `Lead` | Quote pipeline |
| `Client` | Bound accounts |
| `Policy` | Active policies with premiums & expiration |
| `Ticket` | Service queue (endorsement, renewal, claim, cross-sell, etc.) |
| `Campaign` | Mass outreach with templates & scheduling |
| `CampaignRecipient` | Individual send tracking |

## Campaign Variables

Templates support `{{name}}`, `{{business_name}}`, `{{carrier}}`, `{{policy_number}}`, `{{lob}}`, `{{premium}}`, `{{expiration_date}}`, `{{firm_name}}`, `{{firm_phone}}`.

## Screenshots

*(Add screenshots after first deploy)*
