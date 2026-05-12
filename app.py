import streamlit as st
import pandas as pd
import plotly.express as px
import os
from agent.agent import process_query

st.set_page_config(
    page_title="AI Lakehouse Analytics",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e, #16213e);
        border-right: 2px solid #e94560;
    }

    /* Title */
    .main-title {
        font-size: 2.8em;
        font-weight: 800;
        background: linear-gradient(90deg, #f093fb, #f5576c, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1em;
        margin-bottom: 30px;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
        margin: 10px 0;
    }

    .metric-card h2 {
        font-size: 2em;
        margin: 0;
        font-weight: 800;
    }

    .metric-card p {
        margin: 5px 0 0 0;
        opacity: 0.8;
        font-size: 0.9em;
    }

    /* SQL box */
    .sql-box {
        background: #1a1a2e;
        border: 1px solid #e94560;
        border-radius: 10px;
        padding: 15px;
        font-family: monospace;
        color: #4facfe;
        font-size: 1em;
    }

    /* Explanation box */
    .explanation-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #f093fb;
        border-radius: 10px;
        padding: 20px;
        color: #e2e8f0;
        font-size: 1em;
        line-height: 1.7;
        margin: 10px 0;
    }

    /* Section headers */
    .section-header {
        font-size: 1.4em;
        font-weight: 700;
        color: #f093fb;
        border-bottom: 2px solid #e94560;
        padding-bottom: 8px;
        margin: 25px 0 15px 0;
    }

    /* Upload area */
    .upload-text {
        color: #a0aec0;
        font-size: 0.9em;
        text-align: center;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #f093fb, #f5576c);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 35px;
        font-size: 1.1em;
        font-weight: 700;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(245, 87, 108, 0.5);
    }

    /* Input field */
    .stTextInput > div > div > input {
        background: #1a1a2e;
        border: 2px solid #302b63;
        border-radius: 10px;
        color: white;
        padding: 12px;
        font-size: 1em;
    }

    .stTextInput > div > div > input:focus {
        border-color: #f093fb;
        box-shadow: 0 0 10px rgba(240, 147, 251, 0.3);
    }

    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Stats row */
    .stats-container {
        display: flex;
        gap: 15px;
        margin: 20px 0;
    }

    .stat-box {
        flex: 1;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: white;
    }

    .stat-box-1 { background: linear-gradient(135deg, #f093fb, #f5576c); }
    .stat-box-2 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    .stat-box-3 { background: linear-gradient(135deg, #43e97b, #38f9d7); }
    .stat-box-4 { background: linear-gradient(135deg, #fa709a, #fee140); }
</style>
""", unsafe_allow_html=True)

# Session state
if "schema" not in st.session_state:
    st.session_state.schema = None
if "table_name" not in st.session_state:
    st.session_state.table_name = None
if "csv_path" not in st.session_state:
    st.session_state.csv_path = None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0;'>
        <span style='font-size:3em;'>🏗️</span>
        <h2 style='color:#f093fb; margin:10px 0;'>Lakehouse AI</h2>
        <p style='color:#a0aec0; font-size:0.85em;'>Powered by Phi-3 + Spark</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#f093fb; font-weight:700;'>📂 Upload Dataset</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

    if uploaded_file:
        save_path = f"/home/elakiya/prompt2query/data_storage/{uploaded_file.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        table_name = uploaded_file.name.replace(".csv", "").replace("-", "_").replace(" ", "_").lower()
        st.session_state.csv_path = save_path
        st.session_state.table_name = table_name
        st.success(f"✅ {uploaded_file.name} uploaded!")
        st.markdown(f"<p style='color:#a0aec0; font-size:0.8em;'>Table: <b style='color:#4facfe;'>{table_name}</b></p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#a0aec0; font-size:0.8em;'>
        <p>💡 <b style='color:white;'>How to use:</b></p>
        <p>1. Upload your CSV file</p>
        <p>2. Type your question</p>
        <p>3. Click Run Query</p>
        <p>4. View results & charts</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("<div class='main-title'>🏗️ AI Lakehouse Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ask questions about your data in plain English — powered by Phi-3 AI + Apache Spark</div>", unsafe_allow_html=True)

# Question input
col1, col2 = st.columns([4, 1])
with col1:
    question = st.text_input(
        "",
        placeholder="💬 e.g. Show total sales by region, What is the average price by category?",
        label_visibility="collapsed"
    )
with col2:
    run_clicked = st.button("🚀 Run Query")

# Process
if run_clicked and question:
    if not st.session_state.csv_path:
        st.error("⚠️ Please upload a CSV file first!")
    else:
        with st.spinner("🤖 AI is thinking... Generating SQL and analyzing your data..."):
            result = process_query(
                st.session_state.csv_path,
                st.session_state.table_name,
                question
            )

        if "error" in result:
            st.error(f"❌ Error: {result['error']}")
        else:
            # SQL Section
            st.markdown("<div class='section-header'>🔍 Generated SQL</div>", unsafe_allow_html=True)
            st.code(result["validated_sql"], language="sql")

            # Explanation Section
            st.markdown("<div class='section-header'>💡 AI Explanation</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='explanation-box'>{result['explanation']}</div>", unsafe_allow_html=True)

            # Chart Section
            analysis = result["analysis"]
            chart_type = analysis.get("chart_type")
            df = pd.DataFrame(analysis["data"])

            st.markdown("<div class='section-header'>📊 Visualization</div>", unsafe_allow_html=True)

            if chart_type == "metric":
                st.markdown(f"""
                <div class='metric-card'>
                    <h2>{round(analysis['metric_value'], 2)}</h2>
                    <p>{analysis['metric_label'].upper()}</p>
                </div>
                """, unsafe_allow_html=True)

            elif chart_type == "bar":
                fig = px.bar(
                    df,
                    x=analysis["x_column"],
                    y=analysis["y_column"],
                    title=question,
                    color=analysis["y_column"],
                    color_continuous_scale="viridis"
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0.3)",
                    font_color="white",
                    title_font_size=16
                )
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "line":
                fig = px.line(
                    df,
                    x=analysis["x_column"],
                    y=analysis["y_column"],
                    title=question,
                    markers=True
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0.3)",
                    font_color="white"
                )
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.dataframe(df, use_container_width=True)

            # Summary Stats
            if "summary" in analysis:
                st.markdown("<div class='section-header'>📈 Summary Statistics</div>", unsafe_allow_html=True)
                s = analysis["summary"]
                st.markdown(f"""
                <div class='stats-container'>
                    <div class='stat-box stat-box-1'>
                        <h3 style='margin:0;'>{round(s['max'], 2)}</h3>
                        <p style='margin:5px 0 0 0; opacity:0.8;'>Maximum</p>
                    </div>
                    <div class='stat-box stat-box-2'>
                        <h3 style='margin:0;'>{round(s['min'], 2)}</h3>
                        <p style='margin:5px 0 0 0; opacity:0.8;'>Minimum</p>
                    </div>
                    <div class='stat-box stat-box-3'>
                        <h3 style='margin:0;'>{round(s['average'], 2)}</h3>
                        <p style='margin:5px 0 0 0; opacity:0.8;'>Average</p>
                    </div>
                    <div class='stat-box stat-box-4'>
                        <h3 style='margin:0;'>{round(s['total'], 2)}</h3>
                        <p style='margin:5px 0 0 0; opacity:0.8;'>Total</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Raw data table
            st.markdown("<div class='section-header'>🗃️ Raw Data</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)