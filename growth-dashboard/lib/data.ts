"use client"

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
  id: number
  name: string
  email: string
  phone: string
  business_name: string
  business_type: string
  sic_code: string
  naics_code: string
  status: LeadStatus
  source: LeadSource
  notes: string
  assigned_to: string
  created_at: string
}

export interface Client {
  id: number
  name: string
  email: string
  phone: string
  business_name: string
  fein: string
  address: string
  city: string
  state: string
  zip: string
  legal_entity: string
  created_at: string
}

export interface Policy {
  id: number
  client_id: number
  carrier: string
  policy_number: string
  line_of_business: LOB
  premium: number
  effective_date: string
  expiration_date: string
  status: PolicyStatus
}

export interface Ticket {
  id: number
  title: string
  type: TicketType
  status: TicketStatus
  priority: TicketPriority
  summary: string
  assigned_inbox: InboxType
  assigned_to: string
  client_id?: number
  lead_id?: number
  created_at: string
  resolved_at?: string
}

export interface Campaign {
  id: number
  name: string
  type: CampaignType
  status: CampaignStatus
  channel: "email" | "sms"
  template_subject: string
  template_body: string
  audience_filter: string
  schedule_type: "immediate" | "one_time" | "recurring"
  schedule_time?: string
  cron_expression?: string
  last_run_at?: string
  created_at: string
}

export interface CampaignRecipient {
  id: number
  campaign_id: number
  lead_id?: number
  client_id?: number
  status: "pending" | "sent" | "opened" | "clicked" | "failed"
  error_message?: string
  sent_at?: string
}

// ---------------------------------------------------------------------------
// Demo Data
// ---------------------------------------------------------------------------

let leads: Lead[] = [
  { id: 1, name: "David Chen", email: "d.chen@nexusdata.io", phone: "(415) 555-0300", business_name: "Nexus Data Systems, Inc.", business_type: "Office", sic_code: "7372", naics_code: "541512", status: "quoted", source: "website", notes: "Cyber + GL + Property quote. High cyber premium.", assigned_to: "Alice Nguyen", created_at: "2026-01-10" },
  { id: 2, name: "Maria Santos", email: "msantos@savbistro.com", phone: "(404) 555-0299", business_name: "Savannah Bistro Group, LLC", business_type: "Restaurant", sic_code: "5812", naics_code: "722511", status: "qualified", source: "referral", notes: "Restaurant chain, needs GL + Property + BOP. 42 employees.", assigned_to: "Carlos Rivera", created_at: "2026-01-12" },
  { id: 3, name: "Robert Kim", email: "r.kim@lakesidebuild.com", phone: "(312) 555-0456", business_name: "Lakeside Construction Partners, LLC", business_type: "Contractor", sic_code: "1541", naics_code: "236220", status: "new", source: "cold_call", notes: "Commercial construction. 120 employees. $32M revenue.", assigned_to: "James O'Brien", created_at: "2026-01-15" },
]

let clients: Client[] = [
  { id: 1, name: "James Porter", email: "j.porter@porterlogistics.com", phone: "(212) 555-0199", business_name: "Porter Logistics, Inc.", fein: "12-3456789", address: "450 W 33rd St", city: "New York", state: "NY", zip: "10001", legal_entity: "Corporation", created_at: "2025-06-01" },
  { id: 2, name: "Sarah Mitchell", email: "s.mitchell@mitchellretail.com", phone: "(312) 555-0288", business_name: "Mitchell Retail Group, LLC", fein: "98-7654321", address: "842 N Michigan Ave", city: "Chicago", state: "IL", zip: "60611", legal_entity: "LLC", created_at: "2025-08-15" },
]

let policies: Policy[] = [
  { id: 1, client_id: 1, carrier: "Hartford", policy_number: "GL-2025-88421", line_of_business: "general_liability", premium: 12500, effective_date: "2025-01-15", expiration_date: "2026-01-15", status: "active" },
  { id: 2, client_id: 1, carrier: "Hartford", policy_number: "CP-2025-88422", line_of_business: "commercial_property", premium: 8400, effective_date: "2025-01-15", expiration_date: "2026-01-15", status: "active" },
  { id: 3, client_id: 1, carrier: "Liberty Mutual", policy_number: "CY-2025-11223", line_of_business: "cyber_and_privacy", premium: 22000, effective_date: "2025-03-01", expiration_date: "2026-03-01", status: "active" },
  { id: 4, client_id: 2, carrier: "Zurich", policy_number: "ZN-BOP-77210", line_of_business: "business_owners", premium: 6500, effective_date: "2025-06-01", expiration_date: "2026-06-01", status: "active" },
  { id: 5, client_id: 2, carrier: "Travelers", policy_number: "TR-UMB-99543", line_of_business: "umbrella", premium: 3200, effective_date: "2025-06-01", expiration_date: "2026-06-01", status: "active" },
]

let tickets: Ticket[] = [
  { id: 1, title: "GL Endorsement — Additional Insured", type: "endorsement", status: "open", priority: "high", summary: "Client needs vendor added as AI on GL policy before Monday.", assigned_inbox: "underwriting", assigned_to: "Underwriting Team", created_at: "2026-01-14" },
  { id: 2, title: "Renewal — Nexus Data Cyber Policy", type: "renewal", status: "in_progress", priority: "medium", summary: "Cyber renewal expiring 03/01. Premium increased 15%.", assigned_inbox: "sales", assigned_to: "Alice Nguyen", client_id: 1, created_at: "2026-01-13" },
  { id: 3, title: "Quote Follow-up — Lakeside Construction", type: "new_business", status: "open", priority: "medium", summary: "No response after initial GL quote sent 3 days ago.", assigned_inbox: "sales", assigned_to: "James O'Brien", lead_id: 3, created_at: "2026-01-16" },
  { id: 4, title: "Cross-sell Opportunity — Umbrella for Porter Logistics", type: "cross_sell", status: "open", priority: "low", summary: "Client has GL + Property + Cyber but no Umbrella. $2M revenue.", assigned_inbox: "sales", assigned_to: "Alice Nguyen", client_id: 1, created_at: "2026-01-10" },
]

let campaigns: Campaign[] = [
  { id: 1, name: "Q1 Renewal Reminders", type: "renewal_reminder", status: "scheduled", channel: "email", template_subject: "Your policy renews soon — let's review", template_body: "Hi {{name}},\n\nYour {{lob}} policy ({{policy_number}}) with {{carrier}} expires on {{expiration_date}}. Let's schedule a 10-minute review to confirm coverage and explore any changes.\n\nReply or call us at {{firm_phone}}.\n\nBest,\n{{firm_name}}", audience_filter: '{"status":"active","days_before_expiration":30}', schedule_type: "recurring", cron_expression: "0 9 1 * *", created_at: "2026-01-01" },
  { id: 2, name: "Quote Follow-up Sequence", type: "quote_follow_up", status: "draft", channel: "email", template_subject: "Following up on your insurance quote", template_body: "Hi {{name}},\n\nWe sent you a quote for {{business_name}} a few days ago. Do you have any questions, or is there anything we can adjust to better fit your needs?\n\nBest,\n{{firm_name}}", audience_filter: '{"status":"quoted","days_since_quote":3}', schedule_type: "recurring", cron_expression: "0 10 * * 1,3,5", created_at: "2026-01-05" },
  { id: 3, name: "Welcome New Clients", type: "welcome", status: "scheduled", channel: "email", template_subject: "Welcome to {{firm_name}}!", template_body: "Hi {{name}},\n\nThank you for trusting {{firm_name}} with {{business_name}}. Your policies are active and your certificates are attached.\n\nYour account manager is {{assigned_to}}.\n\nBest,\n{{firm_name}}", audience_filter: '{"status":"bound","days_since_bound":1}', schedule_type: "recurring", cron_expression: "0 14 * * *", created_at: "2026-01-08" },
]

let recipients: CampaignRecipient[] = []

let nextId = 100

function genId() {
  return nextId++
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export function getLeads(): Lead[] {
  return [...leads].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
}

export function addLead(lead: Omit<Lead, "id" | "created_at">): Lead {
  const newLead: Lead = { ...lead, id: genId(), created_at: new Date().toISOString().split("T")[0] }
  leads = [...leads, newLead]
  // Auto-create ticket
  addTicket({
    title: `New lead: ${lead.business_name || lead.name}`,
    type: "new_business",
    status: "open",
    priority: "medium",
    summary: lead.notes || `Auto-generated from lead: ${lead.name}`,
    assigned_inbox: "sales",
    assigned_to: lead.assigned_to || "Unassigned",
    lead_id: newLead.id,
  })
  return newLead
}

export function updateLeadStatus(id: number, status: LeadStatus) {
  leads = leads.map((l) => (l.id === id ? { ...l, status } : l))
}

export function getClients(): Client[] {
  return clients
}

export function getPolicies(): Policy[] {
  return policies
}

export function getClientPolicies(clientId: number): Policy[] {
  return policies.filter((p) => p.client_id === clientId)
}

export function getTickets(filters?: { status?: TicketStatus[]; inbox?: InboxType }): Ticket[] {
  let result = [...tickets]
  if (filters?.status?.length) {
    result = result.filter((t) => filters.status!.includes(t.status))
  }
  if (filters?.inbox) {
    result = result.filter((t) => t.assigned_inbox === filters.inbox)
  }
  return result.sort((a, b) => {
    const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 }
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
}

export function addTicket(ticket: Omit<Ticket, "id" | "created_at">): Ticket {
  const newTicket: Ticket = { ...ticket, id: genId(), created_at: new Date().toISOString().split("T")[0] }
  tickets = [...tickets, newTicket]
  return newTicket
}

export function resolveTicket(id: number) {
  tickets = tickets.map((t) => (t.id === id ? { ...t, status: "resolved" as TicketStatus, resolved_at: new Date().toISOString() } : t))
}

export function getCampaigns(): Campaign[] {
  return campaigns.sort((a, b) => b.id - a.id)
}

export function addCampaign(campaign: Omit<Campaign, "id" | "created_at">): Campaign {
  const newCampaign: Campaign = { ...campaign, id: genId(), created_at: new Date().toISOString().split("T")[0] }
  campaigns = [...campaigns, newCampaign]
  return newCampaign
}

export function updateCampaignStatus(id: number, status: CampaignStatus) {
  campaigns = campaigns.map((c) => (c.id === id ? { ...c, status } : c))
}

export function getRecipients(): CampaignRecipient[] {
  return recipients.sort((a, b) => (b.sent_at || "").localeCompare(a.sent_at || ""))
}

export function runCampaign(id: number) {
  const campaign = campaigns.find((c) => c.id === id)
  if (!campaign) return { queued: 0, sent: 0, failed: 0 }

  // Build recipients from leads/clients based on audience filter
  const newRecipients: CampaignRecipient[] = []
  // Demo: send to all leads + all clients
  ;[...leads, ...clients].forEach((entity, i) => {
    const isLead = "status" in entity
    newRecipients.push({
      id: genId(),
      campaign_id: id,
      lead_id: isLead ? entity.id : undefined,
      client_id: isLead ? undefined : entity.id,
      status: "sent",
      sent_at: new Date().toISOString(),
    })
  })

  recipients = [...recipients, ...newRecipients]
  campaigns = campaigns.map((c) => (c.id === id ? { ...c, last_run_at: new Date().toISOString() } : c))

  return { queued: newRecipients.length, sent: newRecipients.length, failed: 0 }
}

// ---------------------------------------------------------------------------
// Metrics
// ---------------------------------------------------------------------------

export function getMetrics() {
  const totalPremium = policies.filter((p) => p.status === "active").reduce((sum, p) => sum + p.premium, 0)
  const activePolicies = policies.filter((p) => p.status === "active").length
  const openTickets = tickets.filter((t) => t.status === "open" || t.status === "in_progress").length
  const urgentTickets = tickets.filter((t) => (t.status === "open" || t.status === "in_progress") && t.priority === "urgent").length
  const upcomingRenewals = policies.filter((p) => {
    if (p.status !== "active") return false
    const days = Math.ceil((new Date(p.expiration_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    return days <= 90 && days >= 0
  }).length

  return {
    totalPremium,
    activePolicies,
    clientCount: clients.length,
    leadCount: leads.length,
    openTickets,
    urgentTickets,
    upcomingRenewals,
    runningCampaigns: campaigns.filter((c) => c.status === "scheduled" || c.status === "running").length,
    emailsSent: recipients.filter((r) => r.status === "sent").length,
  }
}
