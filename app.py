import streamlit as st
import os
import io
import time
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Local imports
from database import init_db, save_scan, get_all_scans, delete_scan, clear_history
from image_processor import run_preprocessing_pipeline
from classifier import classify_document, get_keywords, save_keywords, load_settings, save_settings
from extractor import extract_document_information
from ocr_engine import test_tesseract_connection, run_ocr_on_image, process_pdf_document, extract_page_text_or_render
from ui_helpers import inject_custom_css, render_kpi_card, get_badge_html, get_download_btn, render_hero_section

# Initialize application settings and database
init_db()

# Page configuration
st.set_page_config(
    page_title="SmartOCR AI | Enterprise Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom modern theme styles
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

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px 0; margin-bottom: 10px;'>
        <div style='font-size: 2.5rem; display: inline-block; margin-bottom: 5px;'>📄</div>
        <h3 style='margin: 0; font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>SmartOCR AI</h3>
        <p style='color: #6b7280; font-size: 0.75rem; margin: 4px 0 0 0; font-weight: 600; letter-spacing: 0.8px;'>DOCUMENT INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Radio
    page = st.radio(
        "Navigation",
        ["🔍 OCR Workspace", "📊 Analytics Dashboard", "📁 Batch Processing", "⚙️ System Configuration"],
        index=0
    )
    
    st.markdown("---")
    # Quick Connection Status
    tesseract_ok, ver = test_tesseract_connection()
    if tesseract_ok:
        st.success(f"Tesseract OCR: Connected\n(v{ver[:10]})")
    else:
        st.error("Tesseract OCR: Offline\n(Check path in Settings)")

# ==========================================
# PAGE 1: OCR WORKSPACE
# ==========================================
if page == "🔍 OCR Workspace":
    render_hero_section()
    
    col1, col2 = st.columns([1, 1])
    
    uploaded_file = None
    processed_text = ""
    processed_time = 0.0
    doc_category = "Unknown"
    metadata = {}
    
    with col1:
        st.subheader("📥 Upload Document")
        uploaded_file = st.file_uploader(
            "Select Image or PDF Document",
            type=["png", "jpg", "jpeg", "pdf"],
            key="workspace_upload"
        )
        
        # Image Preprocessing Configuration Panel
        with st.expander("⚙️ Image Preprocessing Pipeline Settings", expanded=False):
            st.markdown("<small>Preprocessing improves text recognition accuracy on low-quality scans or shadows.</small>", unsafe_allow_html=True)
            
            upscale = st.checkbox("Upscale Image (For low resolution)", value=False)
            upscale_factor = st.slider("Upscaling Factor", min_value=1.5, max_value=3.0, value=2.0, step=0.5, disabled=not upscale)
            
            denoise = st.checkbox("Denoise Image (Remove scanning noise)", value=False)
            denoise_strength = st.slider("Denoising Strength", min_value=5, max_value=25, value=10, step=1, disabled=not denoise)
            
            deskew = st.checkbox("Auto-Deskew (Rotate skewed text back to horizontal)", value=True)
            contrast = st.checkbox("Contrast Enhancement (CLAHE)", value=True)
            grayscale = st.checkbox("Grayscale Conversion", value=True)
            
            binarize = st.checkbox("Binarization (Convert to absolute black & white)", value=False)
            binarize_method = st.selectbox(
                "Binarization Method",
                ["otsu", "adaptive_gaussian", "adaptive_mean"],
                disabled=not binarize
            )
            
            # Pack preprocessing configuration
            preprocess_options = {
                "upscale": upscale,
                "upscale_factor": upscale_factor,
                "denoise": denoise,
                "denoise_strength": denoise_strength,
                "deskew": deskew,
                "contrast": contrast,
                "grayscale": grayscale,
                "binarize": binarize,
                "binarize_method": binarize_method
            }
            
        if uploaded_file:
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_ext == ".pdf":
                # PDF processing flow
                pdf_bytes = uploaded_file.read()
                doc, pages_info = process_pdf_document(pdf_bytes)
                page_count = len(doc)
                
                st.info(f"📄 PDF Loaded: **{uploaded_file.name}** ({page_count} pages)")
                
                # Page selector
                selected_page = st.number_input(
                    f"Select Page (1 to {page_count})",
                    min_value=1,
                    max_value=page_count,
                    value=1
                )
                
                # Check selectable text vs scanned page
                page_data = pages_info[selected_page - 1]
                
                # Preview page visual / information
                # Retrieve the text or render the page image
                text_content, page_image, is_digital = extract_page_text_or_render(doc, selected_page - 1)
                
                if is_digital:
                    st.success("✨ Digital Text Layer Detected! This page contains selectable digital text.")
                    # Show preview of selectable text
                    st.markdown("##### Page Preview (Selectable text):")
                    st.text_area("Selectable text snapshot", text_content[:400] + "...", height=120, disabled=True)
                else:
                    st.warning("⚠️ Scanned Page Detected! No selectable text layers found. Converting page to image for OCR...")
                    st.image(page_image, caption=f"Rendered Page {selected_page} of {uploaded_file.name}", use_container_width=True)
            
            else:
                # Standard image processing flow
                try:
                    page_image = Image.open(uploaded_file)
                    is_digital = False
                    text_content = None
                    
                    # Preview Original Image
                    st.markdown("##### Uploaded Image Preview:")
                    st.image(page_image, caption=uploaded_file.name, use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
                    uploaded_file = None
                    
    with col2:
        st.subheader("⚡ Document Intelligence & Analysis")
        
        if uploaded_file:
            action_btn = st.button("🚀 Analyze & Process Document", use_container_width=True)
            
            if action_btn:
                with st.spinner("Processing document... Please wait..."):
                    start_time = time.time()
                    
                    if file_ext == ".pdf":
                        # Determine if we extract digital text or run OCR
                        text_content, page_image, is_digital = extract_page_text_or_render(doc, selected_page - 1)
                        
                        if is_digital:
                            # It's a digital PDF, extraction is instant
                            processed_text = text_content
                            processed_time = time.time() - start_time
                        else:
                            # Preprocess the rendered page image
                            processed_img = run_preprocessing_pipeline(page_image, preprocess_options)
                            
                            # Run OCR
                            processed_text, ocr_dur = run_ocr_on_image(processed_img)
                            processed_time = time.time() - start_time
                    else:
                        # Image flow
                        processed_img = run_preprocessing_pipeline(page_image, preprocess_options)
                        
                        # Show preprocessed comparison tab if preprocessed
                        with st.expander("👁️ View Preprocessed Image Comparison", expanded=False):
                            comp_col1, comp_col2 = st.columns(2)
                            with comp_col1:
                                st.markdown("**Original Image**")
                                st.image(page_image, use_container_width=True)
                            with comp_col2:
                                st.markdown("**Preprocessed OCR Input**")
                                st.image(processed_img, use_container_width=True)
                                
                        # Run OCR
                        processed_text, ocr_dur = run_ocr_on_image(processed_img)
                        processed_time = time.time() - start_time
                    
                    if processed_text and not processed_text.startswith("OCR Error"):
                        # Classify the text
                        doc_category, scores = classify_document(processed_text)
                        
                        # Extract structured metadata based on category
                        metadata = extract_document_information(processed_text, doc_category)
                        
                        # Store in session state for editing
                        st.session_state["active_text"] = processed_text
                        st.session_state["active_category"] = doc_category
                        st.session_state["active_metadata"] = metadata
                        st.session_state["active_scores"] = scores
                        st.session_state["active_processing_time"] = processed_time
                        st.session_state["active_filename"] = uploaded_file.name
                        st.session_state["active_file_type"] = f"PDF (Page {selected_page})" if file_ext == ".pdf" else "Image File"
                        st.session_state["save_triggered"] = False
                    else:
                        st.error(processed_text) # Show OCR Error message
                        
            # Render extraction and save workspace if we have active results in session state
            if "active_text" in st.session_state and st.session_state.get("active_filename") == uploaded_file.name:
                st.markdown("---")
                
                # Row 1: Classification details
                badge_html = get_badge_html(st.session_state["active_category"])
                st.markdown(f"#### Classification: {badge_html}", unsafe_allow_html=True)
                
                with st.expander("📊 Classification Keyword Match Scores", expanded=False):
                    score_df = pd.DataFrame({
                        "Category": list(st.session_state["active_scores"].keys()),
                        "Keyword Hits": list(st.session_state["active_scores"].values())
                    }).sort_values(by="Keyword Hits", ascending=False)
                    st.dataframe(score_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("#### 📝 Edit Extracted Fields")
                st.markdown("<small>Verify the extracted fields below and correct any values if necessary before saving to history.</small>", unsafe_allow_html=True)
                
                # Interactive Form to review and edit values
                with st.form("metadata_edit_form"):
                    edited_metadata = {}
                    
                    # Create editable fields for each extracted key
                    for key, val in st.session_state["active_metadata"].items():
                        edited_metadata[key] = st.text_input(key, str(val))
                        
                    # Custom select box to override classification
                    override_cat = st.selectbox(
                        "Document Category Classification",
                        ["Invoice", "Receipt", "Certificate", "Question Paper", "Notes", "Unknown"],
                        index=["Invoice", "Receipt", "Certificate", "Question Paper", "Notes", "Unknown"].index(st.session_state["active_category"])
                    )
                    
                    submit_save = st.form_submit_button("💾 Save Scan Record to Database", use_container_width=True)
                    
                    if submit_save:
                        # Update session state with edited values
                        st.session_state["active_metadata"] = edited_metadata
                        st.session_state["active_category"] = override_cat
                        
                        # Save to SQLite Database
                        save_scan(
                            filename=st.session_state["active_filename"],
                            file_type=st.session_state["active_file_type"],
                            classified_type=st.session_state["active_category"],
                            ocr_text=st.session_state["active_text"],
                            extracted_metadata=st.session_state["active_metadata"],
                            processing_time=st.session_state["active_processing_time"],
                            char_count=len(st.session_state["active_text"])
                        )
                        st.session_state["save_triggered"] = True
                
                if st.session_state.get("save_triggered"):
                    st.success("✅ Record successfully committed to database history!")
                
                # Row 3: Raw Text display and downloads
                st.markdown("---")
                st.markdown("#### 🔍 Extracted Raw Text")
                st.text_area(
                    "Raw OCR text contents",
                    st.session_state["active_text"],
                    height=200,
                    key="raw_text_display"
                )
                
                # Downloads Row
                dl_col1, dl_col2, dl_col3 = st.columns(3)
                with dl_col1:
                    st.markdown(get_download_btn(st.session_state["active_text"], f"extracted_{st.session_state['active_filename']}.txt", "txt"), unsafe_allow_html=True)
                with dl_col2:
                    st.markdown(get_download_btn(st.session_state["active_metadata"], f"metadata_{st.session_state['active_filename']}.json", "json"), unsafe_allow_html=True)
                with dl_col3:
                    # Individual CSV representation of the extracted metadata
                    meta_df = pd.DataFrame(list(st.session_state["active_metadata"].items()), columns=["Field Name", "Extracted Value"])
                    st.markdown(get_download_btn(meta_df, f"report_{st.session_state['active_filename']}.csv", "csv"), unsafe_allow_html=True)

        else:
            st.info("💡 Upload a document (Image or PDF) on the left to start parsing.")

# ==========================================
# PAGE 2: ANALYTICS DASHBOARD
# ==========================================
elif page == "📊 Analytics Dashboard":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; background: linear-gradient(90deg, #ffffff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af; margin-bottom: 25px;'>Statistical overview of processed documents, database metrics, and custom reports.</p>", unsafe_allow_html=True)
    
    # Load data
    df = get_all_scans()
    
    if df.empty:
        st.warning("⚠️ No documents processed yet! Upload files in the OCR Workspace to populate dashboard metrics.")
    else:
        # High level KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        total_scans = len(df)
        avg_time = df["processing_time"].mean()
        total_chars = df["char_count"].sum()
        
        # Find top category
        top_cat = df["classified_type"].mode()[0] if not df["classified_type"].empty else "N/A"
        
        with kpi1:
            render_kpi_card("Processed Documents", f"{total_scans}", "📁")
        with kpi2:
            render_kpi_card("Avg. Time per Scan", f"{avg_time:.2f}s", "⚡")
        with kpi3:
            render_kpi_card("Total Characters Scanned", f"{total_chars:,}", "🔤")
        with kpi4:
            render_kpi_card("Top Category", f"{top_cat}", "🏆")
            
        st.markdown("---")
        
        # Charts Row
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("<h3 style='font-size: 1.3rem; font-weight: 750; margin-bottom: 15px; background: linear-gradient(90deg, #a78bfa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Document Classification Breakdown</h3>", unsafe_allow_html=True)
            cat_counts = df["classified_type"].value_counts()
            
            # Matplotlib Pie chart
            fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='none')
            ax.set_facecolor('none')
            colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#6b7280']
            
            wedges, texts, autotexts = ax.pie(
                cat_counts, 
                labels=cat_counts.index, 
                autopct='%1.1f%%',
                startangle=140,
                colors=colors[:len(cat_counts)],
                textprops=dict(color="#e0e6ed")
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
                
            plt.title("Document Category Distribution", color="#e0e6ed", weight="bold")
            st.pyplot(fig)
            
        with chart_col2:
            st.markdown("<h3 style='font-size: 1.3rem; font-weight: 750; margin-bottom: 15px; background: linear-gradient(90deg, #a78bfa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Scan Performance over Time</h3>", unsafe_allow_html=True)
            # Sort by ID to show chronological order
            chron_df = df.sort_values(by="id")
            
            # Simple line chart using streamlit native charts
            chart_data = pd.DataFrame({
                "Processing Time (seconds)": chron_df["processing_time"].values
            }, index=chron_df["timestamp"].values)
            st.line_chart(chart_data, color="#8b5cf6")
            
        st.markdown("---")
        
        # Interactive Search & History Table
        st.markdown("<h3 style='font-size: 1.6rem; font-weight: 800; margin-top: 25px; margin-bottom: 15px; background: linear-gradient(90deg, #ffffff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Scanning History Record Database</h3>", unsafe_allow_html=True)
        
        # Filtering parameters
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            search_query = st.text_input("🔍 Search History (by filename or OCR text contents)", "")
        with filter_col2:
            categories_list = ["All"] + list(df["classified_type"].unique())
            category_filter = st.selectbox("Filter by Category", categories_list)
            
        # Apply filters
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["filename"].str.contains(search_query, case=False, na=False) |
                filtered_df["ocr_text"].str.contains(search_query, case=False, na=False)
            ]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df["classified_type"] == category_filter]
            
        # Limit columns for display
        display_columns = ["id", "timestamp", "filename", "file_type", "classified_type", "processing_time", "char_count"]
        st.dataframe(filtered_df[display_columns], use_container_width=True, hide_index=True)
        
        # Table actions (Delete, Export)
        act_col1, act_col2 = st.columns([1, 4])
        with act_col1:
            del_id = st.number_input("Delete Scan ID", min_value=1, step=1, value=1)
            del_btn = st.button("🗑️ Delete Row", use_container_width=True)
            if del_btn:
                delete_scan(del_id)
                st.success(f"Row {del_id} deleted successfully. Refreshing database...")
                time.sleep(1)
                st.rerun()
                
        with act_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(get_download_btn(filtered_df, "smartocr_history_report.csv", "csv"), unsafe_allow_html=True)

# ==========================================
# PAGE 3: BATCH PROCESSING
# ==========================================
elif page == "📁 Batch Processing":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; background: linear-gradient(90deg, #ffffff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Batch Document Processing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af; margin-bottom: 25px;'>Upload multiple images or PDFs at once to run batch OCR extraction and compile summary reports.</p>", unsafe_allow_html=True)
    
    batch_files = st.file_uploader(
        "Drag & drop multiple files",
        type=["png", "jpg", "jpeg", "pdf"],
        accept_multiple_files=True
    )
    
    if batch_files:
        st.success(f"Selected {len(batch_files)} file(s). Click process below to begin.")
        
        run_batch = st.button("🚀 Process Batch Files", use_container_width=True)
        
        if run_batch:
            batch_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, file in enumerate(batch_files):
                status_text.markdown(f"Processing ({index+1}/{len(batch_files)}): **{file.name}**...")
                start_time = time.time()
                
                # Check extension
                file_ext = os.path.splitext(file.name)[1].lower()
                text_content = ""
                
                try:
                    if file_ext == ".pdf":
                        # Process first page for simplicity in batch view
                        doc, pages_info = process_pdf_document(file.read())
                        txt_c, img_c, is_dig = extract_page_text_or_render(doc, 0)
                        if is_dig:
                            text_content = txt_c
                        else:
                            # Scanned PDF, OCR it
                            text_content, _ = run_ocr_on_image(img_c)
                    else:
                        img = Image.open(file)
                        text_content, _ = run_ocr_on_image(img)
                        
                    # Auto classify
                    cat, _ = classify_document(text_content)
                    
                    # Extract general entities & category fields
                    meta = extract_document_information(text_content, cat)
                    dur = time.time() - start_time
                    
                    # Store scan directly to Database
                    save_scan(
                        filename=file.name,
                        file_type="PDF (Batch)" if file_ext == ".pdf" else "Image (Batch)",
                        classified_type=cat,
                        ocr_text=text_content,
                        extracted_metadata=meta,
                        processing_time=dur,
                        char_count=len(text_content)
                    )
                    
                    # Add to summary table
                    batch_results.append({
                        "Filename": file.name,
                        "Type": "PDF" if file_ext == ".pdf" else "Image",
                        "Classification": cat,
                        "Words": len(text_content.split()),
                        "Time (s)": f"{dur:.2f}s",
                        "Extracted Details": str(list(meta.items())[:3]).replace("[", "").replace("]", "") + "..."
                    })
                    
                except Exception as e:
                    batch_results.append({
                        "Filename": file.name,
                        "Type": "Error",
                        "Classification": "Error",
                        "Words": 0,
                        "Time (s)": "0.0s",
                        "Extracted Details": f"Failed: {str(e)}"
                    })
                    
                progress_bar.progress((index + 1) / len(batch_files))
                
            status_text.markdown("✨ **Batch Processing Complete!** All scans committed to Database.")
            
            # Show summary
            batch_df = pd.DataFrame(batch_results)
            st.dataframe(batch_df, use_container_width=True)
            
            # Download full batch summary
            st.markdown(get_download_btn(batch_df, "batch_processing_summary.csv", "csv"), unsafe_allow_html=True)
            
    else:
        st.info("💡 Upload one or more documents or image scans to run automated batch OCR.")

# ==========================================
# PAGE 4: SYSTEM CONFIGURATION
# ==========================================
elif page == "⚙️ System Configuration":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; background: linear-gradient(90deg, #ffffff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>System Configuration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af; margin-bottom: 25px;'>Customize SmartOCR AI pipelines, classification keywords, Tesseract routes, and local file storage.</p>", unsafe_allow_html=True)
    
    settings = load_settings()
    
    tab1, tab2, tab3 = st.tabs(["🛣️ OCR Engine Routes", "🏷️ Document Classifier Keywords", "💽 Database Administration"])
    
    with tab1:
        st.subheader("Tesseract OCR Installation Path")
        st.markdown(
            "Tesseract is an external OCR engine. Provide the absolute file path to your local `tesseract.exe` executable binary."
        )
        
        current_path = settings.get(
    "tesseract_path",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
        new_path = st.text_input("Executable Path (Windows)", current_path)
        
        test_col1, test_col2 = st.columns([1, 3])
        with test_col1:
            test_btn = st.button("🔌 Test OCR Connection")
        
        if test_btn:
            ok, msg = test_tesseract_connection(new_path)
            if ok:
                st.success(f"✅ Connection Successful! Tesseract running version: **{msg}**")
            else:
                st.error(f"❌ Connection Failed. Details:\n{msg}")
                
        # Save Tesseract Settings
        save_route = st.button("💾 Save Path Settings")
        if save_route:
            settings["tesseract_path"] = new_path
            if save_settings(settings):
                st.success("✅ Path configurations successfully committed to settings.json!")
            else:
                st.error("Failed to save settings.")
                
    with tab2:
        st.subheader("Auto-Classification Keywords Manager")
        st.markdown(
            "Modify the list of case-insensitive keywords matching files to determine their document classification category."
        )
        
        current_keywords = get_keywords()
        updated_keywords = {}
        
        for category, kws in current_keywords.items():
            with st.expander(f"🏷️ Category: {category} ({len(kws)} keywords)", expanded=False):
                # Represent as comma separated string
                kws_str = ", ".join(kws)
                new_kws_str = st.text_area(
                    f"Keywords for {category}",
                    kws_str,
                    help="Separate multiple keywords with commas"
                )
                
                # Parse back to list
                parsed_kws = [x.strip() for x in new_kws_str.split(",") if x.strip()]
                updated_keywords[category] = parsed_kws
                
        save_kws_btn = st.button("💾 Save Keyword Schemes")
        if save_kws_btn:
            if save_keywords(updated_keywords):
                st.success("✅ Keyword modifications successfully committed!")
            else:
                st.error("Failed to update keywords.")
                
    with tab3:
        st.subheader("Local database management")
        st.markdown(
            "View directory space and manage saved histories."
        )
        
        db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_history.db")
        if os.path.exists(db_file):
            size_kb = os.path.getsize(db_file) / 1024
            st.metric("Database File Size", f"{size_kb:.2f} KB")
        else:
            st.metric("Database File Size", "0.00 KB (Not Created)")
            
        st.warning("⚠️ Critical Operations below. These operations cannot be undone.")
        
        clear_db_btn = st.button("🔥 Erase All Database History Records")
        if clear_db_btn:
            clear_history()
            st.success("🧹 Database cleared! All rows successfully truncated.")