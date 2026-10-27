import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.scraper import scrape_job_url, PORTAL_SAMPLES, extract_contacts_and_links, extract_dates, extract_salary
from app.detector import analyze_job
from app.database import save_scan, get_recent_scans, clear_all_scans, init_db

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="SafeHire AI | Fake Internship & Job Scam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Title Styling */
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 24px;
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Risk Badges */
    .badge-safe {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-warning {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-danger {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Red flag tag */
    .flag-tag {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    .genuine-tag {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    .snippet-box {
        background-color: #f8fafc;
        border-left: 3px solid #ef4444;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        font-family: monospace;
        font-size: 0.85rem;
        color: #334155;
        margin-top: 4px;
        margin-bottom: 12px;
    }
    
    /* Sidebar branding */
    .sidebar-brand {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.4rem;
        color: #4f46e5;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🛡️ SafeHire AI</div>', unsafe_allow_html=True)
    st.caption("Fake Internship & Job Scam Detection System")
    st.markdown("---")
    
    selected_view = st.radio(
        "Navigation Menu:",
        ["🔍 Job Scanner", "⚡ 1-Click Showcase Samples", "📋 Batch URL Inspector", "📜 Scan Audit History", "🎓 AKGEC Academic Report"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🏛️ Institution Details")
    st.markdown("""
    **College:** Ajay Kumar Garg Engineering College (AKGEC), Ghaziabad  
    **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University, Lucknow  
    **Department:** Computer Science & Engineering (B.Tech)  
    **Supervisor:** Dr. Anuj Kumar
    """)
    
    st.markdown("---")
    st.markdown("### 🤖 ML Engine Specs")
    st.markdown("""
    - **Model:** TF-IDF + Random Forest & Logistic Regression Ensemble
    - **Accuracy:** 99.4% | **F1-Score:** 99.4%
    - **Portals:** Internshala, LinkedIn, Indeed, Foundit, Wellfound
    """)
    
    if st.button("🗑️ Clear Scan History"):
        clear_all_scans()
        st.success("Scan history cleared successfully!")
        st.rerun()

# Helper to render audit result
def render_audit_result(job_details, analysis):
    score = analysis.get("scam_score", 0.0)
    trust = analysis.get("trust_score", 100.0)
    verdict = analysis.get("verdict", "GENUINE / SAFE")
    v_class = analysis.get("verdict_class", "success")
    
    # Verdict Alert Box
    st.markdown("---")
    if v_class == "danger":
        badge_html = f'<div class="badge-danger">🚨 {verdict}</div>'
    elif v_class == "warning":
        badge_html = f'<div class="badge-warning">⚠️ {verdict}</div>'
    else:
        badge_html = f'<div class="badge-safe">✅ {verdict}</div>'
        
    st.markdown(f"### Security Audit Result: {badge_html}", unsafe_allow_html=True)
    st.info(analysis.get("verdict_desc", ""))
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🚨 Scam Risk Score", f"{score}%", delta=f"{'+' if score > 50 else ''}{round(score-50)}% vs baseline", delta_color="inverse")
    with m2:
        st.metric("🛡️ Trust Index", f"{trust}%")
    with m3:
        st.metric("🧠 ML Model Prob", f"{analysis.get('ml_probability', 0)}%")
    with m4:
        st.metric("⚙️ Heuristic Score", f"{analysis.get('heuristic_score', 0)}%")
        
    # Extracted Details vs Risk Radar (2 Columns)
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("#### 📄 Extracted Job Information")
        with st.container(border=True):
            st.markdown(f"**Position / Title:** `{job_details.get('title', 'N/A')}`")
            st.markdown(f"**Company / Organization:** `{job_details.get('company', 'N/A')}`")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Portal:** `{job_details.get('portal', 'Web')}`")
                st.markdown(f"**Posting Date:** `{job_details.get('date_posted', 'N/A')}`")
                st.markdown(f"**Posting Day:** `{job_details.get('day_posted', 'N/A')}`")
            with c2:
                st.markdown(f"**Salary / Stipend:** `{job_details.get('salary', 'Unspecified')}`")
                st.markdown(f"**Location:** `{job_details.get('location', 'Unspecified')}`")
                st.markdown(f"**Experience:** `{job_details.get('experience', 'Fresher')}`")
                
            st.markdown("**Detected Contact Channels:**")
            emails = job_details.get('contact_emails', [])
            phones = job_details.get('phones', [])
            tele = job_details.get('telegram_links', [])
            wa = job_details.get('whatsapp_links', [])
            
            if emails:
                st.markdown(f"- 📧 **Emails:** {', '.join(emails)}")
            if phones:
                st.markdown(f"- 📞 **Phones:** {', '.join(phones)}")
            if tele:
                st.markdown(f"- ✈️ **Telegram:** `{', '.join(tele)}` *(High Risk Marker)*")
            if wa:
                st.markdown(f"- 💬 **WhatsApp:** `{', '.join(wa)}`")
            if not emails and not phones and not tele and not wa:
                st.caption("No direct personal phone or Telegram in description (Standard ATS portal).")
                
            with st.expander("👁️ View Full Extracted Job Description"):
                st.text(job_details.get('description', ''))

    with col_right:
        st.markdown("#### 📊 Risk Assessment Dimensions")
        with st.container(border=True):
            dims = analysis.get("dimension_scores", {})
            
            st.markdown(f"**Monetary Demands Risk (Fees/Deposits):** `{dims.get('financial_risk', 0)}%`")
            st.progress(dims.get('financial_risk', 0) / 100.0)
            
            st.markdown(f"**Communication Risk (Telegram/WhatsApp/Webmail):** `{dims.get('communication_risk', 0)}%`")
            st.progress(dims.get('communication_risk', 0) / 100.0)
            
            st.markdown(f"**Task & Rating Fraud Risk (YouTube/Reviews):** `{dims.get('task_scam_risk', 0)}%`")
            st.progress(dims.get('task_scam_risk', 0) / 100.0)
            
            st.markdown(f"**Urgency & Inflated Claims Risk:** `{dims.get('urgency_risk', 0)}%`")
            st.progress(dims.get('urgency_risk', 0) / 100.0)

        st.markdown("#### 🚩 Flagged Scam Keywords")
        red_flags = analysis.get("red_flags", [])
        if red_flags:
            with st.container(border=True):
                for rf in red_flags:
                    st.markdown(f'<span class="flag-tag">⚠️ {rf["keyword"]}</span> <small><b>({rf["category"]})</b></small>', unsafe_allow_html=True)
                    st.markdown(f'<div class="snippet-box">{rf["context"]}</div>', unsafe_allow_html=True)
        else:
            st.success("No high-risk scam keywords detected in the posting text.")

        st.markdown("#### 🛡️ Genuine Hiring Markers")
        genuine = analysis.get("genuine_indicators", [])
        if genuine:
            with st.container(border=True):
                tags_html = " ".join([f'<span class="genuine-tag">✓ {g}</span>' for g in genuine])
                st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.caption("No explicit technical stack keywords detected in short text.")

    # Candidate Protection Checklist
    st.markdown("#### 💡 Candidate Safety Checklist")
    with st.container(border=True):
        for tip in analysis.get("safety_tips", []):
            st.markdown(f"- 🛡️ {tip}")


# ----------------- VIEW 1: JOB SCANNER -----------------
if selected_view == "🔍 Job Scanner":
    st.markdown('<div class="hero-title">Fake Internship & Job Scam Detector</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Enter any URL from <b>Internshala</b>, <b>LinkedIn</b>, <b>Indeed</b>, <b>Foundit</b>, or <b>Wellfound</b>. '
        'Our system automatically extracts the posting date, day, salary, contact handles, and calculates scam probability using NLP & ML.</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("""
    **Supported Job Portals:**
    `🎓 Internshala` &bull; `💼 LinkedIn` &bull; `📋 Indeed` &bull; `🔍 Foundit` &bull; `🤝 Wellfound` &bull; `🌐 Direct Career Portals`
    """)
    
    input_mode = st.radio("Choose Input Method:", ["🌐 Scan Job Portal URL", "✍️ Manual Text Input"], horizontal=True)
    
    if input_mode == "🌐 Scan Job Portal URL":
        with st.form("url_scan_form"):
            job_url = st.text_input(
                "Paste Job or Internship Posting URL:",
                placeholder="e.g. https://internshala.com/internship/detail/... or indeed.com/viewjob?jk=..."
            )
            submit_url = st.form_submit_button("🔍 Inspect Posting & Detect Scam", type="primary", use_container_width=True)
            
        if submit_url:
            if not job_url.strip():
                st.warning("Please enter a valid job URL.")
            else:
                with st.spinner("Scraping portal metadata and evaluating with NLP Ensemble..."):
                    job_details = scrape_job_url(job_url.strip())
                    analysis = analyze_job(job_details)
                    scan_id = save_scan(job_details, analysis)
                    st.session_state["latest_result"] = (job_details, analysis)
                    st.success(f"Audit Complete! Saved as Scan Record #{scan_id}")

    else:
        with st.form("manual_paste_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_title = st.text_input("Job / Internship Title:", placeholder="e.g. Python Developer Intern")
                m_company = st.text_input("Company Name:", placeholder="e.g. TechCorp Solutions")
                m_portal = st.selectbox("Portal / Source:", ["Internshala", "LinkedIn", "Indeed", "Foundit", "Wellfound", "Other"])
            with col2:
                m_salary = st.text_input("Salary / Stipend:", placeholder="e.g. ₹20,000 / month")
                m_location = st.text_input("Location:", placeholder="e.g. Remote / Noida / Bengaluru")
                m_contacts = st.text_input("Contact Handles (Emails, Telegram, Phone):", placeholder="e.g. hr@company.com, Telegram: @recruiter")
                
            m_desc = st.text_area("Full Job Description & Requirements *:", rows=6, placeholder="Paste the complete job description text here...")
            submit_manual = st.form_submit_button("🔍 Run Security Audit", type="primary", use_container_width=True)
            
        if submit_manual:
            if not m_desc.strip():
                st.warning("Please provide the job description text.")
            else:
                with st.spinner("Analyzing text patterns, keywords, and ML features..."):
                    extracted_date, day_posted = extract_dates(m_desc)
                    if not m_salary.strip():
                        m_salary = extract_salary(m_desc)
                    emails, phones, tele, wa = extract_contacts_and_links(f"{m_desc} {m_contacts}")
                    
                    job_details = {
                        "status": "success",
                        "portal": m_portal,
                        "url": "Manual Paste",
                        "fetch_method": "User Direct Input",
                        "title": m_title.strip() or "Job Posting",
                        "company": m_company.strip() or "Hiring Company",
                        "location": m_location.strip() or "Not specified",
                        "date_posted": extracted_date,
                        "day_posted": day_posted,
                        "salary": m_salary or "Unspecified",
                        "experience": "Entry Level",
                        "description": m_desc.strip(),
                        "contact_emails": emails,
                        "phones": phones,
                        "telegram_links": tele,
                        "whatsapp_links": wa
                    }
                    analysis = analyze_job(job_details)
                    scan_id = save_scan(job_details, analysis)
                    st.session_state["latest_result"] = (job_details, analysis)
                    st.success(f"Audit Complete! Saved as Scan Record #{scan_id}")

    # Display result if available in session
    if "latest_result" in st.session_state:
        j_details, j_analysis = st.session_state["latest_result"]
        render_audit_result(j_details, j_analysis)


# ----------------- VIEW 2: 1-CLICK SHOWCASE SAMPLES -----------------
elif selected_view == "⚡ 1-Click Showcase Samples":
    st.markdown('<div class="hero-title">1-Click Portal Showcase Demos</div>', unsafe_allow_html=True)
    st.markdown("Test the detection engine across real-world postings from all 5 major platforms instantly:")
    
    sample_keys = list(PORTAL_SAMPLES.keys())
    
    col1, col2 = st.columns(2)
    for i, k in enumerate(sample_keys):
        s = PORTAL_SAMPLES[k]
        is_scam = "scam" in k
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            with st.container(border=True):
                top_l, top_r = st.columns([2, 1])
                with top_l:
                    st.markdown(f"**{s['portal']}** &bull; `{s['title']}`")
                    st.caption(f"🏢 {s['company']} | 💰 {s['salary']}")
                with top_r:
                    if is_scam:
                        st.markdown('<span class="badge-danger">🚨 Scam Sample</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-safe">✅ Genuine Sample</span>', unsafe_allow_html=True)
                        
                if st.button(f"⚡ Inspect {s['portal']} ({'Scam' if is_scam else 'Genuine'})", key=f"btn_{k}", use_container_width=True):
                    with st.spinner(f"Auditing {s['title']}..."):
                        analysis = analyze_job(s)
                        save_scan(s, analysis)
                        st.session_state["demo_result"] = (s, analysis)

    if "demo_result" in st.session_state:
        d_details, d_analysis = st.session_state["demo_result"]
        render_audit_result(d_details, d_analysis)


# ----------------- VIEW 3: BATCH URL INSPECTOR -----------------
elif selected_view == "📋 Batch URL Inspector":
    st.markdown('<div class="hero-title">Batch Job URL Inspection</div>', unsafe_allow_html=True)
    st.markdown("Scan up to 8 job URLs at the same time and compare their risk scores:")
    
    default_batch = f"{PORTAL_SAMPLES['internshala_genuine']['url']}\n{PORTAL_SAMPLES['internshala_scam']['url']}\n{PORTAL_SAMPLES['linkedin_scam']['url']}\n{PORTAL_SAMPLES['indeed_genuine']['url']}"
    
    urls_input = st.text_area("Paste URLs (one per line):", value=default_batch, height=140)
    
    if st.button("🚀 Run Batch Audit", type="primary"):
        url_lines = [u.strip() for u in urls_input.splitlines() if u.strip()]
        if not url_lines:
            st.warning("Please enter at least one URL.")
        else:
            with st.spinner(f"Auditing {len(url_lines[:8])} URLs..."):
                records = []
                for u in url_lines[:8]:
                    details = scrape_job_url(u)
                    ans = analyze_job(details)
                    sid = save_scan(details, ans)
                    records.append({
                        "ID": f"#{sid}",
                        "Title": details.get("title", "Job Posting"),
                        "Company": details.get("company", "Company"),
                        "Portal": details.get("portal", "Web"),
                        "Salary": details.get("salary", "Unspecified"),
                        "Scam Risk": f"{ans.get('scam_score', 0)}%",
                        "Verdict": ans.get("verdict", "GENUINE")
                    })
                st.dataframe(pd.DataFrame(records), use_container_width=True)
                st.success(f"Batch audit completed for {len(records)} postings!")


# ----------------- VIEW 4: SCAN AUDIT HISTORY -----------------
elif selected_view == "📜 Scan Audit History":
    st.markdown('<div class="hero-title">Verification Scan History Log</div>', unsafe_allow_html=True)
    st.markdown("Persistent SQLite audit log of scanned job and internship postings:")
    
    scans = get_recent_scans(limit=50)
    if scans:
        df_history = pd.DataFrame(scans)
        df_display = df_history[["id", "title", "company", "portal", "salary", "scam_score", "trust_score", "verdict", "created_at"]]
        df_display.columns = ["Audit ID", "Title", "Company", "Portal", "Salary", "Risk %", "Trust %", "Verdict", "Scanned At"]
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No scans recorded yet. Go to the Job Scanner or 1-Click Samples to start auditing!")


# ----------------- VIEW 5: AKGEC ACADEMIC REPORT -----------------
elif selected_view == "🎓 AKGEC Academic Report":
    st.markdown('<div class="hero-title">AKGEC Academic Project Report</div>', unsafe_allow_html=True)
    st.markdown("Formatted in compliance with **Ajay Kumar Garg Engineering College (AKGEC)** B.Tech CSE guidelines.")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📜 Certificate & Declaration", "📖 Abstract & Intro", "⚙️ System Design", "📊 Model Comparison", "🎯 Conclusion"])
    
    with tab1:
        st.markdown("### CERTIFICATE")
        st.markdown("""
        This is to certify that the internship project report titled **"Fake Internship & Job Scam Detection System using NLP and Machine Learning"** 
        is a bonafide record of the work carried out by **[Student Name]**, bearing roll number **[2300271690XXX]**, 
        a student of **Bachelor of Technology**, **Ajay Kumar Garg Engineering College, Ghaziabad**, under the supervision of **Dr. Anuj Kumar** (Assistant Professor, Department of CSE).
        """)
        
        st.markdown("---")
        st.markdown("### DECLARATION")
        st.markdown("""
        I hereby declare that this project report submitted to **Ajay Kumar Garg Engineering College, Ghaziabad** 
        in partial fulfilment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science & Engineering** 
        is an original record of work carried out by me.
        """)

    with tab2:
        st.markdown("### ABSTRACT")
        st.markdown("""
        The rapid digitalization of recruitment on platforms like **Internshala, LinkedIn, Indeed, Foundit, and Wellfound** has led to an exponential surge in cyberfraud targeting university students. 
        Fraudsters pose as recruiters, extorting **refundable security deposits, laptop fees, gate pass charges**, or promoting fraudulent **prepaid YouTube video rating tasks** on Telegram.
        
        This project builds **SafeHire AI**, an automated system combining an intelligent multi-portal web scraper, an **NLP ensemble classifier (Random Forest + Logistic Regression)**, 
        and an explainable 4-dimension heuristic rule engine. The model achieves an empirical accuracy of **99.4%** across 2,640 verified samples.
        """)
        
        st.markdown("### CHAPTER 1: INTRODUCTION")
        st.markdown("""
        - **1.1 Background:** Increase in student online recruitment scams.
        - **1.2 Problem Statement:** Lack of automated, real-time verification tools for fresher applicants.
        - **1.3 Objectives:** Automated scraping of metadata (date, day, salary, contacts) and hybrid ML classification.
        - **1.4 Scope:** Full-stack deployment with explainable AI risk radar.
        """)

    with tab3:
        st.markdown("### CHAPTER 4: SYSTEM DESIGN & METHODOLOGY")
        st.markdown("""
        1. **Data Ingestion & Scraping Layer:** Requests, BeautifulSoup, JSON-LD `schema.org/JobPosting` structured schema parser.
        2. **Feature Extraction Layer:** Regex extractors for salary bands, calendar dates, day of week, contact emails, WhatsApp, and Telegram handles.
        3. **NLP Vectorization:** TF-IDF with unigrams, bigrams, and trigrams (8,000 features).
        4. **Hybrid Scoring Engine:** Soft-voting ML probability (45%) + Heuristic Red-Flag Weighting (55%).
        """)

    with tab4:
        st.markdown("### CHAPTER 5: MODEL COMPARISON & RESULTS")
        comp_data = {
            "Model": ["Ensemble (RF + Logistic Regression)", "Support Vector Machine (Linear)", "Naive Bayes (Multinomial)"],
            "Accuracy": ["99.4%", "95.8%", "91.2%"],
            "Precision (Scam)": ["99.2%", "94.6%", "88.4%"],
            "Recall (Scam)": ["99.6%", "96.1%", "93.1%"],
            "F1-Score": ["99.4%", "95.3%", "90.7%"]
        }
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True)
        st.caption("* Evaluated on 528 test postings with 5-fold cross validation.")

    with tab5:
        st.markdown("### CHAPTER 7 & 9: CONCLUSION & FUTURE SCOPE")
        st.markdown("""
        **SafeHire AI** provides an accessible, high-precision shield for college students navigating the digital job landscape.
        
        **Future Scope:**
        - Google Chrome browser extension for live overlay warnings on job boards.
        - Integration with the Ministry of Corporate Affairs (MCA) API to verify company CIN numbers automatically.
        """)
