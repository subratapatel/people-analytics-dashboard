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

    /* Main page */
    .main {
        padding-top: 2rem;
    }

    /* Title */
    .dashboard-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    /* Subtitle */
    .dashboard-subtitle {
        font-size: 16px;
        color: #9ca3af;
        margin-bottom: 28px;
    }

    /* Section heading */
    .section-title {
        font-size: 28px;
        font-weight: 650;
        margin-top: 28px;
        margin-bottom: 15px;
    }

    /* Analysis text */
    .analysis-text {
        font-size: 17px;
        line-height: 1.7;
        margin-bottom: 25px;
    }

    /* Error box */
    .error-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #3b1f23;
        color: #ff6b6b;
        margin-top: 15px;
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

st.markdown(
    "**Ask a People Analytics question**"
)

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

    if not labels:
        return None

    if not datasets:
        return None

    fig = go.Figure()

    # --------------------------------------------------------
    # ADD EACH DATASET AS A SEPARATE BAR SERIES
    # --------------------------------------------------------

    for dataset in datasets:

        label = dataset.get("label", "Series")

        values = dataset.get("data", [])

        # Make sure values match number of labels
        if len(values) < len(labels):
            values = values + [0] * (len(labels) - len(values))

        if len(values) > len(labels):
            values = values[:len(labels)]

        fig.add_trace(
            go.Bar(
                name=label,

                x=labels,

                y=values,

                # Display numbers above bars
                text=values,

                textposition="outside",

                # IMPORTANT:
                # White numbers for dark dashboard
                textfont=dict(
                    color="white",
                    size=14
                ),

                # Controlled bar width
                width=0.20,

                # Prevent text from being clipped
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

    # --------------------------------------------------------
    # CHART TITLE
    # --------------------------------------------------------

    chart_title = chart_data.get(
        "chart_title",
        "People Analytics"
    )

    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        title=dict(
            text=chart_title,
            font=dict(
                size=22,
                color="white"
            ),
            x=0,
            xanchor="left"
        ),

        # THIS IS CRITICAL
        # It puts New Joiners and Exits SIDE BY SIDE
        barmode="group",

        # Dark theme
        template="plotly_dark",

        # Chart height
        height=520,

        # Spacing
        margin=dict(
            l=70,
            r=30,
            t=90,
            b=110
        ),

        # Space between FY groups
        bargap=0.40,

        # Small gap between New Joiners and Exits
        bargroupgap=0.01,

        # Legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(
                color="white",
                size=13
            )
        ),

        # Global font
        font=dict(
            color="white"
        )
    )

    # --------------------------------------------------------
    # X AXIS
    # --------------------------------------------------------

    fig.update_xaxes(

        title_text="Financial Year",

        type="category",

        categoryorder="array",

        categoryarray=labels,

        tickmode="array",

        tickvals=labels,

        ticktext=labels,

        tickfont=dict(
            color="white",
            size=13
        ),

        title_font=dict(
            color="white",
            size=14
        ),

        showgrid=False
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

    return fig


# ============================================================
# FUNCTION — CREATE LINE CHART
# ============================================================

def create_line_chart(chart_data):

    labels = chart_data.get("chart_labels", [])
    datasets = chart_data.get("chart_datasets", [])

    if not labels or not datasets:
        return None

    fig = go.Figure()

    for dataset in datasets:

        label = dataset.get("label", "Series")

        values = dataset.get("data", [])

        fig.add_trace(
            go.Scatter(

                name=label,

                x=labels,

                y=values,

                mode="lines+markers+text",

                text=values,

                textposition="top center",

                textfont=dict(
                    color="white",
                    size=13
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
                color="white"
            )
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
                color="white"
            )
        ),

        font=dict(
            color="white"
        )
    )

    fig.update_xaxes(
        title_text="Financial Year",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    )

    fig.update_yaxes(
        title_text="Employee Count",
        rangemode="tozero",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        gridcolor="rgba(255,255,255,0.15)"
    )

    return fig


# ============================================================
# FUNCTION — RENDER CHART
# ============================================================

def render_chart(chart_data):

    if not chart_data:
        return

    if not chart_data.get("chart_required", False):
        return

    chart_type = (
        chart_data.get("chart_type", "bar")
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # BAR
    # --------------------------------------------------------

    if chart_type == "bar":

        fig = create_bar_chart(chart_data)

        if fig:
            st.plotly_chart(
                fig,
                use_container_width=True
            )

        return

    # --------------------------------------------------------
    # LINE
    # --------------------------------------------------------

    if chart_type == "line":

        fig = create_line_chart(chart_data)

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

        with st.spinner("Analyzing workforce data..."):

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

                render_chart(result)
