"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getClients, getPolicies, type Client, type Policy } from "@/lib/data"
import { formatCurrency, formatDate } from "@/lib/format"
import { differenceInDays, parseISO } from "date-fns"
import { AlertTriangle } from "lucide-react"

export default function ClientsPage() {
  const clients = getClients()
  const policies = getPolicies()

  const upcomingRenewals = policies.filter((p) => {
    if (p.status !== "active") return false
    const days = differenceInDays(parseISO(p.expiration_date), new Date())
    return days <= 90 && days >= 0
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Clients & Policies</h1>

      <Tabs defaultValue="clients">
        <TabsList>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
          <TabsTrigger value="renewals">
            <AlertTriangle className="h-3.5 w-3.5 mr-1" />
            Renewals
          </TabsTrigger>
        </TabsList>

        <TabsContent value="clients" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Business</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>State</TableHead>
                    <TableHead>Policies</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {clients.map((c) => {
                    const clientPolicies = policies.filter((p) => p.client_id === c.id)
                    return (
                      <TableRow key={c.id}>
                        <TableCell className="font-medium">{c.name}</TableCell>
                        <TableCell>{c.business_name}</TableCell>
                        <TableCell>{c.email}</TableCell>
                        <TableCell>{c.phone}</TableCell>
                        <TableCell>{c.state}</TableCell>
                        <TableCell>{clientPolicies.length}</TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="policies" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Client</TableHead>
                    <TableHead>Carrier</TableHead>
                    <TableHead>Policy #</TableHead>
                    <TableHead>LOB</TableHead>
                    <TableHead>Premium</TableHead>
                    <TableHead>Effective</TableHead>
                    <TableHead>Expires</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {policies.map((p) => {
                    const client = clients.find((c) => c.id === p.client_id)
                    return (
                      <TableRow key={p.id}>
                        <TableCell className="font-medium">{client?.name || "—"}</TableCell>
                        <TableCell>{p.carrier}</TableCell>
                        <TableCell>{p.policy_number}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{p.line_of_business.replace(/_/g, " ")}</Badge>
                        </TableCell>
                        <TableCell>{formatCurrency(p.premium)}</TableCell>
                        <TableCell>{p.effective_date}</TableCell>
                        <TableCell>{p.expiration_date}</TableCell>
                        <TableCell>
                          <Badge className={p.status === "active" ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-800"} variant="secondary">
                            {p.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="renewals" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Renewals (Next 90 Days)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {upcomingRenewals.map((p) => {
                const client = clients.find((c) => c.id === p.client_id)
                const days = differenceInDays(parseISO(p.expiration_date), new Date())
                return (
                  <div key={p.id} className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <p className="font-medium">{client?.name || "Unknown"}</p>
                      <p className="text-sm text-muted-foreground">{p.carrier} {p.line_of_business.replace(/_/g, " ")}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{p.expiration_date}</p>
                      <Badge variant={days <= 30 ? "destructive" : days <= 60 ? "default" : "secondary"}>
                        {days} days left
                      </Badge>
                    </div>
                  </div>
                )
              })}
              {upcomingRenewals.length === 0 && <p className="text-sm text-muted-foreground">No renewals in the next 90 days.</p>}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
