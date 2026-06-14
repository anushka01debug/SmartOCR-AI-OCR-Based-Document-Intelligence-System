import streamlit as st
import pandas as pd
import json
import base64

def inject_custom_css():
    """Injects a premium, production-ready SaaS CSS theme into the Streamlit application."""
    custom_css = """
    <style>
    /* Import Plus Jakarta Sans and Inter from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apply fonts globally */
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }
    
    /* Root dark gradient background and smooth scrolling */
    .stApp {
        background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.08), transparent 40%),
                    radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.08), transparent 40%),
                    #030712;
        color: #f3f4f6;
    }
    
    /* Hide Streamlit header, footer and main menu for white-label premium feel */
    header, footer, [data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    
    /* Reduce default container padding to maximize workspace size */
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 90% !important;
    }
    
    /* Sidebar premium glass container */
    section[data-testid="stSidebar"] {
        background: rgba(8, 10, 20, 0.75) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        padding-top: 1.5rem !important;
    }
    
    /* Styling Streamlit widgets to look like custom UI inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within, .stNumberInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Fix label visibility - make labels bright slate/white */
    label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
        color: #e5e7eb !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Premium File Uploader wrapper */
    div[data-testid="stFileUploader"] {
        border: 2px dashed rgba(139, 92, 246, 0.2) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.01) !important;
        padding: 24px !important;
        transition: all 0.3s ease !important;
        text-align: center;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #8b5cf6 !important;
        background: rgba(139, 92, 246, 0.03) !important;
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.1) !important;
    }
    div[data-testid="stFileUploader"] section {
        padding: 0 !important;
    }
    
    /* Customize text areas (OCR Output) */
    .stTextArea textarea {
        background-color: rgba(8, 10, 20, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #e5e7eb !important;
        border-radius: 12px !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.95rem !important;
        padding: 16px !important;
        line-height: 1.6 !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.4) !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25), inset 0 2px 8px rgba(0,0,0,0.4) !important;
    }
    
    /* Sleek gradient main buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c084fc 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.3) !important;
        width: 100%;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.5) !important;
        filter: brightness(1.08) !important;
    }
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Form wrapper glassmorphic cards */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4) !important;
        padding: 24px !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    
    /* Styled Submit buttons inside forms */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        box-shadow: 0 6px 22px rgba(16, 185, 129, 0.45) !important;
    }
    
    /* Tab Styling (Clean & Minimalist) */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #9ca3af !important;
        background: transparent !important;
        border: none !important;
        padding: 10px 20px !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #a78bfa !important;
        border-bottom: 2px solid #8b5cf6 !important;
    }
    div[data-testid="stTabItems"] {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        gap: 10px;
    }
    
    /* Expander customization */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #d1d5db !important;
        padding: 12px !important;
        transition: color 0.2s ease;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #a78bfa !important;
    }
    
    /* Tables styling */
    div[data-testid="stTable"] table, div[data-testid="stDataFrame"] {
        background-color: rgba(8, 10, 20, 0.4) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        overflow: hidden !important;
    }
    
    /* Badge tags styling */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 700;
        border-radius: 30px;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .badge-primary { background: rgba(59, 130, 246, 0.12); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-purple { background: rgba(139, 92, 246, 0.12); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-pink { background: rgba(236, 72, 153, 0.12); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }
    .badge-secondary { background: rgba(107, 114, 128, 0.12); color: #9ca3af; border: 1px solid rgba(107, 114, 128, 0.3); }

    /* Custom layout containers */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-bottom: 2rem;
        background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
        border-radius: 20px;
    }
    
    .hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #ffffff 30%, #a78bfa 70%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: #9ca3af;
        font-size: 1.1rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #030712;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Custom KPI Cards */
    .glow-card {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
    }
    .glow-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.15);
    }
    .glow-card::after {
        content: '';
        position: absolute;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        top: -75px;
        right: -75px;
        z-index: 0;
        pointer-events: none;
    }
    .glow-card-val {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 10px;
        margin-bottom: 4px;
        background: linear-gradient(90deg, #ffffff 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        z-index: 1;
        position: relative;
    }
    .glow-card-lbl {
        color: #9ca3af;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        z-index: 1;
        position: relative;
    }
    .glow-card-icon {
        font-size: 1.6rem;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        z-index: 1;
        position: relative;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_hero_section():
    """Renders a beautiful hero header for the workspace."""
    hero_html = """
    <div class="hero-container">
        <div class="hero-title">SmartOCR AI</div>
        <div class="hero-subtitle">Enterprise Document Intelligence Engine with Advanced Visual Pipelines and Structured Extraction</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

def render_kpi_card(title, value, icon="📊"):
    """Renders a stunning modern custom KPI card with hover actions."""
    card_html = f"""
    <div class="glow-card">
        <div class="glow-card-icon">{icon}</div>
        <div class="glow-card-val">{value}</div>
        <div class="glow-card-lbl">{title}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def get_badge_html(category):
    """Returns the HTML for a styled category badge."""
    c_lower = category.lower()
    if c_lower == "invoice":
        return f'<span class="badge badge-primary">Invoice 📄</span>'
    elif c_lower == "receipt":
        return f'<span class="badge badge-success">Receipt 🧾</span>'
    elif c_lower == "certificate":
        return f'<span class="badge badge-purple">Certificate 🎓</span>'
    elif c_lower == "question paper":
        return f'<span class="badge badge-warning">Exam Paper 📝</span>'
    elif c_lower == "notes":
        return f'<span class="badge badge-pink">Study Notes 📓</span>'
    else:
        return f'<span class="badge badge-secondary">{category} 🔍</span>'

def get_download_btn(data, filename, file_format):
    """
    Generates a download link/button for Streamlit.
    file_format can be 'txt', 'json', or 'csv'
    """
    if file_format == 'txt':
        b64 = base64.b64encode(data.encode()).decode()
        mime = 'text/plain'
        label = "📥 Download Raw Text (.txt)"
    elif file_format == 'json':
        b64 = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        mime = 'application/json'
        label = "📥 Download Metadata (.json)"
    elif file_format == 'csv':
        if isinstance(data, pd.DataFrame):
            csv_str = data.to_csv(index=False)
        else:
            csv_str = data
        b64 = base64.b64encode(csv_str.encode()).decode()
        mime = 'text/csv'
        label = "📥 Download CSV Report (.csv)"
    else:
        raise ValueError("Invalid format specified")
        
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color:white; border:none; padding:10px 18px; border-radius:8px; font-weight:700; cursor:pointer; box-shadow:0 4px 12px rgba(16,185,129,0.25); transition:all 0.3s; width: 100%; text-align: center;">{label}</button></a>'
    return href