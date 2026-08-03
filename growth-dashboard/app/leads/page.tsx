"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { getLeads, addLead, updateLeadStatus, type Lead, type LeadStatus } from "@/lib/data"
import { toast } from "sonner"
import { Plus, FileText } from "lucide-react"
import Link from "next/link"

const statusColors: Record<LeadStatus, string> = {
  new: "bg-slate-100 text-slate-800",
  qualified: "bg-blue-100 text-blue-800",
  quoted: "bg-amber-100 text-amber-800",
  bound: "bg-emerald-100 text-emerald-800",
  lost: "bg-red-100 text-red-800",
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>(getLeads())
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)

  const refresh = () => setLeads(getLeads())

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Leads & Intake</h1>
        <Dialog>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Add Lead
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>New Lead Intake</DialogTitle>
            </DialogHeader>
            <LeadForm onSuccess={refresh} />
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="pipeline">
        <TabsList>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="detail">Lead Detail</TabsTrigger>
        </TabsList>

        <TabsContent value="pipeline" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Business</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Assigned</TableHead>
                    <TableHead>Phone</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leads.map((lead) => (
                    <TableRow key={lead.id} className="cursor-pointer" onClick={() => setSelectedLead(lead)}>
                      <TableCell className="font-medium">{lead.name}</TableCell>
                      <TableCell>{lead.business_name}</TableCell>
                      <TableCell>{lead.business_type}</TableCell>
                      <TableCell>
                        <Badge className={statusColors[lead.status]} variant="secondary">{lead.status}</Badge>
                      </TableCell>
                      <TableCell>{lead.source}</TableCell>
                      <TableCell>{lead.assigned_to}</TableCell>
                      <TableCell>{lead.phone}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="detail" className="mt-4">
          {selectedLead ? (
            <LeadDetail lead={selectedLead} onUpdate={refresh} />
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                Select a lead from the pipeline to view details
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

function LeadForm({ onSuccess }: { onSuccess: () => void }) {
  const [form, setForm] = useState({
    name: "", email: "", phone: "", business_name: "", business_type: "Office",
    sic_code: "", naics_code: "", source: "website" as const, notes: "", assigned_to: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addLead({ ...form, status: "new" })
    toast.success("Lead added and ticket created")
    onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-2">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Contact Name</Label>
          <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </div>
        <div className="space-y-2">
          <Label>Email</Label>
          <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>Phone</Label>
          <Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>Business Name</Label>
          <Input value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Business Type</Label>
          <Select value={form.business_type} onValueChange={(v) => setForm({ ...form, business_type: v })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {["Office", "Restaurant", "Retail", "Contractor", "Manufacturing", "Service", "Wholesale", "Other"].map((t) => (
                <SelectItem key={t} value={t}>{t}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Lead Source</Label>
          <Select value={form.source} onValueChange={(v: any) => setForm({ ...form, source: v })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {["website", "referral", "cold_call", "event", "other"].map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>SIC Code</Label>
          <Input value={form.sic_code} onChange={(e) => setForm({ ...form, sic_code: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>NAICS Code</Label>
          <Input value={form.naics_code} onChange={(e) => setForm({ ...form, naics_code: e.target.value })} />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Assigned To</Label>
        <Input value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} placeholder="Agent name" />
      </div>
      <div className="space-y-2">
        <Label>Notes</Label>
        <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      </div>
      <Button type="submit" className="w-full">Save Lead</Button>
    </form>
  )
}

function LeadDetail({ lead, onUpdate }: { lead: Lead; onUpdate: () => void }) {
  const [status, setStatus] = useState<LeadStatus>(lead.status)

  const handleUpdate = () => {
    updateLeadStatus(lead.id, status)
    toast.success("Status updated")
    onUpdate()
  }

  const acordPayload = {
    named_insured: { full_name: lead.name, business_name: lead.business_name },
    business_type: { type: lead.business_type },
    lines_of_business: { general_liability: { selected: true, premium: "" } },
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{lead.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-muted-foreground">Business:</span> {lead.business_name}</div>
            <div><span className="text-muted-foreground">Type:</span> {lead.business_type}</div>
            <div><span className="text-muted-foreground">Phone:</span> {lead.phone}</div>
            <div><span className="text-muted-foreground">Email:</span> {lead.email}</div>
            <div><span className="text-muted-foreground">SIC:</span> {lead.sic_code}</div>
            <div><span className="text-muted-foreground">NAICS:</span> {lead.naics_code}</div>
          </div>
          <div className="flex items-center gap-4">
            <Select value={status} onValueChange={(v: LeadStatus) => setStatus(v)}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["new", "qualified", "quoted", "bound", "lost"].map((s) => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleUpdate} variant="outline">Update Status</Button>
          </div>
          <p className="text-sm text-muted-foreground">{lead.notes}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Link
            href={`/acord?payload=${encodeURIComponent(JSON.stringify(acordPayload))}`}
          >
            <Button className="gap-2">
              <FileText className="h-4 w-4" />
              Pre-fill ACORD 125
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
