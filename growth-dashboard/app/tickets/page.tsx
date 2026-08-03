"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { getTickets, resolveTicket, addTicket, type Ticket, type TicketStatus, type TicketPriority, type TicketType, type InboxType } from "@/lib/data"
import { toast } from "sonner"
import { CheckCircle2, Plus } from "lucide-react"

const priorityEmoji: Record<TicketPriority, string> = {
  low: "🟢",
  medium: "🟡",
  high: "🟠",
  urgent: "🔴",
}

export default function TicketsPage() {
  const [inboxFilter, setInboxFilter] = useState<InboxType | "all">("all")
  const [statusFilter, setStatusFilter] = useState<TicketStatus[]>(["open", "in_progress"])
  const [tickets, setTickets] = useState<Ticket[]>(() => getTickets({ inbox: inboxFilter === "all" ? undefined : inboxFilter, status: statusFilter }))

  const refresh = () => {
    setTickets(getTickets({ inbox: inboxFilter === "all" ? undefined : inboxFilter, status: statusFilter }))
  }

  const inboxes: (InboxType | "all")[] = ["all", "sales", "underwriting", "service", "claims"]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Tickets / Inbox</h1>
        <div className="flex items-center gap-2">
          <Select value={inboxFilter} onValueChange={(v: any) => { setInboxFilter(v); refresh() }}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {inboxes.map((i) => (
                <SelectItem key={i} value={i}>{i === "all" ? "All Inboxes" : i}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-3">
        {tickets.map((t) => (
          <Card key={t.id}>
            <CardContent className="p-4 flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{priorityEmoji[t.priority]}</span>
                  <span className="font-semibold">{t.title}</span>
                  <Badge variant="outline">{t.type}</Badge>
                  <Badge className={t.status === "open" ? "bg-blue-100 text-blue-800" : t.status === "in_progress" ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"} variant="secondary">
                    {t.status}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{t.assigned_inbox} — {t.assigned_to}</p>
                <p className="text-sm mt-1">{t.summary}</p>
              </div>
              <div className="shrink-0">
                {t.status !== "resolved" && t.status !== "closed" && (
                  <Button size="sm" variant="outline" className="gap-1" onClick={() => { resolveTicket(t.id); refresh(); toast.success("Ticket resolved") }}>
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Resolve
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
        {tickets.length === 0 && <p className="text-muted-foreground text-center py-8">No tickets match the selected filters.</p>}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Create Ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <TicketForm onSuccess={refresh} />
        </CardContent>
      </Card>
    </div>
  )
}

function TicketForm({ onSuccess }: { onSuccess: () => void }) {
  const [form, setForm] = useState({
    title: "",
    type: "new_business" as TicketType,
    priority: "medium" as TicketPriority,
    inbox: "sales" as InboxType,
    summary: "",
    assigned_to: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addTicket({ ...form, status: "open", assigned_inbox: form.inbox })
    toast.success("Ticket created")
    onSuccess()
    setForm({ title: "", type: "new_business", priority: "medium", inbox: "sales", summary: "", assigned_to: "" })
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label>Title</Label>
        <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
      </div>
      <div className="space-y-2">
        <Label>Assigned To</Label>
        <Input value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} />
      </div>
      <div className="space-y-2">
        <Label>Type</Label>
        <Select value={form.type} onValueChange={(v: TicketType) => setForm({ ...form, type: v })}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {["endorsement", "renewal", "claim", "cross_sell", "service", "new_business", "underwriting"].map((t) => (
              <SelectItem key={t} value={t}>{t.replace(/_/g, " ")}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Priority</Label>
        <Select value={form.priority} onValueChange={(v: TicketPriority) => setForm({ ...form, priority: v })}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {["low", "medium", "high", "urgent"].map((p) => (
              <SelectItem key={p} value={p}>{p}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Inbox</Label>
        <Select value={form.inbox} onValueChange={(v: InboxType) => setForm({ ...form, inbox: v })}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {["sales", "underwriting", "service", "claims"].map((i) => (
              <SelectItem key={i} value={i}>{i}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2 col-span-2">
        <Label>Summary</Label>
        <Textarea value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} />
      </div>
      <div className="col-span-2">
        <Button type="submit" className="gap-2">
          <Plus className="h-4 w-4" />
          Create Ticket
        </Button>
      </div>
    </form>
  )
}
