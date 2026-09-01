import streamlit as st
import requests
import plotly.graph_objects as go


# ============================================================
# CONFIGURATION
# ============================================================

N8N_WEBHOOK_URL = "https://n8n.umirai.ai/webhook/people-analytics"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 2rem;
    }

    .dashboard-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 16px;
        color: #9ca3af;
        margin-bottom: 28px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 650;
        margin-top: 28px;
        margin-bottom: 15px;
    }

    .analysis-text {
        font-size: 17px;
        line-height: 1.7;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">People Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Workforce insights powered by your People Analytics workflow'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# QUESTION INPUT
# ============================================================

st.markdown("**Ask a People Analytics question**")

question = st.text_input(
    label="",
    value="Compare new joiners and exits between FY 2023-24 and FY 2025-26.",
    placeholder="Ask a People Analytics question...",
    label_visibility="collapsed"
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "Analyze",
    type="primary"
)


# ============================================================
# FUNCTION — CALL N8N
# ============================================================

def call_n8n(user_question):

    payload = {
        "user_question": user_question
    }

    try:

        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to the analytics workflow: {e}"
        )

        return None

    except ValueError:

        st.error(
            "The analytics workflow returned an invalid JSON response."
        )

        return None


# ============================================================
# FUNCTION — CREATE BAR CHART
# ============================================================

def create_bar_chart(chart_data):

    labels = chart_data.get("chart_labels", [])
    datasets = chart_data.get("chart_datasets", [])

    if not labels or not datasets:
        return None

    fig = go.Figure()

    # --------------------------------------------------------
    # DEFAULT COLOURS
    # --------------------------------------------------------

    default_colors = [
        "#4472C4",
        "#ED7D31",
        "#70AD47",
        "#5B9BD5",
        "#A5A5A5",
        "#FFC000"
    ]

    # --------------------------------------------------------
    # ADD EACH DATASET AS A SEPARATE BAR SERIES
    # --------------------------------------------------------

    for index, dataset in enumerate(datasets):

        label = dataset.get(
            "label",
            f"Series {index + 1}"
        )

        values = dataset.get(
            "data",
            []
        )

        # ----------------------------------------------------
        # NORMALISE VALUES
        # ----------------------------------------------------

        values = list(values)

        if len(values) < len(labels):

            values = values + (
                [0] * (len(labels) - len(values))
            )

        elif len(values) > len(labels):

            values = values[:len(labels)]

        # ----------------------------------------------------
        # USE COLOUR FROM N8N WHEN AVAILABLE
        # ----------------------------------------------------

        color = dataset.get(
            "backgroundColor"
        )

        if not color:

            color = default_colors[
                index % len(default_colors)
            ]

        # ----------------------------------------------------
        # BAR TRACE
        # ----------------------------------------------------

        fig.add_trace(

            go.Bar(

                name=label,

                x=labels,

                y=values,

                # ------------------------------------------------
                # SHOW VALUES ABOVE BARS
                # ------------------------------------------------

                text=values,

                texttemplate="%{text}",

                textposition="outside",

                textfont=dict(
                    color="#FFFFFF",
                    size=14,
                    family="Arial"
                ),

                # ------------------------------------------------
                # BAR COLOUR
                # ------------------------------------------------

                marker=dict(
                    color=color
                ),

                # ------------------------------------------------
                # NARROW BAR WIDTH
                # ------------------------------------------------

                width=0.20,

                # ------------------------------------------------
                # PREVENT VALUE CLIPPING
                # ------------------------------------------------

                cliponaxis=False,

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    + label
                    + ": %{y}"
                    + "<extra></extra>"
                )
            )
        )

    # ========================================================
    # DETERMINE Y-AXIS MAXIMUM
    # ========================================================

    all_values = []

    for dataset in datasets:

        values = dataset.get(
            "data",
            []
        )

        for value in values:

            try:
                all_values.append(float(value))

            except (
                ValueError,
                TypeError
            ):
                pass

    if all_values:

        maximum_value = max(all_values)

        if maximum_value <= 0:

            y_axis_max = 10

        else:

            # Give the labels enough room above the bars.
            y_axis_max = maximum_value * 1.18

    else:

        y_axis_max = 10

    # ========================================================
    # CHART TITLE
    # ========================================================

    chart_title = chart_data.get(
        "chart_title",
        "People Analytics"
    )

    # ========================================================
    # CHART LAYOUT
    # ========================================================

    fig.update_layout(

        title=dict(
            text=chart_title,
            font=dict(
                size=22,
                color="#FFFFFF"
            ),
            x=0,
            xanchor="left"
        ),

        # ----------------------------------------------------
        # CRITICAL:
        # GROUP DATASETS SIDE BY SIDE
        # ----------------------------------------------------

        barmode="group",

        # ----------------------------------------------------
        # SPACE BETWEEN FY GROUPS
        # ----------------------------------------------------

        bargap=0.40,

        # ----------------------------------------------------
        # SMALL GAP BETWEEN BARS INSIDE EACH FY
        # ----------------------------------------------------

        bargroupgap=0.01,

        template="plotly_dark",

        height=520,

        margin=dict(
            l=70,
            r=30,
            t=90,
            b=110
        ),

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#FFFFFF",
                size=13
            )
        ),

        font=dict(
            color="#FFFFFF"
        ),

        # ----------------------------------------------------
        # FORCE BAR TEXT TO WHITE
        # ----------------------------------------------------

        uniformtext=dict(
            minsize=12,
            mode="show"
        )
    )

    # ========================================================
    # X AXIS
    # ========================================================

       # X AXIS
    # ========================================================

    x_axis_title = chart_data.get("chart_x_axis_title")

    if not x_axis_title:
        title_lower = str(chart_data.get("chart_title", "")).lower()

        if "location" in title_lower:
            x_axis_title = "Location"
        elif "department" in title_lower:
            x_axis_title = "Department"
        elif "financial year" in title_lower or "financial years" in title_lower:
            x_axis_title = "Financial Year"
        elif "gender" in title_lower:
            x_axis_title = "Gender"
        elif "designation" in title_lower or "job title" in title_lower:
            x_axis_title = "Designation"
        elif "age" in title_lower:
            x_axis_title = "Age"
        elif "tenure" in title_lower:
            x_axis_title = "Tenure"
        else:
            x_axis_title = "Category"

    fig.update_xaxes(
        title_text=x_axis_title,
        type="category",
        categoryorder="array",
        categoryarray=labels,
        tickmode="array",
        tickvals=labels,
        ticktext=labels,
        tickfont=dict(
            color="#FFFFFF",
            size=13
        ),
        title_font=dict(
            color="#FFFFFF",
            size=14
        ),
        showgrid=False,
        zeroline=False
    )
    
    # --------------------------------------------------------
    # Y AXIS
    # --------------------------------------------------------

    fig.update_yaxes(

        title_text="Employee Count",

        rangemode="tozero",

        tickfont=dict(
            color="white",
            size=12
        ),

        title_font=dict(
            color="white",
            size=14
        ),

        gridcolor="rgba(255,255,255,0.15)",

        zeroline=True,
        zerolinecolor="rgba(255,255,255,0.25)"
    )
    # ========================================================
    # FINAL TRACE-LEVEL TEXT OVERRIDE
    # ========================================================

    fig.update_traces(

        textfont=dict(
            color="#FFFFFF",
            size=14,
            family="Arial"
        ),

        selector=dict(
            type="bar"
        )
    )

    return fig


# ============================================================
# FUNCTION — CREATE LINE CHART
# ============================================================

def create_line_chart(chart_data):

    labels = chart_data.get(
        "chart_labels",
        []
    )

    datasets = chart_data.get(
        "chart_datasets",
        []
    )

    if not labels or not datasets:
        return None

    fig = go.Figure()

    default_colors = [
        "#4472C4",
        "#ED7D31",
        "#70AD47",
        "#5B9BD5",
        "#A5A5A5",
        "#FFC000"
    ]

    for index, dataset in enumerate(datasets):

        label = dataset.get(
            "label",
            f"Series {index + 1}"
        )

        values = dataset.get(
            "data",
            []
        )

        color = dataset.get(
            "backgroundColor"
        )

        if not color:

            color = default_colors[
                index % len(default_colors)
            ]

        fig.add_trace(

            go.Scatter(

                name=label,

                x=labels,

                y=values,

                mode="lines+markers+text",

                text=values,

                texttemplate="%{text}",

                textposition="top center",

                textfont=dict(
                    color="#FFFFFF",
                    size=13
                ),

                line=dict(
                    color=color,
                    width=3
                ),

                marker=dict(
                    color=color,
                    size=8
                ),

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    + label
                    + ": %{y}"
                    + "<extra></extra>"
                )
            )
        )

    chart_title = chart_data.get(
        "chart_title",
        "People Analytics"
    )

    fig.update_layout(

        title=dict(
            text=chart_title,
            font=dict(
                size=22,
                color="#FFFFFF"
            ),
            x=0,
            xanchor="left"
        ),

        template="plotly_dark",

        height=520,

        margin=dict(
            l=70,
            r=30,
            t=90,
            b=100
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.20,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#FFFFFF"
            )
        ),

        font=dict(
            color="#FFFFFF"
        )
    )

    fig.update_xaxes(

        title_text="Financial Year",

        tickfont=dict(
            color="#FFFFFF"
        ),

        title_font=dict(
            color="#FFFFFF"
        )
    )

    fig.update_yaxes(

        title_text="Employee Count",

        rangemode="tozero",

        tickfont=dict(
            color="#FFFFFF"
        ),

        title_font=dict(
            color="#FFFFFF"
        ),

        gridcolor="rgba(255,255,255,0.15)"
    )

    return fig


# ============================================================
# FUNCTION — RENDER CHART
# ============================================================

def render_chart(chart_data):

    if not chart_data:
        return

    if not chart_data.get(
        "chart_required",
        False
    ):
        return

    chart_type = str(
        chart_data.get(
            "chart_type",
            "bar"
        )
    ).lower().strip()

    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    if chart_type == "bar":

        fig = create_bar_chart(
            chart_data
        )

        if fig:

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        return

    # --------------------------------------------------------
    # LINE CHART
    # --------------------------------------------------------

    if chart_type == "line":

        fig = create_line_chart(
            chart_data
        )

        if fig:

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        return

    # --------------------------------------------------------
    # UNKNOWN CHART TYPE
    # --------------------------------------------------------

    st.warning(
        f"Unsupported chart type: {chart_type}"
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

if analyze:

    if not question.strip():

        st.warning(
            "Please enter a People Analytics question."
        )

    else:

        with st.spinner(
            "Analyzing workforce data..."
        ):

            result = call_n8n(
                question.strip()
            )

        if result:

            # =================================================
            # ANALYSIS SECTION
            # =================================================

            answer = result.get(
                "answer",
                "No analysis was returned."
            )

            st.markdown(
                '<div class="section-title">Analysis</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="analysis-text">{answer}</div>',
                unsafe_allow_html=True
            )

            # =================================================
            # CHART SECTION
            # =================================================

            if result.get(
                "chart_required",
                False
            ):

                render_chart(
                    result
                )
