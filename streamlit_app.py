import streamlit as st
import requests

# ============================================================
# PEOPLE ANALYTICS DASHBOARD
# ============================================================

WEBHOOK_URL = "https://n8n.umirai.ai/webhook/people-analytics"

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("People Analytics Dashboard")
st.caption("Workforce insights powered by your People Analytics workflow")

# ------------------------------------------------------------
# QUESTION
# ------------------------------------------------------------

question = st.text_input(
    "Ask a People Analytics question",
    placeholder="Example: Compare new joiners and exits between FY 2023-24 and FY 2025-26"
)

# ------------------------------------------------------------
# ANALYZE
# ------------------------------------------------------------

if st.button("Analyze", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing workforce data..."):

        try:
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "user_question": question
                },
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

        except Exception as e:
            st.error(f"Unable to connect to the analytics workflow: {e}")
            st.stop()

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    answer = result.get("answer", "")

    if answer:
        st.subheader("Analysis")
        st.write(answer)

    # --------------------------------------------------------
    # CHART DATA
    # --------------------------------------------------------

    chart_required = result.get("chart_required", False)

    if not chart_required:
        st.info("No chart required for this question.")
        st.stop()

    chart_type = result.get("chart_type", "bar")
    chart_title = result.get("chart_title", "")
    labels = result.get("chart_labels", [])
    datasets = result.get("chart_datasets", [])

    if not labels or not datasets:
        st.warning("Chart was requested but no chart data was returned.")
        st.stop()

    # --------------------------------------------------------
    # CHART TITLE
    # --------------------------------------------------------

    if chart_title:
        st.subheader(chart_title)

    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    if chart_type == "bar":

        chart_data = {}

        for dataset in datasets:
            label = dataset.get("label", "Value")
            values = dataset.get("data", [])

            chart_data[label] = values

        chart_data["Category"] = labels

        # Streamlit native bar chart expects categories as index
        chart_rows = []

        for i, category in enumerate(labels):

            row = {
                "Category": category
            }

            for dataset in datasets:

                label = dataset.get("label", "Value")
                values = dataset.get("data", [])

                if i < len(values):
                    row[label] = values[i]
                else:
                    row[label] = 0

            chart_rows.append(row)

        # Build simple table-like structure without pandas
        categories = [row["Category"] for row in chart_rows]

        chart_columns = {}

        for dataset in datasets:

            label = dataset.get("label", "Value")
            values = dataset.get("data", [])

            chart_columns[label] = values

        st.bar_chart(
            chart_columns,
            x=None,
            y=None,
            height=500
        )

        # Show exact values below chart
        with st.expander("View chart values"):

            for dataset in datasets:

                label = dataset.get("label", "Value")
                values = dataset.get("data", [])

                st.write(f"**{label}**")

                for i, category in enumerate(labels):

                    if i < len(values):
                        st.write(
                            f"{category}: **{values[i]}**"
                        )

    # --------------------------------------------------------
    # LINE CHART
    # --------------------------------------------------------

    elif chart_type == "line":

        chart_data = {}

        for dataset in datasets:

            label = dataset.get("label", "Value")
            values = dataset.get("data", [])

            chart_data[label] = values

        st.line_chart(
            chart_data,
            height=500
        )

        with st.expander("View chart values"):

            for dataset in datasets:

                label = dataset.get("label", "Value")
                values = dataset.get("data", [])

                st.write(f"**{label}**")

                for i, category in enumerate(labels):

                    if i < len(values):
                        st.write(
                            f"{category}: **{values[i]}**"
                        )

    # --------------------------------------------------------
    # PIE / POLAR AREA
    # --------------------------------------------------------

    elif chart_type in ["pie", "polarArea", "doughnut"]:

        st.bar_chart(
            {
                dataset.get("label", "Value"): dataset.get("data", [])
                for dataset in datasets
            },
            height=500
        )

        st.caption(
            "Category distribution"
        )

        with st.expander("View chart values"):

            for dataset in datasets:

                label = dataset.get("label", "Value")
                values = dataset.get("data", [])

                st.write(f"**{label}**")

                for i, category in enumerate(labels):

                    if i < len(values):
                        st.write(
                            f"{category}: **{values[i]}**"
                        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    else:

        st.bar_chart(
            {
                dataset.get("label", "Value"): dataset.get("data", [])
                for dataset in datasets
            },
            height=500
        )

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    "People Analytics Decision Intelligence"
)
