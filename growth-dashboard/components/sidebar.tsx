"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Target,
  Users,
  TicketCheck,
  Megaphone,
  FileText,
  Shield,
} from "lucide-react"

const nav = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Leads & Intake", href: "/leads", icon: Target },
  { name: "Clients & Policies", href: "/clients", icon: Users },
  { name: "Tickets / Inbox", href: "/tickets", icon: TicketCheck },
  { name: "Campaigns", href: "/campaigns", icon: Megaphone },
  { name: "ACORD 125", href: "/acord", icon: FileText },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col shrink-0">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-emerald-400" />
          <span className="font-bold text-lg tracking-tight">Growth OS</span>
        </div>
        <p className="text-xs text-slate-400 mt-1">Insurance Brokerage</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {nav.map((item) => {
          const Icon = item.icon
          const active = pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="p-4 border-t border-slate-800">
        <p className="text-xs text-slate-500">Metro Commercial Insurance</p>
        <p className="text-xs text-slate-500">v1.0.0</p>
      </div>
    </aside>
  )
}
