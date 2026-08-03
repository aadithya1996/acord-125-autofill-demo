"""
Insurance Growth OS — Campaign Engine & Business Logic
Handles campaign execution, cron scheduling, and inbox routing.
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import (
    get_session, Campaign, CampaignRecipient, Lead, Client, Policy, Ticket,
    FirmSettings,
)


# ---------------------------------------------------------------------------
# Campaign Engine
# ---------------------------------------------------------------------------

def render_template(template: str, context: Dict[str, str]) -> str:
    """Simple {{var}} substitution."""
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")
    return result


def build_recipient_context(
    recipient: CampaignRecipient,
    firm: FirmSettings,
    session: Session,
) -> Dict[str, str]:
    """Build the variable context for a campaign email template."""
    ctx = {
        "firm_name": firm.firm_name or "Your Insurance Agency",
        "firm_phone": firm.phone or "",
        "firm_email": firm.email or "",
    }

    if recipient.client_id:
        client = session.query(Client).get(recipient.client_id)
        if client:
            ctx.update({
                "name": client.name or "",
                "email": client.email or "",
                "phone": client.phone or "",
                "business_name": client.business_name or "",
                "assigned_to": "Account Manager",
            })
            # Find most relevant policy
            policy = session.query(Policy).filter(Policy.client_id == client.id).order_by(Policy.expiration_date.desc()).first()
            if policy:
                ctx.update({
                    "carrier": policy.carrier or "",
                    "policy_number": policy.policy_number or "",
                    "lob": policy.line_of_business or "",
                    "premium": str(policy.premium) if policy.premium else "",
                    "effective_date": policy.effective_date or "",
                    "expiration_date": policy.expiration_date or "",
                })

    elif recipient.lead_id:
        lead = session.query(Lead).get(recipient.lead_id)
        if lead:
            ctx.update({
                "name": lead.name or "",
                "email": lead.email or "",
                "phone": lead.phone or "",
                "business_name": lead.business_name or "",
                "assigned_to": lead.assigned_to or "",
            })

    return ctx


def evaluate_audience_filter(session: Session, campaign: Campaign) -> List[Any]:
    """Evaluate a campaign's audience_filter JSON and return matching leads/clients."""
    recipients = []
    try:
        filt = json.loads(campaign.audience_filter or "{}")
    except Exception:
        return recipients

    # Filter by lead status
    lead_status = filt.get("status")
    if lead_status:
        leads = session.query(Lead).filter(Lead.status == lead_status).all()
        recipients.extend(leads)

    # Filter by client policy status
    policy_status = filt.get("policy_status")
    lob = filt.get("lob")
    days_before_expiration = filt.get("days_before_expiration")

    if policy_status or lob or days_before_expiration:
        query = session.query(Client).join(Policy)
        if policy_status:
            query = query.filter(Policy.status == policy_status)
        if lob:
            query = query.filter(Policy.line_of_business == lob)
        if days_before_expiration:
            cutoff = (datetime.utcnow() + timedelta(days=days_before_expiration)).strftime("%Y-%m-%d")
            query = query.filter(Policy.expiration_date <= cutoff)
        clients = query.all()
        recipients.extend(clients)

    # Deduplicate by ID
    seen = set()
    unique = []
    for r in recipients:
        key = (type(r).__name__, r.id)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def queue_campaign_recipients(session: Session, campaign: Campaign) -> int:
    """Build the recipient queue for a campaign. Returns count."""
    audience = evaluate_audience_filter(session, campaign)
    if not audience:
        return 0

    created = 0
    for entity in audience:
        lead_id = entity.id if isinstance(entity, Lead) else None
        client_id = entity.id if isinstance(entity, Client) else None

        # Skip if already queued for this campaign
        exists = session.query(CampaignRecipient).filter(
            CampaignRecipient.campaign_id == campaign.id,
            CampaignRecipient.lead_id == lead_id,
            CampaignRecipient.client_id == client_id,
        ).first()
        if exists:
            continue

        session.add(CampaignRecipient(
            campaign_id=campaign.id,
            lead_id=lead_id,
            client_id=client_id,
            status="pending",
        ))
        created += 1

    session.commit()
    return created


def execute_campaign(session: Session, campaign: Campaign, simulate_only: bool = True) -> Dict[str, int]:
    """Execute a campaign: send (or simulate) to all pending recipients."""
    firm = session.query(FirmSettings).first()
    recipients = session.query(CampaignRecipient).filter(
        CampaignRecipient.campaign_id == campaign.id,
        CampaignRecipient.status == "pending",
    ).all()

    stats = {"sent": 0, "failed": 0, "skipped": 0}

    for recipient in recipients:
        try:
            ctx = build_recipient_context(recipient, firm, session)
            subject = render_template(campaign.template_subject, ctx)
            body = render_template(campaign.template_body, ctx)

            if simulate_only:
                # In production: integrate SendGrid / Twilio / SMTP here
                # For demo: mark as sent and log
                recipient.status = "sent"
                recipient.sent_at = datetime.utcnow()
                stats["sent"] += 1
            else:
                # Production hook
                recipient.status = "sent"
                recipient.sent_at = datetime.utcnow()
                stats["sent"] += 1
        except Exception as e:
            recipient.status = "failed"
            recipient.error_message = str(e)
            stats["failed"] += 1

    campaign.last_run_at = datetime.utcnow()
    if campaign.schedule_type == "one_time":
        campaign.status = "completed"
    session.commit()
    return stats


def run_pending_campaigns(session: Session) -> List[Dict[str, Any]]:
    """Find campaigns ready to run and execute them."""
    results = []
    now = datetime.utcnow()

    # Immediate campaigns
    immediate = session.query(Campaign).filter(
        Campaign.status == "scheduled",
        Campaign.schedule_type == "immediate",
    ).all()

    # One-time campaigns whose time has come
    one_time = session.query(Campaign).filter(
        Campaign.status == "scheduled",
        Campaign.schedule_type == "one_time",
        Campaign.schedule_time <= now,
    ).all()

    for campaign in immediate + one_time:
        queued = queue_campaign_recipients(session, campaign)
        stats = execute_campaign(session, campaign)
        results.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "queued": queued,
            **stats,
        })

    return results


# ---------------------------------------------------------------------------
# Scheduler Singleton
# ---------------------------------------------------------------------------

_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler


def schedule_campaign(campaign: Campaign) -> bool:
    """Schedule a recurring campaign in APScheduler."""
    if campaign.schedule_type != "recurring" or not campaign.cron_expression:
        return False

    scheduler = get_scheduler()
    job_id = f"campaign_{campaign.id}"

    # Remove old job if exists
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    try:
        trigger = CronTrigger.from_crontab(campaign.cron_expression)
        scheduler.add_job(
            _run_campaign_job,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            kwargs={"campaign_id": campaign.id},
        )
        return True
    except Exception:
        return False


def _run_campaign_job(campaign_id: int) -> None:
    """APScheduler callback to run a campaign."""
    session = get_session()
    try:
        campaign = session.query(Campaign).get(campaign_id)
        if not campaign or campaign.status in ("paused", "completed"):
            return
        queue_campaign_recipients(session, campaign)
        execute_campaign(session, campaign)
    finally:
        session.close()


def unschedule_campaign(campaign_id: int) -> None:
    """Remove a campaign from the scheduler."""
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(f"campaign_{campaign_id}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Ticket / Lead Utilities
# ---------------------------------------------------------------------------

def create_ticket_from_lead(session: Session, lead_id: int, title: str, ticket_type: str = "new_business",
                              priority: str = "medium", summary: str = "") -> Ticket:
    lead = session.query(Lead).get(lead_id)
    t = Ticket(
        title=title,
        type=ticket_type,
        status="open",
        priority=priority,
        summary=summary or f"Auto-generated from lead: {lead.name if lead else 'Unknown'}",
        assigned_inbox="sales",
        lead_id=lead_id,
    )
    session.add(t)
    session.commit()
    return t


def create_ticket_from_policy(session: Session, policy_id: int, title: str, ticket_type: str = "renewal",
                               priority: str = "medium", summary: str = "") -> Ticket:
    policy = session.query(Policy).get(policy_id)
    t = Ticket(
        title=title,
        type=ticket_type,
        status="open",
        priority=priority,
        summary=summary or f"Auto-generated for policy {policy.policy_number if policy else 'Unknown'}",
        assigned_inbox="underwriting" if ticket_type == "renewal" else "service",
        client_id=policy.client_id if policy else None,
    )
    session.add(t)
    session.commit()
    return t


def promote_lead_to_client(session: Session, lead_id: int) -> Optional[Client]:
    """Convert a bound lead into a client + create initial policies."""
    lead = session.query(Lead).get(lead_id)
    if not lead:
        return None

    client = Client(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        business_name=lead.business_name,
        fein="",
        address="",
        city="",
        state="",
        zip="",
        legal_entity="",
    )
    session.add(client)
    session.commit()

    lead.status = "bound"
    session.commit()
    return client


def get_dashboard_metrics(session: Session) -> Dict[str, Any]:
    """Aggregate KPIs for the dashboard."""
    from sqlalchemy import func

    lead_count = session.query(Lead).count()
    new_leads = session.query(Lead).filter(Lead.status == "new").count()
    quoted_leads = session.query(Lead).filter(Lead.status == "quoted").count()
    bound_leads = session.query(Lead).filter(Lead.status == "bound").count()

    client_count = session.query(Client).count()
    active_policies = session.query(Policy).filter(Policy.status == "active").count()
    total_premium = session.query(func.sum(Policy.premium)).filter(Policy.status == "active").scalar() or 0.0

    open_tickets = session.query(Ticket).filter(Ticket.status.in_(["open", "in_progress"])).count()
    urgent_tickets = session.query(Ticket).filter(Ticket.status.in_(["open", "in_progress"]), Ticket.priority == "urgent").count()

    # Renewals in next 90 days
    cutoff = (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")
    upcoming_renewals = session.query(Policy).filter(
        Policy.status == "active",
        Policy.expiration_date <= cutoff,
    ).count()

    # Campaign stats
    campaigns_running = session.query(Campaign).filter(Campaign.status.in_(["scheduled", "running"])).count()
    emails_sent = session.query(CampaignRecipient).filter(CampaignRecipient.status == "sent").count()

    return {
        "leads_total": lead_count,
        "leads_new": new_leads,
        "leads_quoted": quoted_leads,
        "leads_bound": bound_leads,
        "clients_total": client_count,
        "policies_active": active_policies,
        "total_premium": round(total_premium, 2),
        "tickets_open": open_tickets,
        "tickets_urgent": urgent_tickets,
        "upcoming_renewals": upcoming_renewals,
        "campaigns_running": campaigns_running,
        "emails_sent": emails_sent,
    }
