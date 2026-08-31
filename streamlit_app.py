import streamlit as st
import requests
import pandas as pd
import altair as alt


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
# PAGE HEADER
# ============================================================

st.title("People Analytics Dashboard")
st.caption("Workforce insights powered by your People Analytics workflow")


# ============================================================
# USER QUESTION
# ============================================================

question = st.text_input(
    "Ask a People Analytics question",
    placeholder=(
        "Example: Compare new joiners and exits between "
        "FY 2023-24 and FY 2025-26."
    )
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button("Analyze", type="primary"):

    if not question.strip():
        st.warning("Please enter a People Analytics question.")
        st.stop()

    # --------------------------------------------------------
    # CALL N8N WORKFLOW
    # --------------------------------------------------------

    with st.spinner("Analyzing workforce data..."):

        try:
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "user_question": question.strip()
                },
                timeout=120
            )

            response.raise_for_status()

            result = response.json()

        except requests.exceptions.Timeout:
            st.error(
                "The analytics workflow took too long to respond."
            )
            st.stop()

        except requests.exceptions.RequestException as e:
            st.error(
                f"Unable to connect to the analytics workflow: {e}"
            )
            st.stop()

        except ValueError:
            st.error(
                "The analytics workflow returned an invalid response."
            )
            st.stop()


    # ========================================================
    # NORMALIZE RESPONSE
    # ========================================================

    # n8n should normally return an object.
    # This also protects us if the response is wrapped in a list.

    if isinstance(result, list):

        if len(result) == 0:
            st.error("The analytics workflow returned no data.")
            st.stop()

        result = result[0]

    if not isinstance(result, dict):
        st.error("Unexpected response format from the analytics workflow.")
        st.stop()


    # ========================================================
    # ANALYSIS / TEXT ANSWER
    # ========================================================

    answer = result.get("answer", "")

    if answer:

        st.subheader("Analysis")

        st.write(answer)


    # ========================================================
    # CHART DECISION
    # ========================================================

    chart_required = result.get(
        "chart_required",
        False
    )

    if not chart_required:
        st.stop()


    # ========================================================
    # CHART DATA
    # ========================================================

    chart_type = str(
        result.get("chart_type", "bar")
    ).strip().lower()

    chart_title = str(
        result.get("chart_title", "")
    ).strip()

    labels = result.get(
        "chart_labels",
        []
    )

    datasets = result.get(
        "chart_datasets",
        []
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not isinstance(labels, list) or not labels:

        st.warning(
            "Chart labels were not returned by the analytics workflow."
        )
        st.stop()


    if not isinstance(datasets, list) or not datasets:

        st.warning(
            "Chart datasets were not returned by the analytics workflow."
        )
        st.stop()


    # ========================================================
    # BAR / COLUMN CHART
    # ========================================================

    if chart_type in [
        "bar",
        "column",
        "groupedBar",
        "grouped_bar"
    ]:

        chart_rows = []


        # ----------------------------------------------------
        # CONVERT N8N DATA INTO LONG-FORM DATA
        # ----------------------------------------------------

        for dataset in datasets:

            if not isinstance(dataset, dict):
                continue

            metric = str(
                dataset.get("label", "Value")
            )

            values = dataset.get(
                "data",
                []
            )

            if not isinstance(values, list):
                continue


            for index, financial_year in enumerate(labels):

                value = (
                    values[index]
                    if index < len(values)
                    else 0
                )

                # Ensure numeric values
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    numeric_value = 0


                chart_rows.append(
                    {
                        "FY": str(financial_year),
                        "Metric": metric,
                        "Value": numeric_value
                    }
                )


        # ----------------------------------------------------
        # CHECK CHART DATA
        # ----------------------------------------------------

        if not chart_rows:

            st.warning(
                "No usable chart data was returned."
            )
            st.stop()


        df = pd.DataFrame(chart_rows)


        # ----------------------------------------------------
        # PRESERVE THE ORDER RETURNED BY N8N
        # ----------------------------------------------------

        fy_order = [
            str(label)
            for label in labels
        ]

        metric_order = []

        for dataset in datasets:

            metric = str(
                dataset.get("label", "Value")
            )

            if metric not in metric_order:
                metric_order.append(metric)


        df["FY"] = pd.Categorical(
            df["FY"],
            categories=fy_order,
            ordered=True
        )

        df["Metric"] = pd.Categorical(
            df["Metric"],
            categories=metric_order,
            ordered=True
        )


        # ----------------------------------------------------
        # CHART TITLE
        # ----------------------------------------------------

        if chart_title:
            st.subheader(chart_title)


        # ----------------------------------------------------
        # COLOUR PALETTE
        #
        # New Joiners and Exits will always be visually
        # different, even if n8n sends the same colour.
        # ----------------------------------------------------

        default_colors = [
            "#4472C4",
            "#ED7D31",
            "#70AD47",
            "#5B9BD5",
            "#A5A5A5",
            "#FFC000",
            "#8064A2",
            "#00A6A6"
        ]


        # ----------------------------------------------------
        # USE COLORS FROM N8N WHEN AVAILABLE
        # ----------------------------------------------------

        color_map = {}

        for index, dataset in enumerate(datasets):

            metric = str(
                dataset.get("label", "Value")
            )

            supplied_color = dataset.get(
                "backgroundColor"
            )

            if (
                isinstance(supplied_color, str)
                and supplied_color.startswith("#")
            ):
                color_map[metric] = supplied_color

            else:
                color_map[metric] = (
                    default_colors[
                        index % len(default_colors)
                    ]
                )


        # ----------------------------------------------------
        # GROUPED BAR CHART
        # ----------------------------------------------------

        bars = (
            alt.Chart(df)
            .mark_bar(
                size=45
            )
            .encode(

                # Financial years are the main X-axis groups
                x=alt.X(
                    "FY:N",
                    title=None,
                    sort=fy_order,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelFontSize=14,
                        labelPadding=12,
                        ticks=True,
                        domain=True
                    )
                ),

                # This is the critical part:
                # xOffset creates SIDE-BY-SIDE bars
                # instead of stacked bars.
                xOffset=alt.XOffset(
                    "Metric:N",
                    sort=metric_order
                ),

                # Employee count
                y=alt.Y(
                    "Value:Q",
                    title="Employee Count",
                    scale=alt.Scale(
                        zero=True
                    ),
                    axis=alt.Axis(
                        labelFontSize=12,
                        titleFontSize=14,
                        tickMinStep=1
                    )
                ),

                # Different colour for every metric
                color=alt.Color(
                    "Metric:N",
                    title=None,
                    sort=metric_order,
                    scale=alt.Scale(
                        domain=list(color_map.keys()),
                        range=list(color_map.values())
                    ),
                    legend=alt.Legend(
                        orient="bottom",
                        labelFontSize=13,
                        symbolSize=120,
                        title=None
                    )
                ),

                tooltip=[
                    alt.Tooltip(
                        "FY:N",
                        title="Financial Year"
                    ),
                    alt.Tooltip(
                        "Metric:N",
                        title="Metric"
                    ),
                    alt.Tooltip(
                        "Value:Q",
                        title="Employee Count",
                        format=".0f"
                    )
                ]
            )
            .properties(
                height=500
            )
        )


        # ----------------------------------------------------
        # VALUE LABELS ABOVE EACH BAR
        # ----------------------------------------------------

        value_labels = (
            alt.Chart(df)
            .mark_text(
                dy=-8,
                fontSize=13,
                fontWeight="bold"
            )
            .encode(

                x=alt.X(
                    "FY:N",
                    sort=fy_order
                ),

                xOffset=alt.XOffset(
                    "Metric:N",
                    sort=metric_order
                ),

                y=alt.Y(
                    "Value:Q"
                ),

                text=alt.Text(
                    "Value:Q",
                    format=".0f"
                )
            )
        )


        # ----------------------------------------------------
        # DISPLAY CHART
        # ----------------------------------------------------

        st.altair_chart(
            bars + value_labels,
            use_container_width=True
        )


    # ========================================================
    # LINE CHART
    # ========================================================

    elif chart_type == "line":

        chart_rows = []

        for dataset in datasets:

            if not isinstance(dataset, dict):
                continue

            metric = str(
                dataset.get("label", "Value")
            )

            values = dataset.get(
                "data",
                []
            )

            for index, label in enumerate(labels):

                value = (
                    values[index]
                    if index < len(values)
                    else 0
                )

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0

                chart_rows.append(
                    {
                        "Period": str(label),
                        "Metric": metric,
                        "Value": value
                    }
                )


        df = pd.DataFrame(chart_rows)


        if chart_title:
            st.subheader(chart_title)


        line_chart = (
            alt.Chart(df)
            .mark_line(
                point=True
            )
            .encode(
                x=alt.X(
                    "Period:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelFontSize=14
                    )
                ),
                y=alt.Y(
                    "Value:Q",
                    title="Value"
                ),
                color=alt.Color(
                    "Metric:N",
                    title=None
                ),
                tooltip=[
                    "Period",
                    "Metric",
                    "Value"
                ]
            )
            .properties(
                height=500
            )
        )


        st.altair_chart(
            line_chart,
            use_container_width=True
        )


    # ========================================================
    # PIE / POLAR AREA
    # ========================================================

    elif chart_type in [
        "pie",
        "doughnut",
        "polarArea"
    ]:

        dataset = datasets[0]

        values = dataset.get(
            "data",
            []
        )

        pie_rows = []

        for index, label in enumerate(labels):

            value = (
                values[index]
                if index < len(values)
                else 0
            )

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0

            pie_rows.append(
                {
                    "Category": str(label),
                    "Value": value
                }
            )


        df = pd.DataFrame(pie_rows)


        if chart_title:
            st.subheader(chart_title)


        pie_chart = (
            alt.Chart(df)
            .mark_arc(
                innerRadius=70
                if chart_type == "doughnut"
                else 0
            )
            .encode(
                theta=alt.Theta(
                    "Value:Q"
                ),
                color=alt.Color(
                    "Category:N",
                    title=None
                ),
                tooltip=[
                    alt.Tooltip(
                        "Category:N",
                        title="Category"
                    ),
                    alt.Tooltip(
                        "Value:Q",
                        title="Employee Count",
                        format=".0f"
                    )
                ]
            )
            .properties(
                height=500
            )
        )


        st.altair_chart(
            pie_chart,
            use_container_width=True
        )


    # ========================================================
    # UNKNOWN CHART TYPE
    # ========================================================

    else:

        st.warning(
            f"Chart type '{chart_type}' is not currently supported."
        )

        # Show the returned data so the issue can be diagnosed
        # without breaking the entire dashboard.

        st.json(
            {
                "chart_type": chart_type,
                "chart_title": chart_title,
                "chart_labels": labels,
                "chart_datasets": datasets
            }
        )
