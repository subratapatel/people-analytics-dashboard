import streamlit as st
import requests
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

WEBHOOK_URL = "https://n8n.umirai.ai/webhook/people-analytics"

st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# HEADER
# ============================================================

st.title("People Analytics Dashboard")
st.caption("Workforce insights powered by People Analytics")

# ============================================================
# QUESTION
# ============================================================

question = st.text_input(
    "Ask a People Analytics question",
    placeholder="Example: Compare new joiners and exits between FY 2023-24 and FY 2025-26"
)

# ============================================================
# ANALYZE
# ============================================================

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
            st.error(f"Unable to connect to analytics workflow: {e}")
            st.stop()

    # ========================================================
    # ANSWER
    # ========================================================

    answer = result.get("answer", "")

    if answer:
        st.subheader("Analysis")
        st.write(answer)

    # ========================================================
    # CHART
    # ========================================================

    if result.get("chart_required", False):

        chart_type = result.get("chart_type", "bar")
        chart_title = result.get("chart_title", "")
        labels = result.get("chart_labels", [])
        datasets = result.get("chart_datasets", [])

        if not labels or not datasets:
            st.warning("Chart data was not returned.")
            st.stop()

        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        if chart_type == "bar":

            chart_rows = []

            for i, label in enumerate(labels):

                row = {
                    "FY": label
                }

                for dataset in datasets:

                    dataset_label = dataset.get(
                        "label",
                        "Value"
                    )

                    values = dataset.get(
                        "data",
                        []
                    )

                    row[dataset_label] = (
                        values[i]
                        if i < len(values)
                        else 0
                    )

                chart_rows.append(row)

            df = pd.DataFrame(chart_rows)

            # Keep FY as the index so FY labels appear
            # directly underneath the grouped bars.
            df = df.set_index("FY")

            # ------------------------------------------------
            # CHART TITLE
            # ------------------------------------------------

            if chart_title:
                st.subheader(chart_title)

            # ------------------------------------------------
            # GROUPED BAR CHART
            # ------------------------------------------------

            st.bar_chart(
                df,
                height=500
            )

            # ------------------------------------------------
            # VALUE DISPLAY
            # ------------------------------------------------

            st.markdown("### Values")

            st.dataframe(
                df,
                use_container_width=True
            )

        # ----------------------------------------------------
        # LINE CHART
        # ----------------------------------------------------

        elif chart_type == "line":

            chart_rows = []

            for i, label in enumerate(labels):

                row = {
                    "Period": label
                }

                for dataset in datasets:

                    dataset_label = dataset.get(
                        "label",
                        "Value"
                    )

                    values = dataset.get(
                        "data",
                        []
                    )

                    row[dataset_label] = (
                        values[i]
                        if i < len(values)
                        else 0
                    )

                chart_rows.append(row)

            df = pd.DataFrame(chart_rows)
            df = df.set_index("Period")

            if chart_title:
                st.subheader(chart_title)

            st.line_chart(
                df,
                height=500
            )

        # ----------------------------------------------------
        # PIE / DOUGHNUT
        # ----------------------------------------------------

        elif chart_type in ["pie", "doughnut"]:

            dataset = datasets[0]

            values = dataset.get(
                "data",
                []
            )

            pie_data = {
                labels[i]: values[i]
                for i in range(
                    min(len(labels), len(values))
                )
            }

            st.subheader(
                chart_title
                if chart_title
                else "Distribution"
            )

            st.write(pie_data)

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        else:

            chart_rows = []

            for i, label in enumerate(labels):

                row = {
                    "Category": label
                }

                for dataset in datasets:

                    dataset_label = dataset.get(
                        "label",
                        "Value"
                    )

                    values = dataset.get(
                        "data",
                        []
                    )

                    row[dataset_label] = (
                        values[i]
                        if i < len(values)
                        else 0
                    )

                chart_rows.append(row)

            df = pd.DataFrame(chart_rows)
            df = df.set_index("Category")

            st.bar_chart(
                df,
                height=500
            )
