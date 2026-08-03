"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { FileDown, Send } from "lucide-react"

const SCENARIOS: Record<string, string> = {
  tech: JSON.stringify({
    producer: { full_name: "CyberShield Insurance Agency", address_line1: "101 Market Street", city: "San Francisco", state: "CA", zip: "94105", contact_name: "Alice Nguyen", phone: "(415) 555-0192", email: "alice@cybershield.com" },
    policy: { status: "Bound", effective_date: "01/15/2026", effective_time: "12:01 AM", expiration_date: "01/15/2027" },
    lines_of_business: { general_liability: { selected: true, premium: "8,500" }, commercial_property: { selected: true, premium: "4,200" }, cyber_and_privacy: { selected: true, premium: "12,000" } },
    named_insured: { full_name: "Nexus Data Systems, Inc.", address_line1: "450 Mission Bay Blvd", city: "San Francisco", state: "CA", zip: "94158", fein: "94-1234567", sic_code: "7372", naics_code: "541512", phone: "(415) 555-0300", legal_entity: "Corporation" },
    contact: { description: "Risk Manager", full_name: "David Park", phone: "(415) 555-0301", email: "d.park@nexusdata.io" },
    location: { address_line1: "450 Mission Bay Blvd", city: "San Francisco", state: "CA", zip: "94158", full_time_employees: "85", annual_revenue: "18,500,000", operations_description: "Cloud infrastructure & SaaS platform development" },
    business_type: { type: "Office", business_start_date: "2018-06-01" },
    prior_coverage: { policy_year: "2025", gl_insurer: "Hartford Insurance", gl_policy_number: "GL-2025-88421", gl_effective_date: "01/15/2025", gl_expiration_date: "01/15/2026" },
    loss_history: { no_prior_losses: true },
  }, null, 2),
  restaurant: JSON.stringify({
    producer: { full_name: "Metro Commercial Insurance", address_line1: "225 Peachtree St NE", city: "Atlanta", state: "GA", zip: "30303", contact_name: "Carlos Rivera", phone: "(404) 555-0147", email: "c.rivera@metrocomm.com" },
    policy: { status: "Quote", effective_date: "03/01/2026", effective_time: "12:01 AM", expiration_date: "03/01/2027" },
    lines_of_business: { general_liability: { selected: true, premium: "22,000" }, commercial_property: { selected: true, premium: "35,500" }, business_owners: { selected: true, premium: "8,750" } },
    named_insured: { full_name: "Savannah Bistro Group, LLC", address_line1: "842 West Peachtree St NW", city: "Atlanta", state: "GA", zip: "30308", fein: "58-9876543", sic_code: "5812", naics_code: "722511", phone: "(404) 555-0299", legal_entity: "LLC" },
    contact: { description: "General Manager", full_name: "Maria Santos", phone: "(404) 555-0288", email: "msantos@savbistro.com" },
    location: { address_line1: "842 West Peachtree St NW", city: "Atlanta", state: "GA", zip: "30308", full_time_employees: "42", annual_revenue: "4,200,000", operations_description: "Full-service restaurant & catering" },
    business_type: { type: "Restaurant", business_start_date: "2015-09-12" },
    prior_coverage: { policy_year: "2025", gl_insurer: "Liberty Mutual", gl_policy_number: "LM-GL-99543", gl_effective_date: "03/01/2025", gl_expiration_date: "03/01/2026" },
    loss_history: { no_prior_losses: false },
  }, null, 2),
  construction: JSON.stringify({
    producer: { full_name: "BuildSecure Agency", address_line1: "500 W Madison St", city: "Chicago", state: "IL", zip: "60661", contact_name: "James O'Brien", phone: "(312) 555-0176", email: "j.obrien@buildsecure.com" },
    policy: { status: "Renew", effective_date: "06/01/2026", effective_time: "12:01 AM", expiration_date: "06/01/2027" },
    lines_of_business: { general_liability: { selected: true, premium: "45,000" } },
    named_insured: { full_name: "Lakeside Construction Partners, LLC", address_line1: "1400 S Western Ave", city: "Chicago", state: "IL", zip: "60608", fein: "36-1122334", sic_code: "1541", naics_code: "236220", phone: "(312) 555-0456", legal_entity: "LLC" },
    contact: { description: "Safety Director", full_name: "Robert Kim", phone: "(312) 555-0457", email: "r.kim@lakesidebuild.com" },
    location: { address_line1: "1400 S Western Ave", city: "Chicago", state: "IL", zip: "60608", full_time_employees: "120", annual_revenue: "32,000,000", operations_description: "Commercial building construction & general contracting" },
    business_type: { type: "Contractor", business_start_date: "2009-04-20" },
    prior_coverage: { policy_year: "2025", gl_insurer: "Zurich North America", gl_policy_number: "ZN-GL-77210", gl_effective_date: "06/01/2025", gl_expiration_date: "06/01/2026" },
    loss_history: { no_prior_losses: true },
  }, null, 2),
}

function AcordPageInner() {
  const searchParams = useSearchParams()
  const [jsonText, setJsonText] = useState(SCENARIOS.tech)
  const [generating, setGenerating] = useState(false)
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null)

  useEffect(() => {
    const payload = searchParams.get("payload")
    if (payload) {
      try {
        const parsed = JSON.parse(decodeURIComponent(payload))
        // Merge with tech scenario as base
        const base = JSON.parse(SCENARIOS.tech)
        setJsonText(JSON.stringify({ ...base, ...parsed }, null, 2))
      } catch {
        // ignore
      }
    }
  }, [searchParams])

  const loadScenario = (key: string) => {
    setJsonText(SCENARIOS[key] || "{}")
    setPdfBlob(null)
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await fetch("/api/generate-acord", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonText,
      })
      if (!res.ok) throw new Error("Generation failed")
      const blob = await res.blob()
      setPdfBlob(blob)
      toast.success("PDF generated successfully")
    } catch (e) {
      toast.error("Failed to generate PDF. Is the Python backend running?")
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">ACORD 125 Auto-Fill</h1>

      <div className="flex gap-2">
        <Button variant="outline" size="sm" onClick={() => loadScenario("tech")}>Tech Startup</Button>
        <Button variant="outline" size="sm" onClick={() => loadScenario("restaurant")}>Restaurant</Button>
        <Button variant="outline" size="sm" onClick={() => loadScenario("construction")}>Construction</Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>JSON Payload</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              rows={24}
              className="font-mono text-sm"
            />
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={handleGenerate} disabled={generating} className="w-full gap-2">
                <Send className="h-4 w-4" />
                {generating ? "Generating..." : "Generate PDF"}
              </Button>
              {pdfBlob && (
                <a href={URL.createObjectURL(pdfBlob)} download="ACORD_125_Filled.pdf">
                  <Button variant="outline" className="w-full gap-2">
                    <FileDown className="h-4 w-4" />
                    Download PDF
                  </Button>
                </a>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Reference</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-1 text-muted-foreground">
              <p><strong>Policy Status:</strong> Quote, Issue, Renew, Bound, Change, Cancel</p>
              <p><strong>Legal Entity:</strong> Corporation, LLC, Partnership, Individual, NonProfit, SubchapterS, JointVenture, Trust, Other</p>
              <p><strong>Business Type:</strong> Office, Restaurant, Retail, Contractor, Manufacturing, Service, Wholesale, Other</p>
              <p><strong>LOB Keys:</strong> general_liability, commercial_property, business_owners, cyber_and_privacy</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default function AcordPage() {
  return (
    <Suspense fallback={<div className="p-8">Loading...</div>}>
      <AcordPageInner />
    </Suspense>
  )
}
