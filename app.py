import streamlit as st
import pandas as pd
import json
import random
import uuid

# Configure page
st.set_page_config(page_title="RDSG Data Discovery", layout="wide")

# Inject UCSD/ACTRI Brand CSS
st.markdown("""
    
""", unsafe_allow_html=True)

# Sidebar Branding
st.sidebar.markdown("## **UCSD Health | ACTRI**")
st.sidebar.markdown("### RDSG Semantic Engine")
st.sidebar.markdown("---")
st.sidebar.markdown("**Lead Architect:** Troy M. Melander")

st.title("🔬 RDSG Semantic Data Discovery UI")
st.markdown("### Self-Service Cohort & Variable Selection")

# Exact mapping from the SSMS extraction and RDSG_METADATA_CATALOG
data = {
    "Domain": ["Demographics", "Demographics", "Demographics", "Demographics", "Demographics", "Demographics", "Geography", "Research"],
    "Field Name": ["Biological_Sex", "Current_Age", "Primary_Race", "Ethnicity", "Gender_Identity", "Preferred_Language", "State", "Research_Contact_Status"],
    "Definition": [
        "Patient sex assigned at birth", "Calculated real-time patient age", 
        "Patient self-identified race", "Patient self-identified ethnicity", 
        "Patient gender identity", "Patient preferred language", 
        "Patient state of residence", "Indicates if patient opted out of research contact"
    ],
    "OMOP Alignment": ["Gender", "Observation", "Race", "Observation", "Observation", "Observation", "Location", "Observation"]
}
df_catalog = pd.DataFrame(data)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Deployment Endpoint")
    deployment_target = st.radio(
        "Select the target system for this data request:",
        ["Epic Forward / Nightingale (Internal)", "Medeloop AI / Sandbox (External De-Identified)"]
    )
    
    st.markdown("---")
    st.header("2. Cohort Estimator")
    st.markdown("*HIPAA Safe Harbor dictates cohorts < 11 are obscured.*")
    
    if st.button("Estimate Cohort Size"):
        mock_count = random.choice([7, 45, 120, 8, 300])
        if mock_count < 11:
            st.warning("📊 Estimated Cohort: **< 11 patients** (Small Cell Suppressed)")
        else:
            st.info(f"📊 Estimated Cohort: **{mock_count} patients**")

with col2:
    st.header("3. Select Variables")
    st.markdown("Browse the semantic catalog. Selecting variables does not expose patient PHI.")
    
    selected_vars = st.multiselect(
        "Select required fields for your data manifest:",
        options=df_catalog['Field Name'].tolist(),
        default=["Biological_Sex", "Current_Age", "Primary_Race"]
    )
    
    st.markdown("#### Selected Variable Definitions")
    st.table(df_catalog[df_catalog['Field Name'].isin(selected_vars)][['Field Name', 'Definition', 'OMOP Alignment']])
    
    st.markdown("---")
    if st.button("Submit Data Request Manifest", type="primary"):
        
        # Simulate payload routing based on deployment target
        if "Epic Forward" in deployment_target:
            payload_type = "vw_RDSG_SEMANTIC_PATIENT"
            subject_key_type = "Epic_PAT_ID (Identified)"
        else:
            payload_type = "vw_RDSG_DEID_PATIENT"
            subject_key_type = "UUID Crosswalk (Safe Harbor De-Identified)"

        manifest = {
            "Deployment_Target": deployment_target,
            "Executing_View": payload_type,
            "Primary_Key_Format": subject_key_type,
            "Requested_Fields": selected_vars,
            "Status": "Approved - Routed to RDSG Automated Pipeline"
        }
        st.success("Manifest generated successfully.")
        
        # Show the executive exactly how Medeloop receives the data vs Epic
        if "Medeloop" in deployment_target:
            st.info(f"**Mock Payload Sample for {deployment_target}:**")
            mock_payload = {
                "Deidentified_Subject_ID": str(uuid.uuid4()),
                "Masked_Age": "90+" if "Current_Age" in selected_vars else "N/A",
                "Biological_Sex": "Female" if "Biological_Sex" in selected_vars else "N/A"
            }
            st.json(json.dumps(mock_payload, indent=4))
        else:
            st.info(f"**Mock Payload Sample for {deployment_target}:**")
            mock_payload = {
                "Epic_Patient_ID": "Z12345678",
                "Clinical_MRN": "99887766",
                "Current_Age": 92 if "Current_Age" in selected_vars else "N/A",
                "Biological_Sex": "Female" if "Biological_Sex" in selected_vars else "N/A"
            }
            st.json(json.dumps(mock_payload, indent=4))
