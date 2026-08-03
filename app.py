"""
Streamlit demo UI for the ACORD 125 auto-fill service.

Layout:
  Left: Quick Edit Form for common fields
  Right: Live JSON display (read-only, always accurate) + Raw JSON editor expander
"""

import json
import io
from pathlib import Path
from typing import Dict, Any

import streamlit as st

from schemas import Acord125Input
from field_mapper import map_data_to_pdf_fields
from pdf_filler import fill_acord_125


SAMPLE_DIR = Path(__file__).parent / "sample_data"
SCENARIOS = {
    "Tech Startup": SAMPLE_DIR / "tech_startup.json",
    "Restaurant Chain": SAMPLE_DIR / "restaurant_chain.json",
    "Construction Business": SAMPLE_DIR / "construction_business.json",
    "Custom (blank)": None,
}


def load_scenario(name: str) -> str:
    """Load the selected scenario JSON as a formatted string."""
    path = SCENARIOS.get(name)
    if path and path.exists():
        with open(path, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    return "{}"


def get_json_data() -> Dict[str, Any]:
    """Parse the current JSON text from session state safely."""
    try:
        return json.loads(st.session_state.json_text)
    except Exception:
        return {}


def set_json_data(data: Dict[str, Any]):
    """Serialize data back to the JSON text area in session state."""
    st.session_state.json_text = json.dumps(data, indent=2)


def main():
    st.set_page_config(
        page_title="ACORD 125 Auto-Fill Demo",
        page_icon="📋",
        layout="wide",
    )

    st.title("📋 ACORD 125 Commercial Insurance Auto-Fill")
    st.markdown(
        "Select a scenario, edit key fields in the form (or edit raw JSON), and generate a filled ACORD 125 PDF instantly."
    )
    st.divider()

    # --- Sidebar with quick reference ---
    with st.sidebar:
        st.header("Quick Reference")
        st.markdown("**Policy Status:** `Quote`, `Issue`, `Renew`, `Bound`, `Change`, `Cancel`")
        st.markdown("**Legal Entity:** `Corporation`, `LLC`, `Partnership`, `Individual`, `NonProfit`, `SubchapterS`, `JointVenture`, `Trust`, `Other`")
        st.markdown("**Business Type:** `Apartments`, `Condominiums`, `Contractor`, `Institutional`, `Manufacturing`, `Office`, `Restaurant`, `Retail`, `Service`, `Wholesale`, `Other`")
        st.markdown("**LOB Keys:** `general_liability`, `commercial_property`, `business_owners`, `cyber_and_privacy`")
        st.divider()
        st.caption("Fields mapped: ~40 high-impact fields across Pages 1–4.")

    # --- Scenario selector ---
    scenario_name = st.selectbox(
        "Choose a demo scenario",
        options=list(SCENARIOS.keys()),
        index=0,
    )

    # Load JSON when scenario changes
    if st.session_state.get("last_scenario") != scenario_name:
        st.session_state.json_text = load_scenario(scenario_name)
        st.session_state.last_scenario = scenario_name
        st.session_state.pop("generated_pdf", None)
        # Reset the raw JSON editor state so it matches the new scenario
        if "json_editor" in st.session_state:
            st.session_state["json_editor"] = st.session_state.json_text

    if "json_text" not in st.session_state:
        st.session_state.json_text = load_scenario(scenario_name)
    if "last_scenario" not in st.session_state:
        st.session_state.last_scenario = scenario_name

    data = get_json_data()

    # ------------------------------------------------------------------
    # TWO-COLUMN LAYOUT: Quick Edit Form + Live JSON Display
    # ------------------------------------------------------------------
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Quick Edit Form")
        st.caption("Edit the most common fields directly. The JSON on the right updates automatically.")

        # -- Named Insured --
        st.markdown("**Named Insured**")
        insured = data.get("named_insured") or {}
        new_insured_name = st.text_input("Full Name", value=insured.get("full_name", ""), key="qi_insured_name")
        new_insured_addr1 = st.text_input("Address Line 1", value=insured.get("address_line1", ""), key="qi_insured_addr1")
        new_insured_city = st.text_input("City", value=insured.get("city", ""), key="qi_insured_city")
        c1, c2 = st.columns(2)
        new_insured_state = c1.text_input("State", value=insured.get("state", ""), key="qi_insured_state", max_chars=2)
        new_insured_zip = c2.text_input("ZIP", value=insured.get("zip", ""), key="qi_insured_zip", max_chars=10)
        new_fein = st.text_input("FEIN / Tax ID", value=insured.get("fein", ""), key="qi_fein")

        # -- Policy --
        st.markdown("**Policy**")
        policy = data.get("policy") or {}
        status_options = ["Quote", "Issue", "Renew", "Bound", "Change", "Cancel"]
        current_status = policy.get("status", "Quote")
        try:
            status_index = status_options.index(current_status)
        except ValueError:
            status_index = 0
        new_status = st.selectbox("Policy Status", options=status_options, index=status_index, key="qi_status")
        d1, d2 = st.columns(2)
        new_eff_date = d1.text_input("Effective Date", value=policy.get("effective_date", ""), key="qi_eff_date")
        new_exp_date = d2.text_input("Expiration Date", value=policy.get("expiration_date", ""), key="qi_exp_date")

        # -- Business Info --
        st.markdown("**Business Info**")
        biz = data.get("business_type") or {}
        biz_options = ["Apartments", "Condominiums", "Contractor", "Institutional", "Manufacturing", "Office", "Restaurant", "Retail", "Service", "Wholesale", "Other"]
        current_biz = biz.get("type", "Office")
        try:
            biz_index = biz_options.index(current_biz)
        except ValueError:
            biz_index = 6
        new_biz_type = st.selectbox("Business Type", options=biz_options, index=biz_index, key="qi_biz_type")

        legal_options = ["Corporation", "LLC", "Partnership", "Individual", "NonProfit", "SubchapterS", "JointVenture", "Trust", "Other"]
        current_legal = insured.get("legal_entity", "Corporation")
        try:
            legal_index = legal_options.index(current_legal)
        except ValueError:
            legal_index = 0
        new_legal_entity = st.selectbox("Legal Entity", options=legal_options, index=legal_index, key="qi_legal")

        loc = data.get("location") or {}
        new_employees = st.text_input("Full-Time Employees", value=loc.get("full_time_employees", ""), key="qi_employees")
        new_revenue = st.text_input("Annual Revenue", value=loc.get("annual_revenue", ""), key="qi_revenue")
        new_ops = st.text_area("Operations Description", value=loc.get("operations_description", ""), height=68, key="qi_ops")

        # -- Lines of Business --
        st.markdown("**Lines of Business**")
        lobs = data.get("lines_of_business") or {}
        lob_keys = ["general_liability", "commercial_property", "business_owners", "cyber_and_privacy"]
        lob_labels = ["General Liability", "Commercial Property", "Business Owners (BOP)", "Cyber & Privacy"]
        selected_lobs = []
        for key, label in zip(lob_keys, lob_labels):
            config = lobs.get(key, {})
            is_checked = bool(config.get("selected")) if isinstance(config, dict) else False
            if st.checkbox(label, value=is_checked, key=f"qi_lob_{key}"):
                selected_lobs.append(key)

        # -- Premiums --
        st.markdown("**Premiums**")
        p1, p2 = st.columns(2)
        gl_prem = str(lobs.get("general_liability", {}).get("premium", "")) if isinstance(lobs.get("general_liability"), dict) else ""
        prop_prem = str(lobs.get("commercial_property", {}).get("premium", "")) if isinstance(lobs.get("commercial_property"), dict) else ""
        new_gl_prem = p1.text_input("GL Premium", value=gl_prem, key="qi_gl_prem")
        new_prop_prem = p2.text_input("Prop Premium", value=prop_prem, key="qi_prop_prem")

        # -- Contact --
        st.markdown("**Contact**")
        contact = data.get("contact") or {}
        new_contact_name = st.text_input("Contact Name", value=contact.get("full_name", ""), key="qi_contact_name")
        new_contact_phone = st.text_input("Contact Phone", value=contact.get("phone", ""), key="qi_contact_phone")
        new_contact_email = st.text_input("Contact Email", value=contact.get("email", ""), key="qi_contact_email")

        # ------------------------------------------------------------------
        # SYNC FORM EDITS BACK INTO JSON PAYLOAD
        # ------------------------------------------------------------------
        data["named_insured"] = data.get("named_insured") or {}
        data["named_insured"]["full_name"] = new_insured_name
        data["named_insured"]["address_line1"] = new_insured_addr1
        data["named_insured"]["city"] = new_insured_city
        data["named_insured"]["state"] = new_insured_state
        data["named_insured"]["zip"] = new_insured_zip
        data["named_insured"]["fein"] = new_fein
        data["named_insured"]["legal_entity"] = new_legal_entity

        data["policy"] = data.get("policy") or {}
        data["policy"]["status"] = new_status
        data["policy"]["effective_date"] = new_eff_date
        data["policy"]["expiration_date"] = new_exp_date

        data["business_type"] = data.get("business_type") or {}
        data["business_type"]["type"] = new_biz_type

        data["location"] = data.get("location") or {}
        data["location"]["full_time_employees"] = new_employees
        data["location"]["annual_revenue"] = new_revenue
        data["location"]["operations_description"] = new_ops

        data["lines_of_business"] = data.get("lines_of_business") or {}
        for key in lob_keys:
            existing_config = data["lines_of_business"].get(key, {})
            if not isinstance(existing_config, dict):
                existing_config = {}
            existing_premium = str(existing_config.get("premium", ""))
            data["lines_of_business"][key] = {
                "selected": key in selected_lobs,
                "premium": existing_premium,
            }
        # Only update premiums for fields exposed in the form
        if new_gl_prem:
            data["lines_of_business"]["general_liability"]["premium"] = new_gl_prem
        if new_prop_prem:
            data["lines_of_business"]["commercial_property"]["premium"] = new_prop_prem

        data["contact"] = data.get("contact") or {}
        data["contact"]["full_name"] = new_contact_name
        data["contact"]["phone"] = new_contact_phone
        data["contact"]["email"] = new_contact_email

        set_json_data(data)

    with right_col:
        st.subheader("Live JSON Payload")
        st.caption("This always reflects the current form state. Edit raw JSON below for advanced changes.")
        st.code(st.session_state.json_text, language="json")

        with st.expander("✏️ Edit Raw JSON"):
            st.caption("Make advanced edits directly. Must be valid JSON.")
            raw_json = st.text_area(
                "Raw JSON editor",
                value=st.session_state.json_text,
                height=400,
                key="json_editor",
            )
            if st.button("Apply Changes", key="apply_json", use_container_width=True):
                try:
                    parsed = json.loads(raw_json)
                    # Best-effort validation
                    Acord125Input(**parsed)
                    st.session_state.json_text = raw_json
                    st.session_state["json_editor"] = raw_json
                    st.success("JSON updated! Form will refresh.")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON syntax: {e}")
                except Exception as e:
                    st.error(f"Validation error: {e}")

    # ------------------------------------------------------------------
    # GENERATE PDF
    # ------------------------------------------------------------------
    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_clicked = st.button("⚡ Generate PDF", type="primary", use_container_width=True)

    if generate_clicked:
        try:
            data = json.loads(st.session_state.json_text)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            return

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
            st.success("✅ PDF generated successfully! Download below.")
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
        st.info(
            "The downloaded PDF retains editable AcroForm fields so you can inspect or tweak values directly."
        )


if __name__ == "__main__":
    main()
