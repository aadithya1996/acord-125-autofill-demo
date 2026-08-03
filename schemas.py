"""
JSON schema for ACORD 125 input data.
All fields are optional to allow flexible demo editing.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Producer(BaseModel):
    full_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Policy(BaseModel):
    status: Optional[str] = None
    effective_date: Optional[str] = None
    effective_time: Optional[str] = None
    expiration_date: Optional[str] = None


class NamedInsured(BaseModel):
    full_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    fein: Optional[str] = None
    sic_code: Optional[str] = None
    naics_code: Optional[str] = None
    phone: Optional[str] = None
    legal_entity: Optional[str] = None  # Corporation, LLC, Partnership, Individual, NonProfit, SubchapterS, JointVenture, Trust, Other


class Contact(BaseModel):
    description: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Location(BaseModel):
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    full_time_employees: Optional[str] = None
    annual_revenue: Optional[str] = None
    operations_description: Optional[str] = None


class BusinessType(BaseModel):
    type: Optional[str] = None  # Apartments, Condominiums, Contractor, Institutional, Manufacturing, Office, Restaurant, Retail, Service, Wholesale, Other
    other_description: Optional[str] = None
    business_start_date: Optional[str] = None


class PriorCoverage(BaseModel):
    policy_year: Optional[str] = None
    gl_insurer: Optional[str] = None
    gl_policy_number: Optional[str] = None
    gl_effective_date: Optional[str] = None
    gl_expiration_date: Optional[str] = None


class LossHistory(BaseModel):
    no_prior_losses: Optional[bool] = None


class Acord125Input(BaseModel):
    producer: Optional[Producer] = Field(default_factory=Producer)
    policy: Optional[Policy] = Field(default_factory=Policy)
    lines_of_business: Optional[Dict[str, Any]] = Field(default_factory=dict)
    named_insured: Optional[NamedInsured] = Field(default_factory=NamedInsured)
    contact: Optional[Contact] = Field(default_factory=Contact)
    location: Optional[Location] = Field(default_factory=Location)
    business_type: Optional[BusinessType] = Field(default_factory=BusinessType)
    prior_coverage: Optional[PriorCoverage] = Field(default_factory=PriorCoverage)
    loss_history: Optional[LossHistory] = Field(default_factory=LossHistory)
