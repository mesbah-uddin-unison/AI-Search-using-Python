"""
Streamlit UI for Procurement Query Extraction.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import json

from app.services.extraction import get_extraction_service
from app.core.config import get_settings

# Page config
st.set_page_config(
    page_title="Procurement Query Extractor",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 Procurement Query Extractor")
st.markdown("Convert natural language questions about federal procurement contracts into structured filters.")

# Sidebar for example queries
with st.sidebar:
    st.markdown("### Example Queries")
    st.markdown("""
    - Show me IT contracts over $1M in FY 2024
    - Recent small business solicitations for construction services
    - Contracts awarded to Boeing in the last 2 years
    - HUBZone awards for facility maintenance
    - PSC code D308 contracts over $500K
    """)

# Main input
query = st.text_area(
    "Enter your procurement query:",
    placeholder="e.g., Show me IT services contracts over $1 million awarded in fiscal year 2024",
    height=100
)

# Extract button
if st.button("Extract Filters", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Extracting structured filters..."):
            try:
                service = get_extraction_service()
                result = service.extract(query=query)

                st.success("Extraction complete!")

                # Display results in tabs
                tab1, tab2 = st.tabs(["📊 Structured View", "📝 JSON Output"])

                with tab1:
                    # Original query
                    st.subheader("Original Query")
                    st.info(result.get("original_query", query))

                    # Group operator
                    group_op = result.get("group_operator_between_groups")
                    if group_op:
                        st.subheader("Group Operator")
                        st.write(f"Filter groups are combined with: **{group_op}**")

                    # Filter groups
                    st.subheader("Filter Groups")
                    filter_groups = result.get("filter_groups", [])

                    for i, group in enumerate(filter_groups):
                        with st.expander(f"Filter Group {i + 1}", expanded=True):
                            cols = st.columns(2)

                            col_idx = 0

                            # Subdoctype
                            if group.get("subdoctype"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Document Type**")
                                    subdoc = group["subdoctype"]
                                    if subdoc.get("value"):
                                        st.write(f"`{subdoc['operator']}` {subdoc['value']}")
                                    elif subdoc.get("values"):
                                        st.write(f"`{subdoc['operator']}` {', '.join(subdoc['values'])}")
                                col_idx += 1

                            # Date
                            if group.get("date"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Date**")
                                    date = group["date"]
                                    if date.get("value"):
                                        st.write(f"`{date['operator']}` {date['value']}")
                                    else:
                                        st.write(f"`{date['operator']}` {date.get('start_date')} to {date.get('end_date')}")
                                    if date.get("recent_days"):
                                        st.caption(f"Recent days: {date['recent_days']}")
                                col_idx += 1

                            # Total Amount
                            if group.get("total_amount"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Total Amount**")
                                    amt = group["total_amount"]
                                    if amt.get("value"):
                                        st.write(f"`{amt['operator']}` ${amt['value']:,.0f}")
                                    else:
                                        st.write(f"`{amt['operator']}` ${amt.get('min_value', 0):,.0f} - ${amt.get('max_value', 0):,.0f}")
                                col_idx += 1

                            # Funded Amount
                            if group.get("funded_amount"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Funded Amount**")
                                    amt = group["funded_amount"]
                                    if amt.get("value"):
                                        st.write(f"`{amt['operator']}` ${amt['value']:,.0f}")
                                    else:
                                        st.write(f"`{amt['operator']}` ${amt.get('min_value', 0):,.0f} - ${amt.get('max_value', 0):,.0f}")
                                col_idx += 1

                            # Vendor
                            if group.get("vendor"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Vendor**")
                                    vendor = group["vendor"]
                                    if vendor.get("value"):
                                        st.write(f"`{vendor['operator']}` {vendor['value']}")
                                    elif vendor.get("values"):
                                        st.write(f"`{vendor['operator']}` {', '.join(vendor['values'])}")
                                col_idx += 1

                            # Set Aside
                            if group.get("set_aside"):
                                with cols[col_idx % 2]:
                                    st.markdown("**Set-Aside**")
                                    sa = group["set_aside"]
                                    desc = sa.get("description", "N/A")
                                    codes = sa.get("code", [])
                                    st.write(f"{desc}")
                                    if codes:
                                        st.caption(f"Codes: {', '.join(codes)}")
                                col_idx += 1

                            # PSC Info (product_service_code)
                            if group.get("product_service_code"):
                                st.markdown("---")
                                st.markdown("**PSC Information (Product Service Code)**")
                                psc = group["product_service_code"]
                                psc_cols = st.columns(4)

                                with psc_cols[0]:
                                    if psc.get("psc_code"):
                                        st.write(f"**Codes:** {', '.join(psc['psc_code'])}")
                                    else:
                                        st.write("**Codes:** None specified")

                                with psc_cols[1]:
                                    if psc.get("description"):
                                        st.write(f"**Description:** {psc['description']}")

                                with psc_cols[2]:
                                    if psc.get("level1"):
                                        st.write(f"**Level 1:** {psc['level1']['code']} - {psc['level1']['description']}")

                                with psc_cols[3]:
                                    if psc.get("level2"):
                                        st.write(f"**Level 2:** {psc['level2']['code']} - {psc['level2']['description']}")

                            # NAICS Info (industry_code)
                            if group.get("industry_code"):
                                st.markdown("---")
                                st.markdown("**NAICS Information (Industry Code)**")
                                naics = group["industry_code"]
                                naics_cols = st.columns(4)

                                with naics_cols[0]:
                                    if naics.get("naics_code"):
                                        st.write(f"**Codes:** {', '.join(naics['naics_code'])}")
                                    else:
                                        st.write("**Codes:** None specified")

                                with naics_cols[1]:
                                    if naics.get("description"):
                                        st.write(f"**Description:** {naics['description']}")

                                with naics_cols[2]:
                                    if naics.get("level1"):
                                        st.write(f"**Level 1:** {naics['level1']['code']} - {naics['level1']['description']}")

                                with naics_cols[3]:
                                    if naics.get("level2"):
                                        st.write(f"**Level 2:** {naics['level2']['code']} - {naics['level2']['description']}")

                with tab2:
                    st.json(result)

                    # Copy button
                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="extraction_result.json",
                        mime="application/json"
                    )

            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")

# Footer
st.markdown("---")
st.caption("Procurement Query Extraction API | Powered by Azure OpenAI")
