"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { getMetrics, getTickets, runCampaign, getCampaigns, getRecipients } from "@/lib/data"
import { formatCurrency } from "@/lib/format"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { toast } from "sonner"
import { useState, useEffect } from "react"
import { Megaphone, TicketCheck, Users, FileCheck, TrendingUp, AlertTriangle } from "lucide-react"

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(getMetrics())
  const [tickets, setTickets] = useState(getTickets({ status: ["open", "in_progress"] }))
  const [campaigns, setCampaigns] = useState(getCampaigns())

  useEffect(() => {
    setMetrics(getMetrics())
    setTickets(getTickets({ status: ["open", "in_progress"] }))
    setCampaigns(getCampaigns())
  }, [])

  const leadData = [
    { stage: "New", count: metrics.leadCount > 0 ? 1 : 0 },
    { stage: "Qualified", count: metrics.leadCount > 0 ? 1 : 0 },
    { stage: "Quoted", count: metrics.leadCount > 0 ? 1 : 0 },
    { stage: "Bound", count: 0 },
  ]

  const handleRunCampaigns = () => {
    const pending = campaigns.filter((c) => c.status === "scheduled")
    if (pending.length === 0) {
      toast.info("No pending campaigns to run")
      return
    }
    pending.forEach((c) => runCampaign(c.id))
    toast.success(`Ran ${pending.length} campaign(s)`)
    setMetrics(getMetrics())
    setCampaigns(getCampaigns())
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <Button onClick={handleRunCampaigns} className="gap-2">
          <Megaphone className="h-4 w-4" />
          Run Pending Campaigns
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Total Premium" value={formatCurrency(metrics.totalPremium)} icon={<TrendingUp className="h-4 w-4 text-emerald-600" />} />
        <KpiCard title="Active Policies" value={metrics.activePolicies.toString()} icon={<FileCheck className="h-4 w-4 text-blue-600" />} />
        <KpiCard title="Clients" value={metrics.clientCount.toString()} icon={<Users className="h-4 w-4 text-violet-600" />} />
        <KpiCard title="Open Tickets" value={metrics.openTickets.toString()} subtitle={`${metrics.urgentTickets} urgent`} icon={<TicketCheck className="h-4 w-4 text-amber-600" />} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Lead Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={leadData}>
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Ticket Inbox</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {tickets.slice(0, 5).map((t) => (
              <div key={t.id} className="flex items-start justify-between gap-2 text-sm">
                <div className="min-w-0">
                  <p className="font-medium truncate">{t.title}</p>
                  <p className="text-muted-foreground text-xs">{t.assigned_inbox} — {t.summary.slice(0, 40)}...</p>
                </div>
                <Badge variant={t.priority === "urgent" ? "destructive" : t.priority === "high" ? "default" : "secondary"}>
                  {t.priority}
                </Badge>
              </div>
            ))}
            {tickets.length === 0 && <p className="text-sm text-muted-foreground">No open tickets</p>}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Megaphone className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Running Campaigns</span>
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.runningCampaigns}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <span className="text-sm font-medium">Renewals (90d)</span>
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.upcomingRenewals}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-600" />
              <span className="text-sm font-medium">Emails Sent</span>
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.emailsSent}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function KpiCard({ title, value, subtitle, icon }: { title: string; value: string; subtitle?: string; icon: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
          {icon}
        </div>
        <p className="text-2xl font-bold mt-2">{value}</p>
        {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
      </CardContent>
    </Card>
  )
}
