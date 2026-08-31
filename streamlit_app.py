import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ============================================================
# PEOPLE ANALYTICS DASHBOARD
# Connected to n8n People Analytics Workflow
# ============================================================

WEBHOOK_URL = "https://n8n.umirai.ai/webhook/people-analytics"

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="People Analytics",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("People Analytics Dashboard")
st.caption("Ask questions about your workforce data")

# ------------------------------------------------------------
# QUESTION INPUT
# ------------------------------------------------------------

question = st.text_input(
    "Ask a People Analytics question",
    placeholder="e.g. Compare new joiners and exits between FY 2023-24 and FY 2025-26"
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
    # CHART
    # --------------------------------------------------------

    chart_required = result.get("chart_required", False)

    if chart_required:

        chart_type = result.get("chart_type", "bar")
        chart_title = result.get("chart_title", "")
        labels = result.get("chart_labels", [])
        datasets = result.get("chart_datasets", [])

        if labels and datasets:

            # ------------------------------------------------
            # CONVERT DATA TO DATAFRAME
            # ------------------------------------------------

            chart_data = {}

            for dataset in datasets:

                dataset_label = dataset.get("label", "Value")
                dataset_values = dataset.get("data", [])

                chart_data[dataset_label] = dataset_values

            chart_data["Category"] = labels

            df = pd.DataFrame(chart_data)

            # ------------------------------------------------
            # BAR
            # ------------------------------------------------

            if chart_type == "bar":

                df_long = df.melt(
                    id_vars="Category",
                    var_name="Metric",
                    value_name="Value"
                )

                fig = px.bar(
                    df_long,
                    x="Category",
                    y="Value",
                    color="Metric",
                    barmode="group",
                    title=chart_title,
                    text="Value"
                )

                fig.update_traces(
                    textposition="outside"
                )

                fig.update_layout(
                    title_font_size=22,
                    xaxis_title="",
                    yaxis_title="Count",
                    font=dict(
                        size=16,
                        color="black"
                    ),
                    legend_title="",
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # LINE
            # ------------------------------------------------

            elif chart_type == "line":

                df_long = df.melt(
                    id_vars="Category",
                    var_name="Metric",
                    value_name="Value"
                )

                fig = px.line(
                    df_long,
                    x="Category",
                    y="Value",
                    color="Metric",
                    markers=True,
                    title=chart_title,
                    text="Value"
                )

                fig.update_traces(
                    textposition="top center"
                )

                fig.update_layout(
                    title_font_size=22,
                    xaxis_title="",
                    yaxis_title="Value",
                    font=dict(
                        size=16,
                        color="black"
                    ),
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # PIE / POLAR AREA
            # ------------------------------------------------

            elif chart_type in ["pie", "polarArea"]:

                dataset = datasets[0]

                values = dataset.get("data", [])

                pie_df = pd.DataFrame({
                    "Category": labels,
                    "Value": values
                })

                fig = px.pie(
                    pie_df,
                    names="Category",
                    values="Value",
                    title=chart_title
                )

                fig.update_layout(
                    title_font_size=22,
                    font=dict(
                        size=16,
                        color="black"
                    ),
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # DOUGHNUT
            # ------------------------------------------------

            elif chart_type == "doughnut":

                dataset = datasets[0]

                values = dataset.get("data", [])

                pie_df = pd.DataFrame({
                    "Category": labels,
                    "Value": values
                })

                fig = px.pie(
                    pie_df,
                    names="Category",
                    values="Value",
                    hole=0.5,
                    title=chart_title
                )

                fig.update_layout(
                    title_font_size=22,
                    font=dict(
                        size=16,
                        color="black"
                    ),
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ------------------------------------------------
            # FALLBACK
            # ------------------------------------------------

            else:

                df_long = df.melt(
                    id_vars="Category",
                    var_name="Metric",
                    value_name="Value"
                )

                fig = px.bar(
                    df_long,
                    x="Category",
                    y="Value",
                    color="Metric",
                    barmode="group",
                    title=chart_title,
                    text="Value"
                )

                fig.update_layout(
                    title_font_size=22,
                    font=dict(
                        size=16,
                        color="black"
                    ),
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

    # --------------------------------------------------------
    # RAW DATA — OPTIONAL DEBUG
    # --------------------------------------------------------

    with st.expander("View chart data"):

        if chart_required:
            st.json({
                "chart_type": result.get("chart_type"),
                "chart_title": result.get("chart_title"),
                "chart_labels": result.get("chart_labels"),
                "chart_datasets": result.get("chart_datasets")
            })
        else:
            st.write("No chart was requested for this question.")
