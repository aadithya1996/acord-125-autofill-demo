"""
Insurance Growth OS — Unified Streamlit Dashboard
Combines ACORD 125 auto-fill with lead capture, ticketing, and campaign management.
"""

import json
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import streamlit as st
import pandas as pd

from schemas import Acord125Input
from field_mapper import map_data_to_pdf_fields
from pdf_filler import fill_acord_125

from growth_os import (
    init_db, get_session, seed_demo_data,
    FirmSettings, Lead, Client, Policy, Ticket, Campaign, CampaignRecipient,
    get_dashboard_metrics,
    run_pending_campaigns, execute_campaign, queue_campaign_recipients,
    schedule_campaign, unschedule_campaign, get_scheduler,
    create_ticket_from_lead, create_ticket_from_policy, promote_lead_to_client,
    render_template,
)


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
if "db_init" not in st.session_state:
    init_db()
    with get_session() as s:
        seed_demo_data(s)
    st.session_state.db_init = True

if "scheduler_started" not in st.session_state:
    # Start APScheduler silently (no jobs yet until campaigns are scheduled)
    get_scheduler()
    st.session_state.scheduler_started = True

st.set_page_config(
    page_title="Insurance Growth OS",
    page_icon="🚀",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
st.sidebar.title("🚀 Insurance Growth OS")

page = st.sidebar.radio(
    "Navigate",
    options=[
        "📊 Dashboard",
        "🎯 Leads & Intake",
        "👥 Clients & Policies",
        "🎫 Tickets / Inbox",
        "📢 Campaigns",
        "📋 ACORD 125 Filler",
    ],
    index=0,
)

# ---------------------------------------------------------------------------
# Helper: DB session context manager
# ---------------------------------------------------------------------------
def db_session():
    return get_session()


# =============================================================================
# PAGE 1 — DASHBOARD
# =============================================================================
if page == "📊 Dashboard":
    st.title("📊 Insurance Growth OS Dashboard")
    st.caption("Real-time KPIs for your brokerage.")

    with db_session() as s:
        metrics = get_dashboard_metrics(s)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Premium", f"${metrics['total_premium']:,.0f}")
    c2.metric("Active Policies", metrics["policies_active"])
    c3.metric("Clients", metrics["clients_total"])
    c4.metric("Open Tickets", metrics["tickets_open"], delta=metrics["tickets_urgent"], delta_color="inverse")
    c5.metric("Renewals (90d)", metrics["upcoming_renewals"])

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Lead Pipeline")
        lead_data = {
            "Stage": ["New", "Qualified", "Quoted", "Bound", "Lost"],
            "Count": [
                metrics["leads_new"],
                metrics["leads_quoted"] + metrics["leads_new"] // 2,  # approximate
                metrics["leads_quoted"],
                metrics["leads_bound"],
                max(0, metrics["leads_total"] - metrics["leads_new"] - metrics["leads_quoted"] - metrics["leads_bound"]),
            ],
        }
        st.bar_chart(pd.DataFrame(lead_data).set_index("Stage"))

    with col_right:
        st.subheader("Ticket Inbox")
        with db_session() as s:
            tickets = s.query(Ticket).filter(Ticket.status.in_(["open", "in_progress"])).order_by(Ticket.priority).all()
        for t in tickets[:5]:
            priority_color = {"low": "gray", "medium": "blue", "high": "orange", "urgent": "red"}.get(t.priority, "gray")
            st.markdown(f"**[{t.priority.upper()}]** `{t.assigned_inbox}` — {t.title}")

    st.divider()
    st.subheader("Campaign Activity")
    c1, c2, c3 = st.columns(3)
    c1.metric("Running Campaigns", metrics["campaigns_running"])
    c2.metric("Emails Sent", metrics["emails_sent"])
    c3.metric("Upcoming Renewals", metrics["upcoming_renewals"])

    # Manual campaign run
    st.divider()
    if st.button("▶️ Run Pending Campaigns Now", type="primary"):
        with db_session() as s:
            results = run_pending_campaigns(s)
        if results:
            for r in results:
                st.success(f"Ran **{r['campaign_name']}**: queued {r['queued']}, sent {r['sent']}, failed {r['failed']}")
        else:
            st.info("No pending campaigns ready to run.")


# =============================================================================
# PAGE 2 — LEADS & INTAKE
# =============================================================================
elif page == "🎯 Leads & Intake":
    st.title("🎯 Leads & Intake")

    tab_list, tab_add, tab_detail = st.tabs(["Lead Pipeline", "➕ Add Lead", "Lead Detail"])

    with tab_list:
        with db_session() as s:
            leads = s.query(Lead).order_by(Lead.created_at.desc()).all()
        if leads:
            df = pd.DataFrame([{
                "ID": l.id,
                "Name": l.name,
                "Business": l.business_name,
                "Type": l.business_type,
                "Status": l.status,
                "Source": l.source,
                "Assigned": l.assigned_to,
                "Phone": l.phone,
                "Created": l.created_at.strftime("%Y-%m-%d"),
            } for l in leads])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No leads yet.")

    with tab_add:
        st.subheader("New Lead Intake Form")
        with st.form("lead_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Contact Name")
            email = col1.text_input("Email")
            phone = col1.text_input("Phone")
            biz_name = col2.text_input("Business Name")
            biz_type = col2.selectbox("Business Type", ["Office", "Restaurant", "Retail", "Contractor", "Manufacturing", "Service", "Wholesale", "Other"])
            sic = col2.text_input("SIC Code")
            naics = col2.text_input("NAICS Code")
            source = st.selectbox("Lead Source", ["website", "referral", "cold_call", "event", "other"])
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save Lead", type="primary")

            if submitted:
                with db_session() as s:
                    lead = Lead(
                        name=name, email=email, phone=phone,
                        business_name=biz_name, business_type=biz_type,
                        sic_code=sic, naics_code=naics,
                        status="new", source=source, notes=notes,
                    )
                    s.add(lead)
                    s.commit()
                    # Auto-create ticket
                    create_ticket_from_lead(s, lead.id, f"New lead: {biz_name or name}", summary=notes)
                st.success(f"Lead saved! Ticket auto-created.")
                st.rerun()

    with tab_detail:
        with db_session() as s:
            leads = s.query(Lead).order_by(Lead.created_at.desc()).all()
        lead_names = {f"{l.name} ({l.business_name or 'No business'})": l.id for l in leads}
        if lead_names:
            selected = st.selectbox("Select lead", options=list(lead_names.keys()))
            lead_id = lead_names[selected]
            with db_session() as s:
                lead = s.query(Lead).get(lead_id)
            if lead:
                st.write(f"**Status:** {lead.status}")
                c1, c2 = st.columns(2)
                new_status = c1.selectbox("Update Status", ["new", "qualified", "quoted", "bound", "lost"], index=["new","qualified","quoted","bound","lost"].index(lead.status))
                if c2.button("Update"):
                    with db_session() as s:
                        l = s.query(Lead).get(lead_id)
                        l.status = new_status
                        s.commit()
                    st.success("Status updated!")
                    st.rerun()

                st.divider()
                # ACORD filler integration
                st.subheader("📋 Generate ACORD 125 from Lead")
                if st.button("Pre-fill ACORD 125", type="primary"):
                    # Build minimal JSON from lead
                    acord_data = {
                        "named_insured": {
                            "full_name": lead.name,
                            "business_name": lead.business_name,
                        },
                        "business_type": {"type": lead.business_type or "Office"},
                        "lines_of_business": {
                            "general_liability": {"selected": True, "premium": ""},
                        },
                    }
                    st.session_state.acord_from_lead = json.dumps(acord_data, indent=2)
                    st.info("ACORD payload prepared. Go to the ACORD 125 Filler page to edit and generate.")
        else:
            st.info("No leads to display.")


# =============================================================================
# PAGE 3 — CLIENTS & POLICIES
# =============================================================================
elif page == "👥 Clients & Policies":
    st.title("👥 Clients & Policies")

    tab_clients, tab_policies = st.tabs(["Clients", "Policies"])

    with tab_clients:
        with db_session() as s:
            clients = s.query(Client).all()
        if clients:
            df = pd.DataFrame([{
                "ID": c.id,
                "Name": c.name,
                "Business": c.business_name,
                "Email": c.email,
                "Phone": c.phone,
                "State": c.state,
                "Policies": len(c.policies.all()),
            } for c in clients])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No clients yet.")

    with tab_policies:
        with db_session() as s:
            policies = s.query(Policy).order_by(Policy.expiration_date).all()
        if policies:
            df = pd.DataFrame([{
                "ID": p.id,
                "Client": p.client.name if p.client else "",
                "Carrier": p.carrier,
                "Policy #": p.policy_number,
                "LOB": p.line_of_business,
                "Premium": f"${p.premium:,.2f}",
                "Effective": p.effective_date,
                "Expires": p.expiration_date,
                "Status": p.status,
            } for p in policies])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No policies yet.")

        # Renewal alerts
        st.divider()
        st.subheader("⏰ Upcoming Renewals (Next 90 Days)")
        cutoff = (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")
        with db_session() as s:
            renewals = s.query(Policy).filter(
                Policy.status == "active",
                Policy.expiration_date <= cutoff,
            ).order_by(Policy.expiration_date).all()
        if renewals:
            for p in renewals:
                days_left = (datetime.strptime(p.expiration_date, "%Y-%m-%d") - datetime.utcnow()).days
                st.markdown(f"**{p.client.name if p.client else 'Unknown'}** — {p.carrier} {p.line_of_business} expires **{p.expiration_date}** ({days_left} days)")
        else:
            st.info("No renewals in the next 90 days.")


# =============================================================================
# PAGE 4 — TICKETS / INBOX
# =============================================================================
elif page == "🎫 Tickets / Inbox":
    st.title("🎫 Tickets / Inbox")

    inbox_filter = st.sidebar.radio("Inbox", ["All", "sales", "underwriting", "service", "claims"])
    status_filter = st.sidebar.multiselect("Status", ["open", "in_progress", "resolved", "closed"], default=["open", "in_progress"])

    with db_session() as s:
        query = s.query(Ticket).filter(Ticket.status.in_(status_filter))
        if inbox_filter != "All":
            query = query.filter(Ticket.assigned_inbox == inbox_filter)
        tickets = query.order_by(Ticket.priority, Ticket.created_at.desc()).all()

    st.caption(f"Showing {len(tickets)} tickets")

    for t in tickets:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(t.priority, "⚪")
            col1.markdown(f"{priority_emoji} **{t.title}**  <br>`{t.type}` | `{t.assigned_inbox}` | {t.summary[:80]}...", unsafe_allow_html=True)
            col2.markdown(f"**Status:** {t.status}")
            col3.markdown(f"**Assigned:** {t.assigned_to}")
            with col4:
                if t.status in ["open", "in_progress"]:
                    if st.button("Resolve", key=f"resolve_{t.id}"):
                        with db_session() as s2:
                            tick = s2.query(Ticket).get(t.id)
                            tick.status = "resolved"
                            tick.resolved_at = datetime.utcnow()
                            s2.commit()
                        st.rerun()
            st.divider()

    # Create ticket
    with st.expander("➕ Create Ticket"):
        with st.form("ticket_form"):
            title = st.text_input("Title")
            t_type = st.selectbox("Type", ["endorsement", "renewal", "claim", "cross_sell", "service", "new_business", "underwriting"])
            priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
            inbox = st.selectbox("Inbox", ["sales", "underwriting", "service", "claims"])
            summary = st.text_area("Summary")
            if st.form_submit_button("Create", type="primary"):
                with db_session() as s:
                    t = Ticket(title=title, type=t_type, priority=priority, assigned_inbox=inbox, summary=summary)
                    s.add(t)
                    s.commit()
                st.success("Ticket created!")
                st.rerun()


# =============================================================================
# PAGE 5 — CAMPAIGNS
# =============================================================================
elif page == "📢 Campaigns":
    st.title("📢 Campaigns")

    tab_list, tab_builder, tab_run = st.tabs(["All Campaigns", "➕ Build Campaign", "Run & Monitor"])

    with tab_list:
        with db_session() as s:
            campaigns = s.query(Campaign).order_by(Campaign.created_at.desc()).all()
        if campaigns:
            for camp in campaigns:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**{camp.name}**  <br>`{camp.type}` | `{camp.status}` | {camp.channel}", unsafe_allow_html=True)
                col2.markdown(f"Schedule: {camp.schedule_type}")
                with col3:
                    if camp.status == "draft":
                        if st.button("Activate", key=f"act_{camp.id}"):
                            with db_session() as s2:
                                c = s2.query(Campaign).get(camp.id)
                                c.status = "scheduled"
                                s2.commit()
                                if camp.schedule_type == "recurring":
                                    schedule_campaign(c)
                            st.rerun()
                    elif camp.status in ["scheduled", "running"]:
                        if st.button("Pause", key=f"pause_{camp.id}"):
                            with db_session() as s2:
                                c = s2.query(Campaign).get(camp.id)
                                c.status = "paused"
                                s2.commit()
                                unschedule_campaign(camp.id)
                            st.rerun()
                st.divider()
        else:
            st.info("No campaigns yet.")

    with tab_builder:
        st.subheader("Build a New Campaign")
        with st.form("campaign_form"):
            name = st.text_input("Campaign Name")
            camp_type = st.selectbox("Type", ["renewal_reminder", "cross_sell", "quote_follow_up", "welcome", "seasonal", "custom"])
            channel = st.selectbox("Channel", ["email", "sms"])
            subject = st.text_input("Subject Line")
            body = st.text_area("Message Body (use {{name}}, {{business_name}}, etc.)", height=200)
            audience = st.text_area("Audience Filter (JSON)", value='{"status":"active","days_before_expiration":30}')
            schedule = st.selectbox("Schedule", ["immediate", "one_time", "recurring"])
            schedule_time = None
            cron = None
            if schedule == "one_time":
                schedule_time = st.date_input("Send Date")
            elif schedule == "recurring":
                cron = st.text_input("Cron Expression", value="0 9 1 * *", help="e.g. 0 9 * * 1 = Mondays 9am")

            if st.form_submit_button("Create Campaign", type="primary"):
                with db_session() as s:
                    camp = Campaign(
                        name=name, type=camp_type, status="draft",
                        channel=channel, template_subject=subject, template_body=body,
                        audience_filter=audience, schedule_type=schedule,
                        schedule_time=datetime.combine(schedule_time, datetime.min.time()) if schedule_time else None,
                        cron_expression=cron,
                    )
                    s.add(camp)
                    s.commit()
                st.success("Campaign created! Activate it from the list.")
                st.rerun()

    with tab_run:
        st.subheader("Manual Execution")
        with db_session() as s:
            campaigns = s.query(Campaign).filter(Campaign.status.in_(["scheduled", "running", "draft"])).all()
        camp_opts = {f"{c.name} (ID:{c.id})": c.id for c in campaigns}
        if camp_opts:
            selected = st.selectbox("Select campaign", options=list(camp_opts.keys()))
            camp_id = camp_opts[selected]
            if st.button("▶️ Run Selected Campaign Now", type="primary"):
                with db_session() as s:
                    camp = s.query(Campaign).get(camp_id)
                    queued = queue_campaign_recipients(s, camp)
                    stats = execute_campaign(s, camp)
                st.success(f"Queued {queued} recipients. Sent {stats['sent']}, failed {stats['failed']}.")
        else:
            st.info("No campaigns available to run.")

        st.divider()
        st.subheader("Recipient Activity")
        with db_session() as s:
            recipients = s.query(CampaignRecipient).order_by(CampaignRecipient.sent_at.desc()).limit(50).all()
        if recipients:
            df = pd.DataFrame([{
                "Campaign": r.campaign.name if r.campaign else "",
                "Status": r.status,
                "Sent": r.sent_at.strftime("%Y-%m-%d %H:%M") if r.sent_at else "",
                "Error": r.error_message or "",
            } for r in recipients])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recipient activity yet.")


# =============================================================================
# PAGE 6 — ACORD 125 FILLER (Existing)
# =============================================================================
elif page == "📋 ACORD 125 Filler":
    st.title("📋 ACORD 125 Commercial Insurance Auto-Fill")
    st.markdown("Select a scenario or build from a lead, edit the JSON, and generate a filled PDF.")

    SAMPLE_DIR = Path(__file__).parent / "sample_data"
    SCENARIOS = {
        "Tech Startup": SAMPLE_DIR / "tech_startup.json",
        "Restaurant Chain": SAMPLE_DIR / "restaurant_chain.json",
        "Construction Business": SAMPLE_DIR / "construction_business.json",
        "From Lead": None,
        "Custom (blank)": None,
    }

    # Load pre-filled data from lead if available
    if "acord_from_lead" in st.session_state:
        SCENARIOS["From Lead"] = st.session_state.acord_from_lead

    def load_scenario(name: str) -> str:
        path = SCENARIOS.get(name)
        if isinstance(path, Path) and path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        if isinstance(path, str):
            return path
        return "{}"

    scenario_name = st.selectbox("Choose a demo scenario", options=list(SCENARIOS.keys()), index=0)

    if st.session_state.get("last_acord_scenario") != scenario_name:
        st.session_state.json_text = load_scenario(scenario_name)
        st.session_state.last_acord_scenario = scenario_name
        st.session_state.pop("generated_pdf", None)

    if "json_text" not in st.session_state:
        st.session_state.json_text = load_scenario(scenario_name)
    if "last_acord_scenario" not in st.session_state:
        st.session_state.last_acord_scenario = scenario_name

    st.subheader("Payload Editor (JSON)")
    json_text = st.text_area("Edit JSON:", value=st.session_state.json_text, height=420, key="acord_json_editor")
    st.session_state.json_text = json_text

    if st.button("⚡ Generate PDF", type="primary"):
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            st.stop()

        try:
            validated = Acord125Input(**data)
            validated_dict = validated.model_dump(by_alias=True)
        except Exception as e:
            st.warning(f"Validation note: {e}")
            validated_dict = data

        try:
            pdf_data = map_data_to_pdf_fields(validated_dict)
            pdf_buffer = fill_acord_125(pdf_data)
            st.session_state.generated_pdf = pdf_buffer.getvalue()
            st.success("✅ PDF generated successfully!")
        except FileNotFoundError as e:
            st.error(f"Template error: {e}")
        except Exception as e:
            st.error(f"Generation failed: {e}")

    if "generated_pdf" in st.session_state:
        st.download_button(
            label="⬇️ Download ACORD 125 PDF",
            data=st.session_state.generated_pdf,
            file_name="ACORD_125_Filled.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.info("The PDF retains editable AcroForm fields.")
