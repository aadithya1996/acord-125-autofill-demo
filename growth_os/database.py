"""
Insurance Growth OS — Database Layer
SQLite backend with SQLAlchemy ORM for demo portability.
"""

import json
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, Float,
    ForeignKey, Enum, Boolean, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

Base = declarative_base()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class FirmSettings(Base):
    __tablename__ = "firm_settings"
    id = Column(Integer, primary_key=True)
    firm_name = Column(String, default="Your Insurance Agency")
    address = Column(String)
    city = Column(String)
    state = Column(String, default="NY")
    zip = Column(String)
    phone = Column(String)
    email = Column(String)
    timezone = Column(String, default="America/New_York")


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    business_name = Column(String)
    business_type = Column(String)
    sic_code = Column(String)
    naics_code = Column(String)
    status = Column(String, default="new")          # new | qualified | quoted | bound | lost
    source = Column(String, default="website")      # website | referral | cold_call | event | other
    notes = Column(Text)
    assigned_to = Column(String, default="Unassigned")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    business_name = Column(String)
    fein = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    legal_entity = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="client")


class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    carrier = Column(String)
    policy_number = Column(String)
    line_of_business = Column(String)               # general_liability | commercial_property | bop | cyber | umbrella | workers_comp | auto | other
    premium = Column(Float, default=0.0)
    effective_date = Column(String)
    expiration_date = Column(String)
    status = Column(String, default="active")        # active | pending | cancelled | expired | renewed
    client: Mapped[Optional["Client"]] = relationship("Client", back_populates="policies")


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    type = Column(String, default="service")         # endorsement | renewal | claim | cross_sell | service | new_business | underwriting
    status = Column(String, default="open")          # open | in_progress | resolved | closed
    priority = Column(String, default="medium")      # low | medium | high | urgent
    summary = Column(Text)
    assigned_inbox = Column(String, default="sales")  # sales | underwriting | service | claims
    assigned_to = Column(String, default="Unassigned")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)                             # renewal_reminder | cross_sell | quote_follow_up | welcome | seasonal | custom
    status = Column(String, default="draft")           # draft | scheduled | running | completed | paused
    channel = Column(String, default="email")          # email | sms
    template_subject = Column(String)
    template_body = Column(Text)
    audience_filter = Column(Text)                      # JSON: {"status":"active","lob":"general_liability"}
    schedule_type = Column(String, default="immediate") # immediate | one_time | recurring
    schedule_time = Column(DateTime, nullable=True)
    cron_expression = Column(String, nullable=True)     # e.g. "0 9 * * 1" for Mondays 9am
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    recipients: Mapped[List["CampaignRecipient"]] = relationship("CampaignRecipient", back_populates="campaign")


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    status = Column(String, default="pending")          # pending | sent | opened | clicked | replied | bounced | failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="recipients")


# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///growth_os.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------

def seed_demo_data(session: Session) -> None:
    """Idempotent seed for demo scenarios."""
    # Firm settings
    if not session.query(FirmSettings).first():
        session.add(FirmSettings(
            firm_name="Metro Commercial Insurance",
            address="225 Peachtree St NE, Suite 1200",
            city="Atlanta",
            state="GA",
            zip="30303",
            phone="(404) 555-0147",
            email="info@metrocomm.com",
        ))

    # Leads
    if session.query(Lead).count() == 0:
        session.add_all([
            Lead(name="David Chen", email="d.chen@nexusdata.io", phone="(415) 555-0300",
                 business_name="Nexus Data Systems, Inc.", business_type="Office",
                 sic_code="7372", naics_code="541512", status="quoted",
                 source="website", notes="Cyber + GL + Property quote. High cyber premium.", assigned_to="Alice Nguyen"),
            Lead(name="Maria Santos", email="msantos@savbistro.com", phone="(404) 555-0299",
                 business_name="Savannah Bistro Group, LLC", business_type="Restaurant",
                 sic_code="5812", naics_code="722511", status="qualified",
                 source="referral", notes="Restaurant chain, needs GL + Property + BOP. 42 employees.", assigned_to="Carlos Rivera"),
            Lead(name="Robert Kim", email="r.kim@lakesidebuild.com", phone="(312) 555-0456",
                 business_name="Lakeside Construction Partners, LLC", business_type="Contractor",
                 sic_code="1541", naics_code="236220", status="new",
                 source="cold_call", notes="Commercial construction. 120 employees. $32M revenue.", assigned_to="James O'Brien"),
        ])

    # Clients + Policies
    if session.query(Client).count() == 0:
        c1 = Client(name="James Porter", email="j.porter@porterlogistics.com", phone="(212) 555-0199",
                    business_name="Porter Logistics, Inc.", fein="12-3456789",
                    address="450 W 33rd St", city="New York", state="NY", zip="10001", legal_entity="Corporation")
        c2 = Client(name="Sarah Mitchell", email="s.mitchell@mitchellretail.com", phone="(312) 555-0288",
                    business_name="Mitchell Retail Group, LLC", fein="98-7654321",
                    address="842 N Michigan Ave", city="Chicago", state="IL", zip="60611", legal_entity="LLC")
        session.add_all([c1, c2])
        session.flush()
        session.add_all([
            Policy(client_id=c1.id, carrier="Hartford", policy_number="GL-2025-88421",
                 line_of_business="general_liability", premium=12500.0,
                 effective_date="2025-01-15", expiration_date="2026-01-15", status="active"),
            Policy(client_id=c1.id, carrier="Hartford", policy_number="CP-2025-88422",
                 line_of_business="commercial_property", premium=8400.0,
                 effective_date="2025-01-15", expiration_date="2026-01-15", status="active"),
            Policy(client_id=c1.id, carrier="Liberty Mutual", policy_number="CY-2025-11223",
                 line_of_business="cyber_and_privacy", premium=22000.0,
                 effective_date="2025-03-01", expiration_date="2026-03-01", status="active"),
            Policy(client_id=c2.id, carrier="Zurich", policy_number="ZN-BOP-77210",
                 line_of_business="business_owners", premium=6500.0,
                 effective_date="2025-06-01", expiration_date="2026-06-01", status="active"),
            Policy(client_id=c2.id, carrier="Travelers", policy_number="TR-UMB-99543",
                 line_of_business="umbrella", premium=3200.0,
                 effective_date="2025-06-01", expiration_date="2026-06-01", status="active"),
        ])

    # Tickets
    if session.query(Ticket).count() == 0:
        session.add_all([
            Ticket(title="GL Endorsement — Additional Insured", type="endorsement",
                   status="open", priority="high", summary="Client needs vendor added as AI on GL policy before Monday.",
                   assigned_inbox="underwriting", assigned_to="Underwriting Team"),
            Ticket(title="Renewal — Nexus Data Cyber Policy", type="renewal",
                   status="in_progress", priority="medium", summary="Cyber renewal expiring 03/01. Premium increased 15%.",
                   assigned_inbox="sales", assigned_to="Alice Nguyen"),
            Ticket(title="Quote Follow-up — Lakeside Construction", type="new_business",
                   status="open", priority="medium", summary="No response after initial GL quote sent 3 days ago.",
                   assigned_inbox="sales", assigned_to="James O'Brien"),
            Ticket(title="Cross-sell Opportunity — Umbrella for Porter Logistics", type="cross_sell",
                   status="open", priority="low", summary="Client has GL + Property + Cyber but no Umbrella. $2M revenue.",
                   assigned_inbox="sales", assigned_to="Alice Nguyen"),
        ])

    # Campaigns
    if session.query(Campaign).count() == 0:
        session.add_all([
            Campaign(name="Q1 Renewal Reminders", type="renewal_reminder",
                     status="scheduled", channel="email",
                     template_subject="Your policy renews soon — let's review",
                     template_body="Hi {{name}},\n\nYour {{lob}} policy ({{policy_number}}) with {{carrier}} expires on {{expiration_date}}. Let's schedule a 10-minute review to confirm coverage and explore any changes.\n\nReply or call us at {{firm_phone}}.\n\nBest,\n{{firm_name}}",
                     audience_filter='{"status":"active","days_before_expiration":30}',
                     schedule_type="recurring", cron_expression="0 9 1 * *"),
            Campaign(name="Quote Follow-up Sequence", type="quote_follow_up",
                     status="draft", channel="email",
                     template_subject="Following up on your insurance quote",
                     template_body="Hi {{name}},\n\nWe sent you a quote for {{business_name}} a few days ago. Do you have any questions, or is there anything we can adjust to better fit your needs?\n\nBest,\n{{firm_name}}",
                     audience_filter='{"status":"quoted","days_since_quote":3}',
                     schedule_type="recurring", cron_expression="0 10 * * 1,3,5"),
            Campaign(name="Welcome New Clients", type="welcome",
                     status="scheduled", channel="email",
                     template_subject="Welcome to {{firm_name}}!",
                     template_body="Hi {{name}},\n\nThank you for trusting {{firm_name}} with {{business_name}}. Your policies are active and your certificates are attached.\n\nYour account manager is {{assigned_to}}.\n\nBest,\n{{firm_name}}",
                     audience_filter='{"status":"bound","days_since_bound":1}',
                     schedule_type="recurring", cron_expression="0 14 * * *"),
        ])

    session.commit()
