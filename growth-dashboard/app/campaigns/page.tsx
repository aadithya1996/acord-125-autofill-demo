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
import { getCampaigns, addCampaign, updateCampaignStatus, runCampaign, getRecipients, type Campaign, type CampaignStatus, type CampaignType } from "@/lib/data"
import { toast } from "sonner"
import { Play, Pause, Plus, Eye } from "lucide-react"

const statusColors: Record<CampaignStatus, string> = {
  draft: "bg-slate-100 text-slate-800",
  scheduled: "bg-blue-100 text-blue-800",
  running: "bg-emerald-100 text-emerald-800",
  completed: "bg-slate-100 text-slate-800",
  paused: "bg-amber-100 text-amber-800",
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>(getCampaigns())
  const refresh = () => setCampaigns(getCampaigns())

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Campaigns</h1>
      </div>

      <Tabs defaultValue="list">
        <TabsList>
          <TabsTrigger value="list">All Campaigns</TabsTrigger>
          <TabsTrigger value="builder">Build Campaign</TabsTrigger>
          <TabsTrigger value="run">Run & Monitor</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-4">
          <div className="space-y-3">
            {campaigns.map((c) => (
              <Card key={c.id}>
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">{c.name}</span>
                      <Badge className={statusColors[c.status]} variant="secondary">{c.status}</Badge>
                      <Badge variant="outline">{c.type.replace(/_/g, " ")}</Badge>
                      <Badge variant="outline">{c.channel}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{c.schedule_type} {c.cron_expression && `— ${c.cron_expression}`}</p>
                  </div>
                  <div className="flex gap-2">
                    {c.status === "draft" && (
                      <Button size="sm" variant="outline" onClick={() => { updateCampaignStatus(c.id, "scheduled"); refresh() }}>
                        <Play className="h-3.5 w-3.5 mr-1" />
                        Activate
                      </Button>
                    )}
                    {(c.status === "scheduled" || c.status === "running") && (
                      <Button size="sm" variant="outline" onClick={() => { updateCampaignStatus(c.id, "paused"); refresh() }}>
                        <Pause className="h-3.5 w-3.5 mr-1" />
                        Pause
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="builder" className="mt-4">
          <CampaignBuilder onSuccess={refresh} />
        </TabsContent>

        <TabsContent value="run" className="mt-4">
          <CampaignRunner />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function CampaignBuilder({ onSuccess }: { onSuccess: () => void }) {
  const [form, setForm] = useState({
    name: "",
    type: "renewal_reminder" as CampaignType,
    channel: "email" as "email" | "sms",
    subject: "",
    body: "",
    audience: '{"status":"active","days_before_expiration":30}',
    schedule: "immediate" as "immediate" | "one_time" | "recurring",
    cron: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addCampaign({
      name: form.name,
      type: form.type,
      status: "draft",
      channel: form.channel,
      template_subject: form.subject,
      template_body: form.body,
      audience_filter: form.audience,
      schedule_type: form.schedule,
      cron_expression: form.cron || undefined,
    })
    toast.success("Campaign created")
    onSuccess()
    setForm({ name: "", type: "renewal_reminder", channel: "email", subject: "", body: "", audience: '{"status":"active"}', schedule: "immediate", cron: "" })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Build a New Campaign</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={form.type} onValueChange={(v: CampaignType) => setForm({ ...form, type: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {["renewal_reminder", "cross_sell", "quote_follow_up", "welcome", "seasonal", "custom"].map((t) => (
                    <SelectItem key={t} value={t}>{t.replace(/_/g, " ")}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Channel</Label>
              <Select value={form.channel} onValueChange={(v: "email" | "sms") => setForm({ ...form, channel: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="sms">SMS</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Schedule</Label>
              <Select value={form.schedule} onValueChange={(v: any) => setForm({ ...form, schedule: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="immediate">Immediate</SelectItem>
                  <SelectItem value="one_time">One-time</SelectItem>
                  <SelectItem value="recurring">Recurring (cron)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {form.schedule === "recurring" && (
            <div className="space-y-2">
              <Label>Cron Expression</Label>
              <Input value={form.cron} onChange={(e) => setForm({ ...form, cron: e.target.value })} placeholder="0 9 1 * *" />
              <p className="text-xs text-muted-foreground">e.g. 0 9 * * 1 = Mondays at 9am</p>
            </div>
          )}
          <div className="space-y-2">
            <Label>Subject Line</Label>
            <Input value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Message Body</Label>
            <Textarea value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} rows={6} placeholder="Use {{name}}, {{business_name}}, {{carrier}}, {{policy_number}}, {{expiration_date}} ..." />
          </div>
          <div className="space-y-2">
            <Label>Audience Filter (JSON)</Label>
            <Textarea value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} rows={2} />
          </div>
          <Button type="submit" className="gap-2">
            <Plus className="h-4 w-4" />
            Create Campaign
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

function CampaignRunner() {
  const campaigns = getCampaigns()
  const [selectedId, setSelectedId] = useState<number | null>(campaigns[0]?.id || null)
  const [recipients, setRecipients] = useState(() => getRecipients())

  const handleRun = () => {
    if (!selectedId) return
    const stats = runCampaign(selectedId)
    toast.success(`Queued ${stats.queued}, sent ${stats.sent}, failed ${stats.failed}`)
    setRecipients(getRecipients())
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Manual Execution</CardTitle>
        </CardHeader>
        <CardContent className="flex items-end gap-4">
          <div className="flex-1">
            <Label className="mb-2 block">Select Campaign</Label>
            <Select value={selectedId?.toString() || ""} onValueChange={(v) => setSelectedId(Number(v))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {campaigns.map((c) => (
                  <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleRun} className="gap-2">
            <Play className="h-4 w-4" />
            Run Now
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recipient Activity</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Campaign</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Sent At</TableHead>
                <TableHead>Error</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recipients.slice(0, 50).map((r) => {
                const camp = campaigns.find((c) => c.id === r.campaign_id)
                return (
                  <TableRow key={r.id}>
                    <TableCell>{camp?.name || "—"}</TableCell>
                    <TableCell>
                      <Badge variant={r.status === "sent" ? "default" : "destructive"}>{r.status}</Badge>
                    </TableCell>
                    <TableCell>{r.sent_at ? new Date(r.sent_at).toLocaleString() : "—"}</TableCell>
                    <TableCell className="text-red-600 text-xs">{r.error_message || "—"}</TableCell>
                  </TableRow>
                )
              })}
              {recipients.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground py-6">
                    No recipient activity yet
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
