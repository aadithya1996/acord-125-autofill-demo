"""
Maps clean JSON data to exact ACORD 125 PDF AcroForm field names.
Handles text fields and checkbox fields (on-state: /1).
"""

from typing import Dict, Any
from pypdf.generic import NameObject


# Mapping of policy status strings to PDF checkbox fields
POLICY_STATUS_MAP = {
    "Quote": "F[0].P1[0].Policy_Status_QuoteIndicator_A[0]",
    "Issue": "F[0].P1[0].Policy_Status_IssueIndicator_A[0]",
    "Renew": "F[0].P1[0].Policy_Status_RenewIndicator_A[0]",
    "Bound": "F[0].P1[0].Policy_Status_BoundIndicator_A[0]",
    "Change": "F[0].P1[0].Policy_Status_ChangeIndicator_A[0]",
    "Cancel": "F[0].P1[0].Policy_Status_CancelIndicator_A[0]",
}

# Mapping of legal entity strings to PDF checkbox fields
LEGAL_ENTITY_MAP = {
    "Corporation": "F[0].P1[0].NamedInsured_LegalEntity_CorporationIndicator_A[0]",
    "LLC": "F[0].P1[0].NamedInsured_LegalEntity_LimitedLiabilityCorporationIndicator_A[0]",
    "Partnership": "F[0].P1[0].NamedInsured_LegalEntity_PartnershipIndicator_A[0]",
    "Individual": "F[0].P1[0].NamedInsured_LegalEntity_IndividualIndicator_A[0]",
    "NonProfit": "F[0].P1[0].NamedInsured_LegalEntity_NotForProfitIndicator_A[0]",
    "SubchapterS": "F[0].P1[0].NamedInsured_LegalEntity_SubchapterSCorporationIndicator_A[0]",
    "JointVenture": "F[0].P1[0].NamedInsured_LegalEntity_JointVentureIndicator_A[0]",
    "Trust": "F[0].P1[0].NamedInsured_LegalEntity_TrustIndicator_A[0]",
    "Other": "F[0].P1[0].NamedInsured_LegalEntity_OtherIndicator_A[0]",
}

# Mapping of lines of business to PDF checkbox + premium fields
LOB_MAP = {
    "general_liability": {
        "checkbox": "F[0].P1[0].Policy_LineOfBusiness_CommercialGeneralLiability_A[0]",
        "premium": "F[0].P1[0].GeneralLiabilityLineOfBusiness_TotalPremiumAmount_A[0]",
    },
    "commercial_property": {
        "checkbox": "F[0].P1[0].Policy_LineOfBusiness_CommercialProperty_A[0]",
        "premium": "F[0].P1[0].CommercialPropertyLineOfBusiness_PremiumAmount_A[0]",
    },
    "business_owners": {
        "checkbox": "F[0].P1[0].Policy_LineOfBusiness_BusinessOwnersIndicator_A[0]",
        "premium": "F[0].P1[0].BusinessOwnersLineOfBusiness_PremiumAmount_A[0]",
    },
    "cyber_and_privacy": {
        "checkbox": "F[0].P1[0].Policy_LineOfBusiness_CyberAndPrivacy_A[0]",
        "premium": "F[0].P1[0].CyberAndPrivacyLineOfBusiness_PremiumAmount_A[0]",
    },
}

# Mapping of business type strings to PDF checkbox fields
BUSINESS_TYPE_MAP = {
    "Apartments": "F[0].P2[0].BusinessInformation_BusinessType_ApartmentsIndicator_A[0]",
    "Condominiums": "F[0].P2[0].BusinessInformation_BusinessType_CondominiumsIndicator_A[0]",
    "Contractor": "F[0].P2[0].BusinessInformation_BusinessType_ContractorIndicator_A[0]",
    "Institutional": "F[0].P2[0].BusinessInformation_BusinessType_InstitutionalIndicator_A[0]",
    "Manufacturing": "F[0].P2[0].BusinessInformation_BusinessType_ManufacturingIndicator_A[0]",
    "Office": "F[0].P2[0].BusinessInformation_BusinessType_OfficeIndicator_A[0]",
    "Restaurant": "F[0].P2[0].BusinessInformation_BusinessType_RestaurantIndicator_A[0]",
    "Retail": "F[0].P2[0].BusinessInformation_BusinessType_RetailIndicator_A[0]",
    "Service": "F[0].P2[0].BusinessInformation_BusinessType_ServiceIndicator_A[0]",
    "Wholesale": "F[0].P2[0].BusinessInformation_BusinessType_WholesaleIndicator_A[0]",
    "Other": "F[0].P2[0].BusinessInformation_BusinessType_OtherIndicator_A[0]",
}


def _checkbox_value(selected: bool) -> NameObject:
    """Return /1 for selected, /Off for unselected."""
    return NameObject("/1") if selected else NameObject("/Off")


def map_data_to_pdf_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert the structured JSON input into a flat dict of
    {fully_qualified_pdf_field_name: value}.
    """
    pdf_data: Dict[str, Any] = {}

    # --- Page 1: Producer ---
    producer = data.get("producer") or {}
    if producer.get("full_name"):
        pdf_data["F[0].P1[0].Producer_FullName_A[0]"] = producer["full_name"]
    if producer.get("address_line1"):
        pdf_data["F[0].P1[0].Producer_MailingAddress_LineOne_A[0]"] = producer["address_line1"]
    if producer.get("address_line2"):
        pdf_data["F[0].P1[0].Producer_MailingAddress_LineTwo_A[0]"] = producer["address_line2"]
    if producer.get("city"):
        pdf_data["F[0].P1[0].Producer_MailingAddress_CityName_A[0]"] = producer["city"]
    if producer.get("state"):
        pdf_data["F[0].P1[0].Producer_MailingAddress_StateOrProvinceCode_A[0]"] = producer["state"]
    if producer.get("zip"):
        pdf_data["F[0].P1[0].Producer_MailingAddress_PostalCode_A[0]"] = producer["zip"]
    if producer.get("contact_name"):
        pdf_data["F[0].P1[0].Producer_ContactPerson_FullName_A[0]"] = producer["contact_name"]
    if producer.get("phone"):
        pdf_data["F[0].P1[0].Producer_ContactPerson_PhoneNumber_A[0]"] = producer["phone"]
    if producer.get("email"):
        pdf_data["F[0].P1[0].Producer_ContactPerson_EmailAddress_A[0]"] = producer["email"]

    # --- Page 1: Policy ---
    policy = data.get("policy") or {}
    status = policy.get("status")
    if status:
        for status_name, field_name in POLICY_STATUS_MAP.items():
            pdf_data[field_name] = _checkbox_value(status_name == status)

    if policy.get("effective_date"):
        pdf_data["F[0].P1[0].Policy_Status_EffectiveDate_A[0]"] = policy["effective_date"]
    if policy.get("effective_time"):
        pdf_data["F[0].P1[0].Policy_Status_EffectiveTime_A[0]"] = policy["effective_time"]
    if policy.get("expiration_date"):
        pdf_data["F[0].P1[0].Policy_ExpirationDate_A[0]"] = policy["expiration_date"]

    # --- Page 1: Lines of Business ---
    lobs = data.get("lines_of_business") or {}
    for lob_key, lob_config in lobs.items():
        mapping = LOB_MAP.get(lob_key)
        if not mapping:
            continue
        is_selected = bool(lob_config.get("selected")) if isinstance(lob_config, dict) else False
        premium = ""
        if isinstance(lob_config, dict):
            premium = str(lob_config.get("premium", ""))
        pdf_data[mapping["checkbox"]] = _checkbox_value(is_selected)
        if premium:
            pdf_data[mapping["premium"]] = premium

    # --- Page 1: Named Insured ---
    insured = data.get("named_insured") or {}
    if insured.get("full_name"):
        pdf_data["F[0].P1[0].NamedInsured_FullName_A[0]"] = insured["full_name"]
    if insured.get("address_line1"):
        pdf_data["F[0].P1[0].NamedInsured_MailingAddress_LineOne_A[0]"] = insured["address_line1"]
    if insured.get("address_line2"):
        pdf_data["F[0].P1[0].NamedInsured_MailingAddress_LineTwo_A[0]"] = insured["address_line2"]
    if insured.get("city"):
        pdf_data["F[0].P1[0].NamedInsured_MailingAddress_CityName_A[0]"] = insured["city"]
    if insured.get("state"):
        pdf_data["F[0].P1[0].NamedInsured_MailingAddress_StateOrProvinceCode_A[0]"] = insured["state"]
    if insured.get("zip"):
        pdf_data["F[0].P1[0].NamedInsured_MailingAddress_PostalCode_A[0]"] = insured["zip"]
    if insured.get("fein"):
        pdf_data["F[0].P1[0].NamedInsured_TaxIdentifier_A[0]"] = insured["fein"]
    if insured.get("sic_code"):
        pdf_data["F[0].P1[0].NamedInsured_SICCode_A[0]"] = insured["sic_code"]
    if insured.get("naics_code"):
        pdf_data["F[0].P1[0].NamedInsured_NAICSCode_A[0]"] = insured["naics_code"]
    if insured.get("phone"):
        pdf_data["F[0].P1[0].NamedInsured_Primary_PhoneNumber_A[0]"] = insured["phone"]

    # Legal entity checkbox
    entity = insured.get("legal_entity")
    if entity:
        for entity_name, field_name in LEGAL_ENTITY_MAP.items():
            pdf_data[field_name] = _checkbox_value(entity_name == entity)

    # --- Page 2: Contact ---
    contact = data.get("contact") or {}
    if contact.get("description"):
        pdf_data["F[0].P2[0].NamedInsured_Contact_ContactDescription_A[0]"] = contact["description"]
    if contact.get("full_name"):
        pdf_data["F[0].P2[0].NamedInsured_Contact_FullName_A[0]"] = contact["full_name"]
    if contact.get("phone"):
        pdf_data["F[0].P2[0].NamedInsured_Contact_PrimaryPhoneNumber_A[0]"] = contact["phone"]
    if contact.get("email"):
        pdf_data["F[0].P2[0].NamedInsured_Contact_PrimaryEmailAddress_A[0]"] = contact["email"]

    # --- Page 2: Location ---
    location = data.get("location") or {}
    if location.get("address_line1"):
        pdf_data["F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_A[0]"] = location["address_line1"]
    if location.get("address_line2"):
        pdf_data["F[0].P2[0].CommercialStructure_PhysicalAddress_LineTwo_A[0]"] = location["address_line2"]
    if location.get("city"):
        pdf_data["F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_A[0]"] = location["city"]
    if location.get("state"):
        pdf_data["F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_A[0]"] = location["state"]
    if location.get("zip"):
        pdf_data["F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_A[0]"] = location["zip"]
    if location.get("full_time_employees"):
        pdf_data["F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_A[0]"] = location["full_time_employees"]
    if location.get("annual_revenue"):
        pdf_data["F[0].P2[0].CommercialStructure_AnnualRevenueAmount_A[0]"] = location["annual_revenue"]
    if location.get("operations_description"):
        pdf_data["F[0].P2[0].BuildingOccupancy_OperationsDescription_A[0]"] = location["operations_description"]

    # --- Page 2: Business Type ---
    biz_type = data.get("business_type") or {}
    bt = biz_type.get("type")
    if bt:
        for type_name, field_name in BUSINESS_TYPE_MAP.items():
            pdf_data[field_name] = _checkbox_value(type_name == bt)
    if biz_type.get("other_description"):
        pdf_data["F[0].P2[0].BusinessInformation_BusinessType_OtherDescription_A[0]"] = biz_type["other_description"]
    if biz_type.get("business_start_date"):
        pdf_data["F[0].P2[0].NamedInsured_BusinessStartDate_A[0]"] = biz_type["business_start_date"]

    # --- Page 3-4: Prior Coverage (light touch) ---
    prior = data.get("prior_coverage") or {}
    if prior.get("policy_year"):
        pdf_data["F[0].P3[0].PriorCoverage_PolicyYear_A[0]"] = prior["policy_year"]
    if prior.get("gl_insurer"):
        pdf_data["F[0].P3[0].PriorCoverage_GeneralLiability_InsurerFullName_A[0]"] = prior["gl_insurer"]
    if prior.get("gl_policy_number"):
        pdf_data["F[0].P3[0].PriorCoverage_GeneralLiability_PolicyNumberIdentifier_A[0]"] = prior["gl_policy_number"]
    if prior.get("gl_effective_date"):
        pdf_data["F[0].P3[0].PriorCoverage_GeneralLiability_EffectiveDate_A[0]"] = prior["gl_effective_date"]
    if prior.get("gl_expiration_date"):
        pdf_data["F[0].P3[0].PriorCoverage_GeneralLiability_ExpirationDate_A[0]"] = prior["gl_expiration_date"]

    # --- Page 4: Loss History (light touch) ---
    loss = data.get("loss_history") or {}
    if loss.get("no_prior_losses") is not None:
        pdf_data["F[0].P4[0].LossHistory_NoPriorLossesIndicator_A[0]"] = _checkbox_value(bool(loss["no_prior_losses"]))

    return pdf_data
