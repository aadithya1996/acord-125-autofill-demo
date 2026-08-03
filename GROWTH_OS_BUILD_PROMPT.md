# Insurance Growth OS — Complete Build Prompt

Copy and paste the following into Claude, ChatGPT, or any AI code generator. It contains the full specification for building the Insurance Growth OS as a Next.js + Shadcn UI application.

---

## PROJECT OVERVIEW

Build an **Insurance Brokerage Growth OS** — a modern, dark-themed SaaS dashboard that helps insurance brokerages manage leads, clients, policies, service tickets, marketing campaigns, and ACORD 125 form automation.

**Tech Stack:**
- Next.js 16 + React 19 + TypeScript
- Tailwind CSS 4
- Shadcn UI (Radix primitives + Tailwind)
- Recharts for analytics
- Lucide React for icons
- In-memory mock data layer (easily swappable for Supabase/Prisma)

**Theme:** Dark mode professional SaaS. Primary palette: slate, emerald, and amber accents. Think "Linear meets Salesforce."

---

## DESIGN SYSTEM / AESTHETICS

### Color Palette
- **Background:** `#0f172a` (slate-950) — deep navy-black
- **Surface:** `#1e293b` (slate-900) — card backgrounds
- **Elevated:** `#334155` (slate-800) — hover states, borders
- **Primary:** `#10b981` (emerald-500) — CTAs, active states, success
- **Primary Hover:** `#059669` (emerald-600)
- **Secondary:** `#3b82f6` (blue-500) — info, links
- **Accent:** `#f59e0b` (amber-500) — warnings, pending states
- **Danger:** `#ef4444` (red-500) — errors, urgent tickets
- **Text Primary:** `#f8fafc` (slate-50) — headings
- **Text Secondary:** `#94a3b8` (slate-400) — body, labels
- **Text Muted:** `#64748b` (slate-500) — timestamps, meta

### Typography
- **Font:** Inter (Google Fonts)
- **Headings:** 600 weight, tight tracking (-0.02em)
- **Body:** 400 weight, 1.5 line-height
- **Mono:** JetBrains Mono or SF Mono for data/code blocks

### Spacing & Shape
- **Border Radius:** 12px for cards, 8px for buttons/inputs, 9999px for badges
- **Shadows:** `0 4px 6px -1px rgba(0,0,0,0.3)` for cards
- **Border:** 1px solid `rgba(148,163,184,0.1)` — barely visible glass borders
- **Transitions:** 150ms ease for all interactive elements

### Layout
- **Sidebar:** 260px fixed, collapsible on mobile, glassmorphism effect
- **Main Content:** max-width 1440px, centered, 24px padding
- **Grid:** 12-column, 16px gap

### Iconography
- Use **Lucide React** exclusively
- All icons: 20px default, stroke-width 1.5
- Status icons with color coding:
  - Success: CircleCheck (emerald)
  - Warning: TriangleAlert (amber)
  - Error: CircleX (red)
  - Info: Info (blue)

### Animation Specs
- **Page transitions:** 200ms fade + 8px translateY slide-up
- **Card hover:** translateY -2px + shadow increase
- **Button hover:** brightness 110% + scale 1.02
- **Modal/dialog:** 150ms scale from 0.95 + opacity fade
- **Toast notifications:** Slide in from right, 300ms, auto-dismiss 4s
- **Skeleton loaders:** Shimmer gradient animation, slate-800 to slate-700

---

## DATA MODEL

Define these TypeScript types in `lib/types.ts`:

```typescript
export type LeadStatus = "new" | "qualified" | "quoted" | "bound" | "lost"
export type LeadSource = "website" | "referral" | "cold_call" | "event" | "other"
export type TicketStatus = "open" | "in_progress" | "resolved" | "closed"
export type TicketPriority = "low" | "medium" | "high" | "urgent"
export type TicketType = "endorsement" | "renewal" | "claim" | "cross_sell" | "service" | "new_business" | "underwriting"
export type InboxType = "sales" | "underwriting" | "service" | "claims"
export type CampaignStatus = "draft" | "scheduled" | "running" | "completed" | "paused"
export type CampaignType = "renewal_reminder" | "cross_sell" | "quote_follow_up" | "welcome" | "seasonal" | "custom"
export type PolicyStatus = "active" | "pending" | "cancelled" | "expired" | "renewed"
export type LOB = "general_liability" | "commercial_property" | "business_owners" | "cyber_and_privacy" | "umbrella" | "workers_comp" | "auto" | "other"

export interface Lead {
  id: number; name: string; email: string; phone: string; business_name: string;
  business_type: string; sic_code: string; naics_code: string; status: LeadStatus;
  source: LeadSource; notes: string; assigned_to: string; created_at: string;
}

export interface Client {
  id: number; name: string; email: string; phone: string; business_name: string;
  fein: string; address: string; city: string; state: string; zip: string;
  legal_entity: string; created_at: string;
}

export interface Policy {
  id: number; client_id: number; carrier: string; policy_number: string;
  line_of_business: LOB; premium: number; effective_date: string;
  expiration_date: string; status: PolicyStatus;
}

export interface Ticket {
  id: number; title: string; type: TicketType; status: TicketStatus;
  priority: TicketPriority; summary: string; assigned_inbox: InboxType;
  assigned_to: string; client_id?: number; lead_id?: number;
  created_at: string; resolved_at?: string;
}

export interface Campaign {
  id: number; name: string; type: CampaignType; status: CampaignStatus;
  channel: "email" | "sms"; template_subject: string; template_body: string;
  audience_filter: string; schedule_type: "immediate" | "one_time" | "recurring";
  schedule_time?: string; cron_expression?: string; last_run_at?: string; created_at: string;
}

export interface CampaignRecipient {
  id: number; campaign_id: number; lead_id?: number; client_id?: number;
  status: "pending" | "sent" | "opened" | "clicked" | "failed";
  error_message?: string; sent_at?: string;
}
```

---

## SAMPLE DATA (Seed)

Seed with exactly this data in `lib/data.ts`:

**3 Leads:**
1. David Chen / Nexus Data Systems (Office) / quoted / Cyber+GL+Property / assigned Alice Nguyen
2. Maria Santos / Savannah Bistro Group (Restaurant) / qualified / GL+Property+BOP / assigned Carlos Rivera
3. Robert Kim / Lakeside Construction Partners (Contractor) / new / Commercial construction / assigned James O'Brien

**2 Clients + 5 Policies:**
1. James Porter / Porter Logistics (NY) — GL $12,500, Property $8,400, Cyber $22,000 (all Hartford/Liberty, active)
2. Sarah Mitchell / Mitchell Retail Group (IL) — BOP $6,500, Umbrella $3,200 (Zurich/Travelers, active)

**4 Tickets:**
1. GL Endorsement — Additional Insured / endorsement / open / high / underwriting
2. Renewal — Nexus Data Cyber Policy / renewal / in_progress / medium / sales
3. Quote Follow-up — Lakeside Construction / new_business / open / medium / sales
4. Cross-sell Opportunity — Umbrella for Porter Logistics / cross_sell / open / low / sales

**3 Campaigns:**
1. Q1 Renewal Reminders / renewal_reminder / scheduled / email / cron: `0 9 1 * *`
2. Quote Follow-up Sequence / quote_follow_up / draft / email / cron: `0 10 * * 1,3,5`
3. Welcome New Clients / welcome / scheduled / email / cron: `0 14 * * *`

---

## PAGE SPECIFICATIONS

### 1. Dashboard (`/`)
- **Hero row:** 4 KPI cards in a grid
  - Total Premium (large currency format, emerald accent)
  - Active Policies (blue accent)
  - Clients (violet accent)
  - Open Tickets (amber accent, show urgent sub-count)
- **Middle section:** 2-column layout
  - Left (2/3): Lead Pipeline bar chart (Recharts, 5 stages)
  - Right (1/3): Ticket Inbox preview (top 5 tickets, priority color-coded badges)
- **Bottom row:** 3 metric cards
  - Running Campaigns | Renewals (90d) | Emails Sent
- **Top right CTA:** "Run Pending Campaigns" button (primary emerald)

### 2. Leads & Intake (`/leads`)
- **Tabs:** Pipeline | Lead Detail
- **Pipeline tab:** Full-width data table with columns: Name, Business, Type, Status (badge), Source, Assigned, Phone
  - Row click selects lead
  - Top-right: "Add Lead" button → opens Dialog with form
- **Lead Form fields:** Name, Email, Phone, Business Name, Business Type (select), SIC Code, NAICS Code, Lead Source (select), Assigned To, Notes
  - On submit: create lead + auto-create ticket + show toast
- **Lead Detail tab:** Show selected lead info card
  - Status dropdown + Update button
  - "Pre-fill ACORD 125" button → navigates to `/acord?payload=...`

### 3. Clients & Policies (`/clients`)
- **Tabs:** Clients | Policies | Renewals
- **Clients tab:** Table with Name, Business, Email, Phone, State, Policy Count
- **Policies tab:** Table with Client, Carrier, Policy #, LOB (badge), Premium (currency), Effective, Expires, Status (badge)
- **Renewals tab:** Card list showing policies expiring in 90 days
  - Each card: Client name, Carrier, LOB, Expiration date, Days remaining badge (red if ≤30, amber if ≤60, else default)

### 4. Tickets / Inbox (`/tickets`)
- **Filters:** Inbox dropdown (All/Sales/Underwriting/Service/Claims) + Status checkboxes
- **Ticket cards:** Full-width cards, not table rows
  - Left: Priority emoji indicator + Title + Type badge + Status badge
  - Middle: Inbox + Assignee + Summary text
  - Right: "Resolve" button (only for open/in_progress)
- **Bottom:** "Create Ticket" card with form: Title, Type (select), Priority (select), Inbox (select), Assigned To, Summary

### 5. Campaigns (`/campaigns`)
- **Tabs:** All Campaigns | Build Campaign | Run & Monitor
- **All Campaigns:** List of campaign cards
  - Each: Name + Status badge + Type badge + Channel badge + Schedule info
  - Actions: Activate (if draft) / Pause (if running)
- **Build Campaign:** Form card
  - Name, Type (select), Channel (select), Schedule (select)
  - If recurring: Cron expression input with helper text
  - Subject, Body textarea (placeholder showing available `{{vars}}`)
  - Audience Filter JSON textarea
  - Submit creates campaign
- **Run & Monitor:**
  - Campaign selector dropdown + "Run Now" button
  - Recipient activity table: Campaign, Status (badge), Sent At, Error

### 6. ACORD 125 Filler (`/acord`)
- **Left (1/2):** JSON editor (textarea, monospace, 24 rows)
  - 3 scenario buttons above: Tech Startup | Restaurant | Construction
  - If `?payload=` in URL, merge it with base scenario
- **Right (1/2):** Actions card
  - "Generate PDF" button (primary)
  - If PDF generated: "Download PDF" button (secondary outline)
- **Below:** Quick Reference card listing valid enum values

---

## COMPONENT INVENTORY

Install these shadcn components:
- button, card, dialog, input, label, textarea, select, badge, table, tabs, checkbox, scroll-area, separator, sonner (toast), sheet, avatar

Also install:
- `recharts` for charts
- `lucide-react` for icons
- `date-fns` for date formatting

---

## SHARED COMPONENTS

### Sidebar (`components/sidebar.tsx`)
- Fixed 260px width, full height
- Top: Logo icon (Shield) + "Growth OS" + "Insurance Brokerage" subtitle
- Nav items with icon + label: Dashboard, Leads, Clients, Tickets, Campaigns, ACORD 125
- Active state: `bg-slate-800 text-white`
- Inactive: `text-slate-400 hover:text-white hover:bg-slate-800/50`
- Bottom: Firm name + version

### Layout (`app/layout.tsx`)
- Dark background `bg-slate-950`
- Inter font
- Toast provider (Sonner)
- Flex layout: Sidebar + Main (flex-1, overflow-y-auto, p-6)

---

## ACORD 125 INTEGRATION

The ACORD page needs a **Python backend** to generate PDFs. Provide this architecture:

**Frontend:** Next.js API Route `app/api/generate-acord/route.ts`
- POST accepts JSON, forwards to Python backend at `http://localhost:8000/generate-acord`
- Returns PDF blob

**Backend:** FastAPI (`api.py` in parent directory)
- POST `/generate-acord` accepts JSON, validates with Pydantic
- Uses `pypdf` to fill `Acord125CommInsApp (1).pdf` template
- Returns `StreamingResponse` with PDF

**PDF Field Mapping Logic:**
- Text fields: direct string values
- Checkbox fields: use PDF NameObject `/1` for checked, `/Off` for unchecked
- Key mappings:
  - `producer.full_name` → `F[0].P1[0].Producer_FullName_A[0]`
  - `policy.status` → status checkboxes (Quote/Issue/Renew/Bound/Change/Cancel)
  - `named_insured.full_name` → `F[0].P1[0].NamedInsured_FullName_A[0]`
  - `lines_of_business.general_liability.selected` + `.premium` → checkbox + premium field
  - `named_insured.legal_entity` → entity checkboxes (Corporation/LLC/etc.)
  - `business_type.type` → business type checkboxes (Office/Restaurant/etc.)

---

## FILE STRUCTURE

```
growth-dashboard/
├── app/
│   ├── layout.tsx
│   ├── globals.css
│   ├── page.tsx              (Dashboard)
│   ├── leads/page.tsx
│   ├── clients/page.tsx
│   ├── tickets/page.tsx
│   ├── campaigns/page.tsx
│   ├── acord/page.tsx
│   └── api/generate-acord/route.ts
├── components/
│   ├── sidebar.tsx
│   └── ui/                   (shadcn components)
├── lib/
│   ├── utils.ts              (cn helper)
│   ├── types.ts              (all interfaces)
│   ├── data.ts               (mock DB + CRUD functions)
│   └── format.ts             (currency, date formatters)
├── public/
│   └── (empty)
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

Parent directory (for Python backend):
```
Acord_pdf_1001/
├── api.py                    (FastAPI wrapper)
├── field_mapper.py           (JSON → PDF field mapping)
├── pdf_filler.py             (pypdf read/write)
├── schemas.py                (Pydantic models)
├── Acord125CommInsApp (1).pdf (template)
└── sample_data/              (3 JSON scenarios)
```

---

## CRITICAL IMPLEMENTATION NOTES

1. **All data is in-memory** for demo. Export mock DB functions from `lib/data.ts` that mutate arrays and return new references to trigger React re-renders.

2. **ACORD 125 page uses `useSearchParams`** to read `?payload=` from lead navigation. Wrap in `<Suspense>` boundary.

3. **Charts** use Recharts `ResponsiveContainer` with fixed height (240px). Color: `#3b82f6` (blue-500).

4. **Badge variants:**
   - Status: `default` (blue), `secondary` (gray), `outline` (subtle)
   - Priority: `default` for high, `secondary` for medium/low, `destructive` for urgent
   - Custom colors via className overrides: `bg-emerald-100 text-emerald-800`, etc.

5. **Form validation:** Use native HTML `required` + type attributes. No complex validation library needed for demo.

6. **Currency formatting:** Use `Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })`

7. **Date formatting:** Use `date-fns` `differenceInDays` for renewal countdowns.

8. **Ticket cards:** Use emoji priority indicators (🟢🟡🟠🔴) for quick visual scanning.

9. **Campaign templates:** Support variable substitution with simple regex: `/\{\{(\w+)\}\}/g`. Replace with context values.

10. **Responsive:** Sidebar collapses to hamburger on mobile. Tables scroll horizontally on small screens.

---

## COPY THIS PROMPT

Paste everything above from "## PROJECT OVERVIEW" through "## CRITICAL IMPLEMENTATION NOTES" into Claude. Then say:

> "Build this entire application. Start by creating the file structure, then implement each page in order: Dashboard → Leads → Clients → Tickets → Campaigns → ACORD. Use the exact color palette, spacing, and component specifications. Seed with the provided sample data. Make sure the ACORD page can communicate with the Python backend."

---

## AESTHETIC SUMMARY (For Designers)

| Element | Specification |
|---|---|
| **Vibe** | Dark, premium, fintech SaaS — trustworthy and high-conversion |
| **Mood** | Linear + Salesforce + Notion hybrid |
| **Lighting** | Subtle, no harsh whites. Cards float on dark canvas |
| **Depth** | 1px borders + soft shadows, not heavy drop shadows |
| **Motion** | Snappy 150ms, purposeful, no bloat |
| **Data density** | High — tables are information-rich but breathable |
| **Color psychology** | Emerald = growth/success, Blue = trust/action, Amber = attention/urgency |
| **Accessibility** | WCAG AA compliant — all text 4.5:1 contrast minimum |
