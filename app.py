import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from patent_tools import PatentSearchClient
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import json
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

# Page Configuration
st.set_page_config(
    page_title="Patent Research Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 100% LIGHT BROWN THEME - NO BLACK
# ============================================================
st.markdown("""
<style>
    /* ===== FORCE EVERYTHING BROWN ===== */
    html, body, .stApp, .stApp > div, .stApp > div > div, 
    .main, .block-container, .css-1d391kg, .css-1lcbmhc, 
    .css-18e3th9, .css-1r6slb0, .css-1q8dd3e, .st-emotion-cache-1d391kg {
        background: #f5efe8 !important;
        background-color: #f5efe8 !important;
    }
    
    /* ===== SIDEBAR - LIGHT BROWN ===== */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div,
    .css-1d391kg, .st-emotion-cache-1d391kg {
        background: #ede4d8 !important;
        background-color: #ede4d8 !important;
        border: none !important;
        border-right: 1px solid #dccfc0 !important;
    }
    
    /* ===== ALL TEXT - DARK BROWN ===== */
    * {
        color: #4a3728 !important;
    }
    
    /* ===== SIDEBAR BUTTONS ===== */
    .stButton > button {
        background: #ede4d8 !important;
        color: #4a3728 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        text-align: left !important;
        width: 100% !important;
        margin: 4px 0 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #dccfc0 !important;
        border-color: #c4b49f !important;
        color: #4a3728 !important;
    }
    
    /* ===== HEADER ===== */
    .main-header {
        background: #ede4d8 !important;
        padding: 24px 32px;
        border-radius: 12px;
        border: 1px solid #dccfc0;
        margin-bottom: 24px;
    }
    
    .main-header h1 { color: #4a3728 !important; }
    .main-header h1 span { color: #8a7a6a !important; }
    .main-header p { color: #4a3728 !important; }
    
    .badge {
        background: #f5efe8 !important;
        border: 1px solid #dccfc0 !important;
        color: #4a3728 !important;
    }
    
    /* ===== STAT CARDS ===== */
    .stat-card {
        background: #ede4d8 !important;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #dccfc0;
        text-align: center;
    }
    .stat-number { color: #4a3728 !important; font-size: 32px; font-weight: 700; }
    .stat-label { color: #6b5a4a !important; font-size: 13px; margin-top: 4px; }
    
    /* ===== FILTER BOX ===== */
    .filter-box {
        background: #ede4d8 !important;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #dccfc0;
        margin-bottom: 20px;
    }
    .filter-box h4 { color: #4a3728 !important; }
    .filter-box * { color: #4a3728 !important; }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input {
        background: #faf6f0 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px;
        padding: 12px 16px;
        color: #4a3728 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #c4b49f !important;
        box-shadow: 0 0 0 3px rgba(196, 180, 159, 0.2) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #8a7a6a !important; }
    
    .stTextArea > div > div > textarea {
        background: #faf6f0 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px;
        color: #4a3728 !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #c4b49f !important;
        box-shadow: 0 0 0 3px rgba(196, 180, 159, 0.2) !important;
    }
    .stTextArea > div > div > textarea::placeholder { color: #8a7a6a !important; }
    
    /* ===== SELECT BOX ===== */
    .stSelectbox > div > div {
        background: #faf6f0 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px;
        color: #4a3728 !important;
    }
    .stSelectbox > div > div:hover { border-color: #c4b49f !important; }
    .stSelectbox > div > div * { color: #4a3728 !important; }
    .stSelectbox label { color: #4a3728 !important; }
    
    /* ===== RESULT CARDS ===== */
    .result-card {
        background: #ede4d8 !important;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #dccfc0;
        margin-bottom: 12px;
    }
    .result-card:hover { border-color: #c4b49f !important; }
    .result-card * { color: #4a3728 !important; }
    .result-card .patent-number { color: #6b5a4a !important; font-weight: 600; font-family: 'Courier New', monospace; font-size: 14px; }
    .result-card .patent-title { color: #4a3728 !important; font-size: 18px; font-weight: 700; margin: 4px 0 8px 0; }
    .result-card .patent-date { color: #6b5a4a !important; font-size: 13px; }
    .result-card .patent-abstract { color: #4a3728 !important; font-size: 14px; line-height: 1.7; margin-top: 8px; padding: 12px; background: #faf6f0; border-radius: 8px; }
    .result-card .patent-detail { color: #4a3728 !important; font-size: 14px; margin: 4px 0; }
    .result-card .patent-label { color: #6b5a4a !important; font-weight: 600; font-size: 13px; }
    
    /* ===== AI BOX ===== */
    .ai-box {
        background: #faf6f0 !important;
        border-radius: 12px;
        padding: 24px 28px;
        border-left: 4px solid #c4b49f !important;
        margin: 20px 0;
        border: 1px solid #dccfc0;
    }
    .ai-box * { color: #4a3728 !important; }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: #faf6f0 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px !important;
        color: #4a3728 !important;
    }
    .streamlit-expanderHeader:hover { background: #f5efe8 !important; }
    .streamlit-expanderHeader * { color: #4a3728 !important; }
    .streamlit-expanderContent {
        background: #ede4d8 !important;
        border: 1px solid #dccfc0 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 20px !important;
    }
    .streamlit-expanderContent * { color: #4a3728 !important; }
    
    /* ===== METRIC ===== */
    [data-testid="metric-container"] {
        background: #ede4d8 !important;
        border: 1px solid #dccfc0 !important;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="metric-container"] label { color: #6b5a4a !important; }
    [data-testid="metric-container"] [data-testid="metric-value"] { color: #4a3728 !important; }
    
    /* ===== ALERT ===== */
    .stAlert, .stInfo, .stWarning, .stSuccess {
        border-radius: 8px !important;
        border: 1px solid #dccfc0 !important;
        background: #faf6f0 !important;
    }
    .stAlert *, .stInfo *, .stWarning *, .stSuccess * { color: #4a3728 !important; }
    
    /* ===== PROGRESS ===== */
    .stProgress > div > div { background: #c4b49f !important; border-radius: 8px !important; }
    
    /* ===== DIVIDER ===== */
    hr { border: none; border-top: 1px solid #dccfc0 !important; margin: 24px 0; }
    
    /* ===== DATA TABLE ===== */
    .stDataFrame { border: 1px solid #dccfc0 !important; border-radius: 8px !important; }
    .stDataFrame thead tr th { background: #ede4d8 !important; color: #4a3728 !important; }
    .stDataFrame tbody tr td { background: #faf6f0 !important; color: #4a3728 !important; }
    .stDataFrame * { color: #4a3728 !important; }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 24px 32px;
        color: #6b5a4a !important;
        font-size: 13px;
        border-top: 1px solid #dccfc0;
        background: transparent;
        margin-top: 40px;
    }
    .footer * { color: #6b5a4a !important; }
    
    /* ===== SPINNER ===== */
    .stSpinner > div { border-color: #c4b49f !important; border-top-color: transparent !important; }
    
    /* ===== LABELS ===== */
    label { color: #4a3728 !important; }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-header { padding: 16px 20px; }
        .main-header h1 { font-size: 22px; }
        .filter-box { padding: 16px; }
        .stat-card { padding: 16px; }
        .stat-number { font-size: 24px; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'patent_cache' not in st.session_state:
    st.session_state.patent_cache = {}
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Search"
if 'last_patents' not in st.session_state:
    st.session_state.last_patents = []
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# ============================================================
# PDF GENERATION FUNCTION
# ============================================================
def generate_pdf_report(query, patents, analysis_text=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#4a3728'), spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#4a3728'), spaceAfter=12)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#4a3728'), spaceAfter=6)
    patent_style = ParagraphStyle('PatentStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4a3728'), spaceAfter=12, leftIndent=20)
    
    elements = []
    
    elements.append(Paragraph("📄 Patent Research Report", title_style))
    elements.append(Paragraph(f"<b>Search Query:</b> {query}", body_style))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    elements.append(Paragraph(f"<b>Total Patents Found:</b> {len(patents)}", body_style))
    elements.append(Spacer(1, 20))
    
    if patents:
        elements.append(Paragraph("📊 Patent List", heading_style))
        for i, patent in enumerate(patents, 1):
            patent_text = f"""
            <b>{i}. {patent.get('patent_number', 'N/A')}</b><br/>
            <b>Title:</b> {patent.get('patent_title', 'Untitled')}<br/>
            <b>Date:</b> {patent.get('patent_date', 'N/A')}<br/>
            <b>Abstract:</b> {patent.get('patent_abstract', 'No abstract')[:500]}...
            """
            elements.append(Paragraph(patent_text, patent_style))
            elements.append(Spacer(1, 6))
    
    if analysis_text:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("🤖 AI Analysis", heading_style))
        elements.append(Paragraph(analysis_text[:1000], body_style))
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Generated by PatentPro · All processing is local and private", body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================
# INITIALIZE CLIENTS
# ============================================================
@st.cache_resource
def init_clients():
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    patent_client = PatentSearchClient()
    return llm, patent_client

llm, patent_client = init_clients()

# ============================================================
# SIDEBAR - NATIVE STREAMLIT BUTTONS
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 16px 0;">
        <div style="font-size: 36px; margin: 0;">📄</div>
        <h2 style="color: #4a3728; margin: 0; font-weight: 700;">Patent<span style="color: #8a7a6a;">Pro</span></h2>
        <p style="color: #6b5a4a; font-size: 12px; margin-top: 2px;">AI Research Agent</p>
        <div style="background: #f5efe8; border: 1px solid #dccfc0; padding: 2px 12px; border-radius: 20px; display: inline-block; margin-top: 4px;">
            <span style="color: #4a3728; font-size: 10px; font-weight: 600;">v2.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔍 Search", use_container_width=True, key="btn_search"):
        st.session_state.selected_page = "Search"
        st.rerun()
    
    if st.button("💡 Novelty", use_container_width=True, key="btn_novelty"):
        st.session_state.selected_page = "Novelty"
        st.rerun()
    
    if st.button("📊 Analytics", use_container_width=True, key="btn_analytics"):
        st.session_state.selected_page = "Analytics"
        st.rerun()
    
    if st.button("📚 History", use_container_width=True, key="btn_history"):
        st.session_state.selected_page = "History"
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    <p style="color: #6b5a4a; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
        📊 Quick Stats
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Searches", len(st.session_state.search_history))
    with col2:
        total_patents = sum([len(s.get('patents', [])) for s in st.session_state.search_history])
        st.metric("Patents", total_patents)

# ============================================================
# MAIN HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1>📄 Patent <span>Research</span> Agent</h1>
            <p>AI-powered patent discovery, analysis & novelty assessment</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="badge">🔬 Real-time</span>
            <span class="badge">🏢 Enterprise</span>
            <span class="badge">💎 100% Free</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PAGE: SEARCH
# ============================================================
if st.session_state.selected_page == "Search":
    st.markdown("""
    <div class="filter-box">
        <h4>🔍 Search & Filter Options</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input(
            "",
            placeholder="e.g., artificial intelligence, blockchain, CRISPR...",
            label_visibility="collapsed"
        )
    with col2:
        filter_year = st.selectbox(
            "📅 Year",
            ["All", "2025", "2024", "2023", "2022", "2021", "2020"],
            index=0
        )
    with col3:
        filter_results = st.selectbox(
            "📊 Results",
            [5, 10, 20, 50],
            index=1
        )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")
    with col2:
        clear_clicked = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_clicked:
        st.rerun()
    
    if search_clicked and search_query:
        with st.spinner("🔬 Searching patents..."):
            results = patent_client.search_patents(search_query, limit=50)
            all_patents = results.get("patents", [])
            
            filtered_patents = all_patents
            if filter_year != "All":
                filtered_patents = [
                    p for p in all_patents 
                    if p.get('patent_date', '').startswith(filter_year)
                ]
            
            patents = filtered_patents[:filter_results]
            
            st.session_state.last_patents = patents
            st.session_state.last_query = search_query
            
            st.session_state.search_history.append({
                'query': search_query,
                'patents': patents,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'year_filter': filter_year,
                'result_limit': filter_results
            })
            
            if patents:
                st.markdown(f"""
                <div style="background: #f5efe8; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #dccfc0;">
                    <span style="color: #4a3728; font-size: 14px;">
                        🔍 Showing <strong>{len(patents)}</strong> patents 
                        {f'from year <strong>{filter_year}</strong>' if filter_year != "All" else 'from <strong>all years</strong>'}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{len(patents)}</div>
                        <div class="stat-label">Patents Found</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    dates = [p.get('patent_date', '2024') for p in patents if p.get('patent_date')]
                    latest = max(dates) if dates else 'N/A'
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{latest[:4] if latest != 'N/A' else 'N/A'}</div>
                        <div class="stat-label">Latest Year</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    if filter_year != "All":
                        year_count = len([p for p in patents if p.get('patent_date', '').startswith(filter_year)])
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{year_count}</div>
                            <div class="stat-label">From {filter_year}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        years = set([p.get('patent_date', '')[:4] for p in patents if p.get('patent_date')])
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{len(years)}</div>
                            <div class="stat-label">Years Range</div>
                        </div>
                        """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{len(patents)}</div>
                        <div class="stat-label">Total Results</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ===== DISPLAY ALL PATENT INFO =====
                for i, patent in enumerate(patents, 1):
                    st.markdown(f"""
                    <div class="result-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <span class="patent-number">📄 {patent.get('patent_number', 'N/A')}</span>
                            <span class="patent-date">📅 {patent.get('patent_date', 'N/A')}</span>
                        </div>
                        <div class="patent-title">{patent.get('patent_title', 'Untitled')}</div>
                        <div style="margin: 8px 0;">
                            <span class="patent-label">🔢 Patent Number:</span>
                            <span class="patent-detail">{patent.get('patent_number', 'N/A')}</span>
                        </div>
                        <div style="margin: 4px 0;">
                            <span class="patent-label">📅 Filing Date:</span>
                            <span class="patent-detail">{patent.get('patent_date', 'N/A')}</span>
                        </div>
                        <div style="margin: 4px 0;">
                            <span class="patent-label">🏢 Assignee/Company:</span>
                            <span class="patent-detail">{patent.get('patent_assignee', 'N/A')}</span>
                        </div>
                        <div style="margin: 4px 0;">
                            <span class="patent-label">👤 Inventor(s):</span>
                            <span class="patent-detail">{patent.get('patent_inventor', 'N/A')}</span>
                        </div>
                        <div style="margin: 4px 0;">
                            <span class="patent-label">📂 CPC Classification:</span>
                            <span class="patent-detail">{patent.get('patent_cpc', 'N/A')}</span>
                        </div>
                        <div style="margin: 4px 0;">
                            <span class="patent-label">🔗 Patent ID:</span>
                            <span class="patent-detail">{patent.get('patent_id', 'N/A')}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <span class="patent-label">📝 Abstract:</span>
                            <div class="patent-abstract">{patent.get('patent_abstract', 'No abstract available')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ===== AI ANALYSIS =====
                with st.spinner("🧠 Generating AI insights..."):
                    ai_prompt = f"""Provide a comprehensive analysis of these patents about '{search_query}'. 
                    Include: key trends, major players, technology overview, and potential applications.
                    Patents: {json.dumps(patents[:5])}"""
                    response = llm.invoke([HumanMessage(content=ai_prompt)])
                    ai_analysis = response.content
                    
                    st.markdown(f"""
                    <div class="ai-box">
                        <div style="font-weight: 700; font-size: 18px; color: #4a3728; margin-bottom: 8px;">🤖 AI Patent Analysis</div>
                        <div class="content">{ai_analysis}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ===== DOWNLOAD PDF =====
                st.markdown("### 📥 Export Report")
                col1, col2, col3 = st.columns(3)
                with col1:
                    pdf_data = generate_pdf_report(search_query, patents, ai_analysis)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_data,
                        file_name=f"patent_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                with col2:
                    if patents:
                        # Create a clean DataFrame with all fields
                        df_data = []
                        for p in patents:
                            df_data.append({
                                'Patent Number': p.get('patent_number', 'N/A'),
                                'Title': p.get('patent_title', 'Untitled'),
                                'Date': p.get('patent_date', 'N/A'),
                                'Assignee': p.get('patent_assignee', 'N/A'),
                                'Inventor': p.get('patent_inventor', 'N/A'),
                                'CPC': p.get('patent_cpc', 'N/A'),
                                'Abstract': p.get('patent_abstract', 'No abstract')[:200] + '...'
                            })
                        df = pd.DataFrame(df_data)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv,
                            file_name=f"patents_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                with col3:
                    st.button("📋 Copy Results", use_container_width=True)
                    
            else:
                st.info("No patents found for this search term. Try adjusting your filters.")

# ============================================================
# PAGE: NOVELTY
# ============================================================
elif st.session_state.selected_page == "Novelty":
    st.markdown("""
    <div style="background: #ede4d8; padding: 24px 28px; border-radius: 12px; border: 1px solid #dccfc0; margin-bottom: 20px;">
        <h3 style="margin: 0 0 4px 0; color: #4a3728;">💡 Novelty Assessment</h3>
        <p style="color: #6b5a4a; font-size: 14px; margin: 0;">Check if your idea or claim is novel by comparing against existing patents</p>
    </div>
    """, unsafe_allow_html=True)
    
    claim_text = st.text_area(
        "",
        placeholder="e.g., A system that uses artificial intelligence to automatically detect and classify cancer cells from medical imaging data...",
        height=120,
        label_visibility="collapsed"
    )
    
    if st.button("💡 Check Novelty", type="primary"):
        if claim_text:
            with st.spinner("🔬 Analyzing novelty..."):
                results = patent_client.search_by_claim(claim_text, limit=5)
                patents = results.get("patents", [])
                score = max(0, 100 - (len(patents) * 18))
                
                st.markdown(f"""
                <div style="background: #ede4d8; border: 1px solid #dccfc0; border-radius: 12px; padding: 24px 28px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
                        <div>
                            <div style="font-size: 52px; font-weight: 700; color: #4a3728;">{score}%</div>
                            <div style="color: #6b5a4a;">Novelty Score</div>
                        </div>
                        <div>
                            <div style="font-size: 28px;">{'✅' if score > 70 else '⚠️' if score > 40 else '❌'}</div>
                            <div style="font-weight: 600; color: #4a3728;">{'High Novelty' if score > 70 else 'Moderate' if score > 40 else 'Low'}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if patents:
                    st.warning(f"Found {len(patents)} similar patents")
                    for i, patent in enumerate(patents, 1):
                        with st.expander(f"📄 Patent {i}: {patent.get('patent_number', 'N/A')}"):
                            st.markdown(f"""
                            **📌 Title:** {patent.get('patent_title', 'N/A')}  
                            **📅 Date:** {patent.get('patent_date', 'N/A')}  
                            **🔢 Number:** {patent.get('patent_number', 'N/A')}  
                            **🏢 Assignee:** {patent.get('patent_assignee', 'N/A')}  
                            **👤 Inventor:** {patent.get('patent_inventor', 'N/A')}  
                            **📝 Abstract:** {patent.get('patent_abstract', 'N/A')}
                            """)
                else:
                    st.success("✅ No similar patents found! Your claim appears novel!")

# ============================================================
# PAGE: ANALYTICS
# ============================================================
elif st.session_state.selected_page == "Analytics":
    st.markdown('<h3 style="color:#4a3728;">📊 Analytics Dashboard</h3>', unsafe_allow_html=True)
    
    if st.session_state.search_history:
        data = []
        for search in st.session_state.search_history:
            for patent in search.get('patents', []):
                data.append({
                    'Query': search.get('query', 'Unknown'),
                    'Patent Number': patent.get('patent_number', 'N/A'),
                    'Title': patent.get('patent_title', 'N/A')[:50],
                    'Year': patent.get('patent_date', '')[:4] if patent.get('patent_date') else 'N/A',
                    'Timestamp': search.get('timestamp', '')
                })
        
        if data:
            df = pd.DataFrame(data)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(df)}</div>
                    <div class="stat-label">Total Patents</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{df['Query'].nunique()}</div>
                    <div class="stat-label">Unique Searches</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{df['Patent Number'].nunique()}</div>
                    <div class="stat-label">Unique Patents</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                years = [y for y in df['Year'] if y != 'N/A']
                latest = max(years) if years else 'N/A'
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{latest}</div>
                    <div class="stat-label">Latest Year</div>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                year_counts = df[df['Year'] != 'N/A']['Year'].value_counts().sort_index()
                if not year_counts.empty:
                    fig = px.bar(
                        x=year_counts.index,
                        y=year_counts.values,
                        title="Patents by Year",
                        color_discrete_sequence=['#c4b49f']
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        height=350,
                        font=dict(color='#4a3728')
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                query_counts = df['Query'].value_counts().head(10)
                if not query_counts.empty:
                    fig = px.bar(
                        x=query_counts.values,
                        y=query_counts.index,
                        orientation='h',
                        title="Top Searches",
                        color_discrete_sequence=['#dccfc0']
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        height=350,
                        font=dict(color='#4a3728')
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<h4 style="color:#4a3728;">📋 Recent Activity</h4>', unsafe_allow_html=True)
            st.dataframe(
                df[['Timestamp', 'Query', 'Patent Number', 'Title']].sort_values('Timestamp', ascending=False).head(15),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Timestamp": "Time",
                    "Query": "Search",
                    "Patent Number": "Patent #",
                    "Title": "Title"
                }
            )
    else:
        st.info("📭 No search history yet. Go to Search tab and find some patents!")

# ============================================================
# PAGE: HISTORY
# ============================================================
elif st.session_state.selected_page == "History":
    st.markdown('<h3 style="color:#4a3728;">📚 Search History</h3>', unsafe_allow_html=True)
    
    if st.session_state.search_history:
        for search in reversed(st.session_state.search_history):
            with st.expander(f"🔍 {search.get('query', 'Unknown')} — {search.get('timestamp', '')} ({len(search.get('patents', []))} patents)"):
                for patent in search.get('patents', [])[:5]:
                    st.markdown(f"""
                    **📄 {patent.get('patent_number', 'N/A')}**  
                    {patent.get('patent_title', 'Untitled')[:100]}  
                    *📅 {patent.get('patent_date', 'N/A')}*
                    ---
                    """)
                if len(search.get('patents', [])) > 5:
                    st.info(f"... and {len(search.get('patents', [])) - 5} more patents")
        
        if st.button("🗑️ Clear All History"):
            st.session_state.search_history = []
            st.rerun()
    else:
        st.info("📭 No search history yet. Start exploring patents!")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    📄 PatentPro · Powered by Llama 3.2 & PatentsView API · All processing is local and private
</div>
""", unsafe_allow_html=True)