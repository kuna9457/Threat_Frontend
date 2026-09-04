import streamlit as st
import requests
import pandas as pd
import os
import json
import io
from datetime import datetime

st.set_page_config(
    page_title="ICICI Bank — Cyber Threat Intelligence Platform",
    page_icon="🏦",
    layout="wide",
)

# ── ICICI Bank Color Palette ──────────────────────────────────────────────────
# Primary  : #F37224  (ICICI Orange)
# Secondary: #1C3E73  (ICICI Navy)
# Accent   : #E8300B  (ICICI Red)
# BG       : #F7F8FA  (Light official background)

ICICI_ORANGE = "#F37224"
ICICI_NAVY   = "#1C3E73"
ICICI_RED    = "#E8300B"
ICICI_LIGHT  = "#FFF3EB"
ICICI_LOGO   = "https://www.icicibank.com/content/dam/icicibank/india/managed-assets/images/icici-bank-logo.png"

st.markdown(f"""
<style>
    /* ── Google Font ────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Root overrides ─────────────────────────────────────────────────── */
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    .stApp {{ background-color: #F7F8FA !important; }}
    .main .block-container {{ padding-top: 0.5rem; max-width: 1200px; }}

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {ICICI_NAVY} 0%, #142d5a 100%) !important;
    }}
    [data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
    [data-testid="stSidebar"] .stRadio label {{ color: #CBD5E1 !important; }}
    [data-testid="stSidebar"] .stRadio label:hover {{ color: {ICICI_ORANGE} !important; }}
    [data-testid="stSidebar"] input {{ background: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2) !important; }}

    /* ── Page Header Banner ──────────────────────────────────────────────── */
    .icici-header {{
        background: linear-gradient(135deg, {ICICI_NAVY} 0%, #2a5298 100%);
        padding: 18px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 22px;
        box-shadow: 0 4px 20px rgba(28,62,115,0.25);
        border-left: 6px solid {ICICI_ORANGE};
    }}
    .icici-header-text {{ flex: 1; }}
    .icici-header-text h1 {{
        color: #FFFFFF !important;
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        margin: 0 0 4px 0 !important;
        letter-spacing: 0.3px;
    }}
    .icici-header-text p {{
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.82rem !important;
        margin: 0 !important;
    }}
    .icici-dept-tag {{
        background: {ICICI_ORANGE};
        color: #FFFFFF !important;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        white-space: nowrap;
    }}

    /* ── Metric Cards ────────────────────────────────────────────────────── */
    div[data-testid="metric-container"] {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 3px solid {ICICI_ORANGE};
    }}
    div[data-testid="metric-container"] label {{
        color: #64748B !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    div[data-testid="metric-container"] [data-testid="metric-value"] {{
        color: {ICICI_NAVY} !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }}

    /* ── Verdict Badges ──────────────────────────────────────────────────── */
    .badge {{
        display: inline-block; padding: 6px 20px;
        border-radius: 20px; font-weight: 700;
        font-size: 0.95rem; letter-spacing: 0.5px;
    }}
    .badge-allow  {{ background: #ECFDF5; color: #065F46; border: 1.5px solid #059669; }}
    .badge-review {{ background: #FFFBEB; color: #92400E; border: 1.5px solid #D97706; }}
    .badge-block  {{ background: #FEF2F2; color: #991B1B; border: 1.5px solid {ICICI_RED}; }}

    /* ── Section Heading Cards ───────────────────────────────────────────── */
    .section-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px 26px;
        margin: 14px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .section-card h3, .section-card h4 {{
        color: {ICICI_NAVY} !important;
        font-weight: 700 !important;
    }}

    /* ── Grade Badges ────────────────────────────────────────────────────── */
    .grade-badge {{
        display: inline-block; padding: 8px 22px;
        border-radius: 10px; font-weight: 800; font-size: 1.8rem;
    }}
    .grade-a {{ background: #ECFDF5; color: #065F46; border: 2px solid #059669; }}
    .grade-b {{ background: #F0FDF4; color: #166534; border: 2px solid #16A34A; }}
    .grade-c {{ background: #FFFBEB; color: #92400E; border: 2px solid #D97706; }}
    .grade-d {{ background: #FFF7ED; color: #9A3412; border: 2px solid #EA580C; }}
    .grade-f {{ background: #FEF2F2; color: #991B1B; border: 2px solid {ICICI_RED}; }}

    /* ── Category Colors ─────────────────────────────────────────────────── */
    .cat-malicious  {{ color: {ICICI_RED}; font-weight: 600; }}
    .cat-suspicious {{ color: #D97706; font-weight: 600; }}
    .cat-harmless   {{ color: #059669; }}
    .cat-undetected {{ color: #94A3B8; }}

    /* ── Dividers ────────────────────────────────────────────────────────── */
    .section-divider {{
        border-top: 1px solid #E2E8F0;
        margin: 1.5rem 0;
    }}

    /* ── Email Qualification Banners ─────────────────────────────────────── */
    .email-qualify-banner {{
        padding: 16px 28px; border-radius: 12px; margin: 18px 0;
        text-align: center; font-size: 1.1rem; font-weight: 800; letter-spacing: 1px;
    }}
    .email-qualify-pass  {{ background: #ECFDF5; color: #065F46; border: 2px solid #059669; }}
    .email-qualify-fail  {{ background: #FEF2F2; color: #991B1B; border: 2px solid {ICICI_RED}; }}
    .email-qualify-warn  {{ background: #FFFBEB; color: #92400E; border: 2px solid #D97706; }}

    /* ── SPF / DMARC / DKIM Policy Badges ───────────────────────────────── */
    .spf-badge, .dmarc-badge, .dkim-badge {{
        display: inline-block; padding: 4px 14px; border-radius: 8px;
        font-weight: 700; font-size: 0.9rem; margin-left: 8px;
    }}
    .policy-hard   {{ background:#ECFDF5; color:#065F46; border:1px solid #059669; }}
    .policy-soft   {{ background:#F0FDF4; color:#166534; border:1px solid #16A34A; }}
    .policy-none   {{ background:#FFFBEB; color:#92400E; border:1px solid #D97706; }}
    .policy-miss   {{ background:#FEF2F2; color:#991B1B; border:1px solid {ICICI_RED}; }}
    .policy-reject {{ background:#ECFDF5; color:#065F46; border:1px solid #059669; }}
    .policy-quar   {{ background:#F0FDF4; color:#166534; border:1px solid #16A34A; }}

    /* ── Check Cards ─────────────────────────────────────────────────────── */
    .check-card {{
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 18px 22px; margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .check-title {{ font-size: 1rem; font-weight: 700; color: {ICICI_NAVY}; margin-bottom: 6px; }}
    .amber-notice {{
        background: #FFFBEB; border: 1px solid #D97706;
        border-radius: 10px; padding: 12px 18px; color: #92400E;
        font-size: 0.93rem; margin-top: 8px;
    }}

    /* ── Security Pass/Fail ──────────────────────────────────────────────── */
    .security-pass {{ color: #059669; }} 
    .security-fail {{ color: {ICICI_RED}; }}
    .security-warn {{ color: #D97706; }}

    /* ── Headings ────────────────────────────────────────────────────────── */
    h1, h2, h3 {{ color: {ICICI_NAVY} !important; }}
    h4, h5 {{ color: #334155 !important; }}

    /* ── Buttons ─────────────────────────────────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {ICICI_ORANGE}, #e05f0f) !important;
        color: white !important; border: none !important;
        font-weight: 700 !important; border-radius: 10px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(243,114,36,0.35) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(243,114,36,0.5) !important;
    }}

    /* ── Form Submit Buttons ─────────────────────────────────────────────── */
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {ICICI_NAVY}, #2a5298) !important;
        color: white !important; border: none !important;
        font-weight: 700 !important; border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(28,62,115,0.35) !important;
    }}

    /* ── Footer ──────────────────────────────────────────────────────────── */
    .icici-footer {{
        background: {ICICI_NAVY};
        color: rgba(255,255,255,0.7);
        font-size: 0.72rem;
        padding: 14px 24px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
        letter-spacing: 0.3px;
    }}
    .icici-footer span {{ color: {ICICI_ORANGE}; font-weight: 700; }}

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {{
        color: #64748B !important; font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        color: {ICICI_NAVY} !important; border-bottom-color: {ICICI_ORANGE} !important;
    }}

    /* ── Download Buttons ────────────────────────────────────────────────── */
    .stDownloadButton > button {{
        background: #FFFFFF !important; color: {ICICI_NAVY} !important;
        border: 2px solid {ICICI_NAVY} !important;
        font-weight: 600 !important; border-radius: 10px !important;
    }}
    .stDownloadButton > button:hover {{
        background: {ICICI_NAVY} !important; color: white !important;
    }}

    /* ── Confidential Banner ─────────────────────────────────────────────── */
    .confidential-banner {{
        background: linear-gradient(90deg, {ICICI_ORANGE}22, {ICICI_ORANGE}11);
        border: 1px solid {ICICI_ORANGE}66;
        border-left: 4px solid {ICICI_ORANGE};
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #92400E;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 16px;
    }}

    /* ── Dataframe header ────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] thead th {{
        background: {ICICI_NAVY} !important;
        color: white !important;
    }}
</style>
""", unsafe_allow_html=True)


# ── ICICI Header Component ────────────────────────────────────────────────────
def render_icici_header(page_subtitle: str = "Cyber Threat Intelligence Platform"):
    st.markdown(f"""
    <div class="icici-header">
        <img src="{ICICI_LOGO}" style="height:48px; object-fit:contain; filter:brightness(0) invert(1);" 
             onerror="this.style.display='none'" alt="ICICI Bank">
        <div class="icici-header-text">
            <h1>ICICI Bank &mdash; {page_subtitle}</h1>
            <p>Information Security Group &nbsp;&bull;&nbsp; Cyber Risk &amp; Intelligence Unit</p>
        </div>
        <div class="icici-dept-tag">🔒 Internal Use Only</div>
    </div>
    <div class="confidential-banner">
        🔐 &nbsp; STRICTLY CONFIDENTIAL — FOR AUTHORISED ICICI BANK PERSONNEL ONLY
    </div>
    """, unsafe_allow_html=True)


# ── ICICI Footer ──────────────────────────────────────────────────────────────
def render_icici_footer():
    now = datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    st.markdown(f"""
    <div class="icici-footer">
        <span>ICICI Bank Limited</span> &nbsp;|&nbsp; Information Security Group &nbsp;|&nbsp;
        Cyber Risk &amp; Intelligence Unit &nbsp;|&nbsp; Confidential &mdash; For Internal Use Only<br>
        <span style="color:rgba(255,255,255,0.4); font-size:0.68rem;">
            Report generated on {now} &nbsp;&bull;&nbsp; Powered by VirusTotal · SSL Labs · URLScan · AbuseIPDB
        </span>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:10px 0 6px 0;">
        <img src="{ICICI_LOGO}" style="height:40px; object-fit:contain; filter:brightness(0) invert(1);"
             onerror="this.style.display='none'" alt="ICICI Bank">
        <div style="color:{ICICI_ORANGE}; font-weight:800; font-size:1.05rem; margin-top:8px; letter-spacing:0.5px;">
            ICICI Bank
        </div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; letter-spacing:0.3px;">
            Information Security Group
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.15); margin: 10px 0;">
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigation")
    app_mode = st.radio(
        "Select Module",
        ["Threat Scanner", "Enterprise Risk Assessment", "Email Assessment"]
    )
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    default_api = os.getenv("BACKEND_API_URL", "http://localhost:8001/api/v1")
    api_url = st.text_input("Backend API URL", value=default_api)
    st.info("Ensure the ICICI Bank backend service is running.")
    st.markdown("---")
    st.markdown("**Intelligence Sources**")
    st.markdown(
        "- 🔬 VirusTotal (90+ engines)\n"
        "- 🔍 WHOIS / Domain Age\n"
        "- 🛡️ Google Safe Browsing\n"
        "- 🌐 URLScan.io\n"
        "- 🚫 AbuseIPDB\n"
        "- 🔒 SSL Labs (Qualys)\n"
        "- 📧 MX / DNS Analysis"
    )
    st.markdown("---")
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.4); font-size:0.68rem; text-align:center;'>"
        f"ICICI Bank Ltd. &copy; {datetime.now().year}<br>For Authorised Personnel Only</div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENTERPRISE RISK ASSESSMENT PAGE
# ══════════════════════════════════════════════════════════════════════════════
if app_mode == "Enterprise Risk Assessment":
    render_icici_header("Enterprise Risk Exception Assessment")

    st.markdown(
        "<p style='color:#64748B; margin-top:-10px;'>"
        "Assess security risk for requested URL exceptions and generate a formal enterprise risk report "
        "in accordance with ICICI Bank Information Security Policy.</p>",
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.form("risk_assessment_form"):
        assess_url = st.text_input(
            "🌐 URL to Assess", placeholder="https://example.com",
            help="Enter the full URL requiring exception approval"
        )

        req_col, ctrl_col = st.columns(2)

        with req_col:
            st.markdown(f"#### <span style='color:{ICICI_ORANGE}'>📝 Exception Requests</span>", unsafe_allow_html=True)
            req_opts = [
                "Allow Upload", "Allow Download", "Disable SSL Inspection",
                "Sandbox Bypass", "Remove Browser Isolation", "Allow External Sharing",
                "Allow Executable Download", "Allow Remote Access Tool", "Allow Browser Extension"
            ]
            selected_reqs = []
            for opt in req_opts:
                if st.checkbox(opt, key=f"req_{opt}"):
                    selected_reqs.append(opt)

            st.markdown(f"#### <span style='color:{ICICI_ORANGE}'>💬 Business Justification</span>", unsafe_allow_html=True)
            business_justification = st.text_area(
                "Why is this access required?", height=100,
                placeholder="Provide a clear business rationale for the security exception..."
            )

        with ctrl_col:
            st.markdown(f"#### <span style='color:{ICICI_ORANGE}'>🛡️ Existing Security Controls</span>", unsafe_allow_html=True)
            ctrl_opts = [
                "Endpoint AV", "EDR", "DLP", "CASB", "MFA", "Logging Enabled",
                "SIEM Monitoring", "DNS Security", "File Type Restriction",
                "URL Filtering", "SSL Inspection"
            ]
            selected_ctrls = []
            for opt in ctrl_opts:
                if st.checkbox(opt, key=f"ctrl_{opt}"):
                    selected_ctrls.append(opt)

        submit_risk = st.form_submit_button("📊 Generate Risk Assessment Report", width='stretch')

    if submit_risk:
        if not assess_url:
            st.error("Please enter a URL to assess.")
        elif not selected_reqs:
            st.error("Please select at least one Exception Request.")
        elif not business_justification:
            st.error("Please provide a business justification.")
        else:
            with st.spinner("Performing threat intelligence analysis and risk scoring…"):
                payload = {
                    "url": assess_url,
                    "request_types": selected_reqs,
                    "business_justification": business_justification,
                    "existing_controls": selected_ctrls
                }
                try:
                    resp = requests.post(f"{api_url}/assess-risk", json=payload, timeout=300)
                    resp.raise_for_status()
                    data = resp.json()

                    st.success("✅ Assessment Complete — Report Generated Successfully")

                    # Report Header
                    ref_no = f"ICICI-CIT-{datetime.now().strftime('%Y%m%d')}-{abs(hash(assess_url)) % 9000 + 1000}"
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px 26px; margin:16px 0; box-shadow:0 2px 10px rgba(0,0,0,0.06);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="color:{ICICI_NAVY}; font-weight:800; font-size:1.15rem;">📋 Risk Assessment Report</div>
                                <div style="color:#64748B; font-size:0.8rem; margin-top:4px;">
                                    Reference: <b>{ref_no}</b> &nbsp;|&nbsp; 
                                    Generated: <b>{datetime.now().strftime('%d %b %Y, %I:%M %p IST')}</b>
                                </div>
                            </div>
                            <div style="background:{ICICI_ORANGE}; color:white; padding:8px 18px; border-radius:20px; font-size:0.75rem; font-weight:700; text-transform:uppercase;">
                                Official Assessment
                            </div>
                        </div>
                        <hr style="border-color:#E2E8F0; margin:14px 0 10px 0;">
                        <div style="color:#64748B; font-size:0.82rem;">
                            <b style="color:{ICICI_NAVY};">URL Under Assessment:</b> {assess_url}<br>
                            <b style="color:{ICICI_NAVY};">Business Justification:</b> {business_justification}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Risk Scores
                    st.markdown(f"#### <span style='color:{ICICI_NAVY}'>📊 Risk Assessment Results</span>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    c1.metric("Inherent Risk Score", f"{data['inherent_risk_score']} / 100",
                              data['inherent_risk_classification'], delta_color="inverse")
                    c2.metric("Residual Risk Score", f"{data['residual_risk_score']} / 100",
                              data['residual_risk_classification'], delta_color="inverse")

                    st.markdown("---")
                    st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🛡️ Applied Compensating Controls</span>", unsafe_allow_html=True)
                    if data['applied_controls']:
                        for ac in data['applied_controls']:
                            st.markdown(
                                f"- **{ac['control']}** — reduces risk by `{ac['risk_reduction']}` points"
                            )
                    else:
                        st.info("No mapped compensating controls selected.")

                    st.markdown("---")
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        st.markdown(f"#### <span style='color:{ICICI_RED}'>🚨 Threat Analysis</span>", unsafe_allow_html=True)
                        for t in data['threat_analysis']:
                            st.markdown(f"- {t}")
                    with rc2:
                        st.markdown(f"#### <span style='color:{ICICI_NAVY}'>💡 Mitigation Controls</span>", unsafe_allow_html=True)
                        for s in data['suggested_mitigation_controls']:
                            st.markdown(f"- {s}")

                    st.markdown("---")
                    st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🎯 Final Recommendation</span>", unsafe_allow_html=True)
                    rec = data['final_recommendation']
                    if "ALLOW" in rec and "BLOCK" not in rec:
                        rec_bg = "#ECFDF5"; rec_border = "#059669"; rec_text = "#065F46"
                    elif "COMPENSATING" in rec:
                        rec_bg = "#FFFBEB"; rec_border = "#D97706"; rec_text = "#92400E"
                    else:
                        rec_bg = "#FEF2F2"; rec_border = ICICI_RED; rec_text = "#991B1B"

                    st.markdown(
                        f"<div style='text-align:center; padding:22px; border-radius:12px; "
                        f"border:2px solid {rec_border}; background:{rec_bg}; margin:10px 0;'>"
                        f"<h2 style='color:{rec_text}; margin:0; font-size:1.5rem;'>{rec}</h2>"
                        f"<p style='color:{rec_text}; opacity:0.7; font-size:0.8rem; margin:8px 0 0 0;'>"
                        f"ICICI Bank Information Security Group — {datetime.now().strftime('%d %B %Y')}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error(f"❌ Assessment Failed: {e}")

    render_icici_footer()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL ASSESSMENT PAGE
# ══════════════════════════════════════════════════════════════════════════════
if app_mode == "Email Assessment":
    render_icici_header("Email Security Posture Validator")
    st.markdown(
        "<p style='color:#64748B; margin-top:-10px;'>"
        "Validate <b>SPF</b>, <b>DKIM</b>, and <b>DMARC</b> records for any domain against the "
        "<b>Section 7 Qualification Standard</b> for automated counterparty whitelisting.</p>",
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    def _spf_badge(policy: str) -> str:
        cls = {"-all": "policy-hard", "~all": "policy-soft",
               "+all": "policy-miss", "?all": "policy-none",
               "missing": "policy-miss", "none": "policy-none"}.get(policy, "policy-none")
        return f"<span class='spf-badge {cls}'>{policy}</span>"

    def _dmarc_badge(policy: str) -> str:
        cls = {"reject": "policy-reject", "quarantine": "policy-quar",
               "none": "policy-none", "missing": "policy-miss"}.get(policy, "policy-none")
        return f"<span class='dmarc-badge {cls}'>{policy}</span>"

    def _check_icon(passed: bool, warn: bool = False) -> str:
        if passed: return "✅"
        if warn:   return "⚠️"
        return "❌"

    def _render_email_result(data: dict):
        domain_label = data.get("domain", "Unknown")
        meets = data.get("meets_qualification", False)
        spf   = data.get("spf", {})
        dmarc = data.get("dmarc", {})
        dkim  = data.get("dkim", {})
        header_parse = data.get("header_parse")

        if meets:
            banner_cls = "email-qualify-pass"
            banner_txt = "✅ PASSED — QUALIFIES FOR WHITELISTING"
        elif not spf.get("pass") and not dmarc.get("pass"):
            banner_cls = "email-qualify-fail"
            banner_txt = "❌ ACTION REQUIRED — SPF & DMARC POLICIES FAIL SECTION 7"
        elif not dkim.get("pass"):
            banner_cls = "email-qualify-warn"
            banner_txt = "⚠️ REVIEW REQUIRED — DKIM NOT VERIFIED"
        else:
            banner_cls = "email-qualify-fail"
            banner_txt = "❌ ACTION REQUIRED — DOES NOT MEET SECTION 7 CRITERIA"

        st.markdown(
            f"<div class='email-qualify-banner {banner_cls}'>{banner_txt}</div>",
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("SPF",   _check_icon(spf.get("pass", False))   + " " + spf.get("policy", "missing"))
        m2.metric("DMARC", _check_icon(dmarc.get("pass", False)) + " " + dmarc.get("policy", "missing"))
        m3.metric("DKIM",  _check_icon(dkim.get("pass", False), warn=True) + " " +
                  ("Found" if dkim.get("pass") else "Not found"))

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🔒 SPF (Sender Policy Framework)</span>", unsafe_allow_html=True)
        st.markdown(
            f"**Policy badge:** {_spf_badge(spf.get('policy', 'missing'))} &nbsp;&nbsp;"
            f"**Pass:** {'Yes ✅' if spf.get('pass') else 'No ❌'}",
            unsafe_allow_html=True,
        )
        if spf.get("record"):
            st.code(spf["record"], language="")
        else:
            st.warning("No SPF TXT record found for this domain.")
        spf_guide = {
            "-all": "✅ HARD FAIL – Strong enforcement. Qualifies.",
            "~all": "✅ SOFT FAIL – Permissive enforcement. Qualifies.",
            "+all": "❌ PERMISSIVE – Any sender allowed. Fails Section 7.",
            "?all": "❌ NEUTRAL – No policy enforced. Fails Section 7.",
            "missing": "❌ MISSING – No SPF record found. Fails Section 7.",
            "none": "❌ NO MECHANISM – Policy unknown. Fails Section 7.",
        }
        st.caption(spf_guide.get(spf.get("policy", "missing"), ""))

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        st.markdown(f"#### <span style='color:{ICICI_NAVY}'>📋 DMARC (Domain-based Message Authentication)</span>", unsafe_allow_html=True)
        st.markdown(
            f"**Policy badge:** {_dmarc_badge(dmarc.get('policy', 'missing'))} &nbsp;&nbsp;"
            f"**Pass:** {'Yes ✅' if dmarc.get('pass') else 'No ❌'}",
            unsafe_allow_html=True,
        )
        if dmarc.get("record"):
            st.code(dmarc["record"], language="")
            dcol1, dcol2 = st.columns(2)
            if dmarc.get("rua"):
                dcol1.markdown(f"**Report Recipient (rua):** `{dmarc['rua']}`")
            if dmarc.get("ruf"):
                dcol2.markdown(f"**Forensic Reports (ruf):** `{dmarc['ruf']}`")
            if dmarc.get("sp"):
                st.markdown(f"**Subdomain Policy (sp):** `{dmarc['sp']}`")
            if dmarc.get("pct"):
                st.markdown(f"**PCT (applies to):** `{dmarc['pct']}%`")
        else:
            st.warning("No DMARC record found at `_dmarc.<domain>`.")
        dmarc_guide = {
            "reject":     "✅ REJECT – Unauthenticated mail is rejected. Qualifies.",
            "quarantine": "✅ QUARANTINE – Unauthenticated mail goes to spam. Qualifies.",
            "none":       "❌ NONE – Monitoring only, no enforcement. Fails Section 7.",
            "missing":    "❌ MISSING – No DMARC record found. Fails Section 7.",
        }
        st.caption(dmarc_guide.get(dmarc.get("policy", "missing"), ""))

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🔑 DKIM (DomainKeys Identified Mail)</span>", unsafe_allow_html=True)
        if dkim.get("pass"):
            selectors_list = dkim.get("selectors_found", [])
            st.success(f"✅ DKIM verified — selectors found: **{', '.join(selectors_list)}**")
            with st.expander("🔍 DKIM Key Records"):
                for sel, rec in dkim.get("records", {}).items():
                    st.markdown(f"**`{sel}._domainkey`**")
                    st.code(rec, language="")
        else:
            st.markdown(
                "<div class='amber-notice'>⚠️ "
                + (dkim.get("disclaimer") or "No DKIM selectors found.")
                + "</div>",
                unsafe_allow_html=True,
            )

        if header_parse and (header_parse.get("domain") or header_parse.get("selectors")):
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>📨 Extracted from Email Header</span>", unsafe_allow_html=True)
            hc1, hc2 = st.columns(2)
            hc1.markdown(f"**Signing Domain (d=):** `{header_parse.get('domain', '—')}`")
            hc2.markdown(f"**Selector(s) (s=):** `{', '.join(header_parse.get('selectors', [])) or '—'}`")

    # Input Tabs
    email_tab1, email_tab2 = st.tabs(["🔎 Single Domain", "📋 Batch Domains"])

    with email_tab1:
        with st.form("email_single_form", clear_on_submit=False):
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🌐 Domain to Validate</span>", unsafe_allow_html=True)
            e_domain = st.text_input(
                "Domain", placeholder="e.g. company.com",
                help="Enter the domain only — no https:// prefix needed.",
            )
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🔑 Custom DKIM Selectors *(optional)*</span>", unsafe_allow_html=True)
            e_selectors = st.text_input(
                "Selectors (comma-separated)", placeholder="e.g. k1, pps1, 2024mail",
                help="DKIM selectors cannot be discovered automatically if non-standard.",
            )
            with st.expander("📨 Extract from Email Header (paste raw headers)"):
                st.caption(
                    "Paste the full raw email headers here. The backend will "
                    "automatically extract the `d=` (domain) and `s=` (selector) "
                    "tags from the DKIM-Signature header."
                )
                e_raw_header = st.text_area(
                    "Raw Email Headers", height=200,
                    placeholder="Paste raw email headers here…",
                    label_visibility="collapsed",
                )
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>⚙️ DNS Resolver</span>", unsafe_allow_html=True)
            e_resolver = st.selectbox(
                "Resolver", options=["default", "google", "quad9"],
                format_func=lambda x: {
                    "default": "Default (Cloudflare 1.1.1.1)",
                    "google":  "Google (8.8.8.8)",
                    "quad9":   "Quad9 (9.9.9.9) — privacy-first",
                }[x],
            )
            e_submit = st.form_submit_button("🔍 Validate Domain", width='stretch')

        if e_submit:
            target_domain = e_domain.strip()
            raw_header_val = e_raw_header.strip() if "e_raw_header" in dir() else ""
            if not target_domain and not raw_header_val:
                st.error("Please enter a domain or paste raw email headers.")
            else:
                custom_sel_list = [
                    s.strip() for s in e_selectors.split(",") if s.strip()
                ] if e_selectors else []
                payload = {
                    "domain":     target_domain,
                    "selectors":  custom_sel_list or None,
                    "raw_header": raw_header_val or None,
                    "resolver":   e_resolver,
                }
                with st.spinner(f"Validating `{target_domain or '(from header)'}` — querying SPF, DMARC & DKIM…"):
                    try:
                        resp = requests.post(
                            f"{api_url}/validate-domain", json=payload, timeout=30,
                        )
                        resp.raise_for_status()
                        result_data = resp.json()
                    except Exception as exc:
                        st.error(f"❌ Backend error: {exc}")
                        st.stop()

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown(f"### Results for `{result_data.get('domain', target_domain)}`")
                _render_email_result(result_data)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown(f"#### <span style='color:{ICICI_NAVY}'>📤 Export Governance Audit Trail</span>", unsafe_allow_html=True)
                exp_c1, exp_c2 = st.columns(2)
                with exp_c1:
                    json_str = json.dumps(result_data, indent=2)
                    st.download_button(
                        label="📋 Download JSON",
                        data=json_str,
                        file_name=f"ICICI_Email_Assessment_{result_data.get('domain','domain')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        width='stretch',
                    )
                with exp_c2:
                    csv_rows = [{
                        "domain":              result_data.get("domain"),
                        "meets_qualification": result_data.get("meets_qualification"),
                        "spf_policy":          result_data.get("spf", {}).get("policy"),
                        "spf_record":          result_data.get("spf", {}).get("record"),
                        "dmarc_policy":        result_data.get("dmarc", {}).get("policy"),
                        "dmarc_rua":           result_data.get("dmarc", {}).get("rua"),
                        "dmarc_record":        result_data.get("dmarc", {}).get("record"),
                        "dkim_found":          result_data.get("dkim", {}).get("pass"),
                        "dkim_selectors":      ", ".join(result_data.get("dkim", {}).get("selectors_found", [])),
                        "resolver_used":       result_data.get("resolver_used"),
                        "assessed_at":         datetime.now().isoformat(),
                    }]
                    csv_buf = io.StringIO()
                    import csv as _csv
                    writer = _csv.DictWriter(csv_buf, fieldnames=csv_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_rows)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_buf.getvalue(),
                        file_name=f"ICICI_Email_Assessment_{result_data.get('domain','domain')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        width='stretch',
                    )

    with email_tab2:
        st.markdown(
            "Enter one domain per line. All domains are validated concurrently "
            "and results are shown in a summary table."
        )
        with st.form("email_batch_form", clear_on_submit=False):
            e_batch_domains = st.text_area(
                "Domains (one per line)",
                placeholder="google.com\nmicrosoft.com\ngithub.com",
                height=140,
            )
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                e_batch_selectors = st.text_input(
                    "Shared Custom Selectors *(optional)*", placeholder="k1, pps1",
                )
            with b_col2:
                e_batch_resolver = st.selectbox(
                    "DNS Resolver",
                    options=["default", "google", "quad9"],
                    format_func=lambda x: {
                        "default": "Cloudflare 1.1.1.1",
                        "google":  "Google 8.8.8.8",
                        "quad9":   "Quad9 9.9.9.9",
                    }[x],
                    key="batch_resolver",
                )
            b_submit = st.form_submit_button("🔍 Validate All", width='stretch')

        if b_submit:
            domains_list = [d.strip() for d in e_batch_domains.strip().splitlines() if d.strip()]
            if not domains_list:
                st.error("Please enter at least one domain.")
            else:
                batch_sel = [
                    s.strip() for s in e_batch_selectors.split(",") if s.strip()
                ] if e_batch_selectors else None
                batch_payload = {
                    "domains":  domains_list,
                    "selectors": batch_sel,
                    "resolver": e_batch_resolver,
                }
                with st.spinner(f"Validating {len(domains_list)} domain(s) concurrently…"):
                    try:
                        resp = requests.post(
                            f"{api_url}/validate-batch", json=batch_payload, timeout=60,
                        )
                        resp.raise_for_status()
                        batch_data = resp.json()
                    except Exception as exc:
                        st.error(f"❌ Backend error: {exc}")
                        st.stop()

                results = batch_data.get("results", [])
                total   = batch_data.get("total", len(results))
                q_count = batch_data.get("qualified_count", 0)
                u_count = batch_data.get("unqualified_count", total)

                sm1, sm2, sm3 = st.columns(3)
                sm1.metric("Total Domains",   total)
                sm2.metric("✅ Qualified",     q_count)
                sm3.metric("❌ Action Needed", u_count)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                table_rows = []
                for r in results:
                    spf_p   = r.get("spf", {}).get("policy", "—")
                    dmarc_p = r.get("dmarc", {}).get("policy", "—")
                    dkim_ok = r.get("dkim", {}).get("pass", False)
                    table_rows.append({
                        "Domain":         r.get("domain", "—"),
                        "Qualifies":      "✅ Yes" if r.get("meets_qualification") else "❌ No",
                        "SPF Policy":     spf_p,
                        "DMARC Policy":   dmarc_p,
                        "DKIM":           "✅ Found" if dkim_ok else "⚠️ Not found",
                        "DKIM Selectors": ", ".join(r.get("dkim", {}).get("selectors_found", [])) or "—",
                    })

                st.dataframe(pd.DataFrame(table_rows), width='stretch', hide_index=True)

                st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🔍 Detailed Results</span>", unsafe_allow_html=True)
                for r in results:
                    qual = r.get("meets_qualification", False)
                    icon = "✅" if qual else "❌"
                    with st.expander(f"{icon} {r.get('domain', '—')}"):
                        _render_email_result(r)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown(f"#### <span style='color:{ICICI_NAVY}'>📤 Export Full Batch Report</span>", unsafe_allow_html=True)
                bc1, bc2 = st.columns(2)
                with bc1:
                    st.download_button(
                        label="📋 Download JSON",
                        data=json.dumps(batch_data, indent=2),
                        file_name=f"ICICI_Email_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        width='stretch',
                    )
                with bc2:
                    csv_buf2 = io.StringIO()
                    import csv as _csv2
                    if table_rows:
                        writer2 = _csv2.DictWriter(csv_buf2, fieldnames=table_rows[0].keys())
                        writer2.writeheader()
                        writer2.writerows(table_rows)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_buf2.getvalue(),
                        file_name=f"ICICI_Email_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        width='stretch',
                    )

    render_icici_footer()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# THREAT SCANNER PAGE
# ══════════════════════════════════════════════════════════════════════════════
render_icici_header("URL Threat Intelligence Scanner")
st.markdown(
    "<p style='color:#64748B; margin-top:-10px;'>"
    "Analyze URLs across <b>90+ security engines</b>, <b>SSL/TLS grading</b>, "
    "and <b>mail-server analysis</b> in accordance with ICICI Bank Cybersecurity Framework.</p>",
    unsafe_allow_html=True
)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Multi-URL Input
st.markdown(f"### <span style='color:{ICICI_NAVY}'>📝 Enter URLs to Scan</span>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; font-size:0.85rem;'>Enter one URL per line for batch scanning.</p>", unsafe_allow_html=True)
urls_text = st.text_area(
    "URLs",
    placeholder="https://google.com\nhttps://example.com\nhttps://github.com",
    label_visibility="collapsed", height=120
)

col_btn1, col_spacer = st.columns([1, 5])
with col_btn1:
    scan_clicked = st.button("🔍 Scan All URLs", width='stretch')


def _grade_class(grade):
    if not grade or grade == "N/A": return "grade-f"
    g = grade.upper()[0]
    return {"A": "grade-a", "B": "grade-b", "C": "grade-c", "D": "grade-d"}.get(g, "grade-f")


def _render_ssl_section(ssl):
    if not ssl or "error" in ssl:
        st.warning(ssl.get("error", "SSL data not available") if ssl else "No SSL data")
        return
    grade = ssl.get("grade", "N/A")
    gc = _grade_class(grade)
    st.markdown(f"**SSL Grade:** <span class='grade-badge {gc}'>{grade}</span>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("IP Address", ssl.get("ip_address", "—"))
    s2.metric("Server Name", ssl.get("server_name", "—") or "—")
    s3.metric("HSTS", ssl.get("hsts", {}).get("status", "unknown").title())
    s4.metric("OCSP Stapling", "Yes" if ssl.get("ocsp_stapling") else "No")

    cert = ssl.get("certificate", {})
    if cert:
        with st.expander("🔐 Certificate Details"):
            for k, v in [("Subject", cert.get("subject")), ("Issuer", cert.get("issuer")),
                         ("Key Algorithm", f"{cert.get('key_alg','')} ({cert.get('key_size','')} bit)"),
                         ("Signature", cert.get("sig_alg")), ("Serial", cert.get("serial")),
                         ("SHA-256", cert.get("sha256_fingerprint"))]:
                if v: st.markdown(f"**{k}:** `{v}`")
            nb, na = cert.get("not_before"), cert.get("not_after")
            if nb:
                try: st.markdown(f"**Valid From:** `{datetime.utcfromtimestamp(nb/1000).strftime('%Y-%m-%d')}`")
                except: pass
            if na:
                try: st.markdown(f"**Valid Until:** `{datetime.utcfromtimestamp(na/1000).strftime('%Y-%m-%d')}`")
                except: pass
            san = cert.get("san", [])
            if san: st.markdown(f"**SANs:** {', '.join(san[:10])}")

    protos = ssl.get("protocols", [])
    if protos:
        with st.expander(f"📡 Protocols ({len(protos)})"):
            pdf_proto = pd.DataFrame(protos)
            st.dataframe(pdf_proto, width='stretch', hide_index=True)

    vulns = ssl.get("vulnerabilities", {})
    if vulns:
        with st.expander("🛡️ Vulnerability Checks"):
            vuln_rows = []
            for k, v in vulns.items():
                label = k.replace("_", " ").title()
                if isinstance(v, bool):
                    status = "🔴 VULNERABLE" if v else "🟢 Safe"
                elif isinstance(v, int):
                    status = "🟢 Safe" if v <= 1 else "🔴 VULNERABLE"
                else:
                    status = str(v)
                vuln_rows.append({"Check": label, "Status": status})
            st.dataframe(pd.DataFrame(vuln_rows), width='stretch', hide_index=True)

    ciphers = ssl.get("cipher_suites", [])
    if ciphers:
        with st.expander(f"🔑 Cipher Suites ({ssl.get('total_cipher_suites', len(ciphers))})"):
            st.dataframe(pd.DataFrame(ciphers), width='stretch', hide_index=True)


def _render_result(result, idx=None):
    data = result.get("data", {})
    vt = data.get("virustotal", {})
    urlscan_data = data.get("urlscan", {})
    abuseipdb_data = data.get("abuseipdb", {})
    ssl = data.get("ssl_labs", {})

    verdict = result.get("verdict", "UNKNOWN")
    badge_class = f"badge-{verdict.lower()}"
    verdict_icon = {"ALLOW": "✅", "REVIEW": "⚠️", "BLOCK": "🚫"}.get(verdict, "❓")
    score = result.get("score", 0)
    score_color = "#059669" if score < 30 else ("#D97706" if score < 60 else ICICI_RED)

    # URL Card Header
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
                padding:20px 26px; margin:14px 0; box-shadow:0 2px 10px rgba(0,0,0,0.06);
                border-left:5px solid {ICICI_ORANGE};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="flex:1;">
                <div style="color:#94A3B8; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">
                    {'#' + str(idx) + ' — URL ASSESSMENT' if idx else 'URL ASSESSMENT'}
                </div>
                <div style="color:{ICICI_NAVY}; font-weight:700; font-size:1.05rem; margin-top:4px; word-break:break-all;">
                    {result.get('url', '')}
                </div>
            </div>
            <div style="text-align:right; margin-left:20px;">
                <div style="color:#94A3B8; font-size:0.7rem;">Risk Score</div>
                <div style="color:{score_color}; font-size:2rem; font-weight:800; line-height:1;">{score}</div>
                <div style="color:#94A3B8; font-size:0.7rem;">/100</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Risk Score", f"{score} / 100")
    c2.metric("🔴 Malicious", vt.get("malicious", 0))
    c3.metric("🟡 Suspicious", vt.get("suspicious", 0))
    c4.metric("🟢 Harmless", vt.get("harmless", 0))
    c5.metric("⚪ Undetected", vt.get("undetected", 0))

    st.markdown(f"**Verdict:** <span class='badge {badge_class}'>{verdict_icon} {verdict}</span>", unsafe_allow_html=True)

    tabs = st.tabs(["🔬 VirusTotal", "🔒 SSL Labs", "🌐 URLScan", "🚫 AbuseIPDB", "📄 Raw JSON"])

    with tabs[0]:
        st.markdown(f"### <span style='color:{ICICI_NAVY}'>🌐 URL Metadata</span>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Domain Age (days)", data.get("domain_age", "Unknown"))
        m2.metric("HTTP Response Code", vt.get("last_http_response_code") or "N/A")
        m3.metric("Times Submitted", vt.get("times_submitted", 0))
        for label, value in [("Final URL", vt.get("final_url") or result.get("url")),
                             ("Page Title", vt.get("title") or "—"),
                             ("Tags", ", ".join(vt.get("tags", [])) or "None"),
                             ("Google Phishing", "⚠️ YES" if data.get("phishing") else "✅ No"),
                             ("Reputation", vt.get("reputation", "N/A"))]:
            st.markdown(f"**{label}:** `{value}`")
        chain = vt.get("redirection_chain", [])
        if chain:
            with st.expander(f"🔀 Redirection Chain ({len(chain)})"):
                for i, hop in enumerate(chain, 1): st.markdown(f"`{i}.` {hop}")
        categories = vt.get("categories", {})
        if categories:
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🏷️ Categories</span>", unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([{"Vendor": k, "Category": v} for k, v in categories.items()]),
                width='stretch', hide_index=True
            )
        analysis_results = vt.get("last_analysis_results", {})
        if analysis_results:
            st.markdown(f"#### <span style='color:{ICICI_NAVY}'>🔬 Engine Results ({len(analysis_results)})</span>", unsafe_allow_html=True)
            fc1, fc2 = st.columns([3, 1])
            with fc1: se = st.text_input("🔎 Search engine", key=f"eng_{idx}")
            with fc2: so = st.selectbox("Filter", ["All", "malicious", "suspicious", "harmless", "undetected"], key=f"cat_{idx}")
            rows = [{"Engine": e, "Category": d.get("category",""), "Result": d.get("result",""), "Method": d.get("method","")}
                    for e, d in analysis_results.items()]
            df = pd.DataFrame(rows).sort_values(by="Category",
                key=lambda s: s.map({"malicious":0,"suspicious":1,"harmless":2,"undetected":3}).fillna(4))
            if so != "All": df = df[df["Category"] == so]
            if se: df = df[df["Engine"].str.contains(se, case=False)]
            def cc(val):
                return {"malicious": f"color:{ICICI_RED};font-weight:600",
                        "suspicious": "color:#D97706;font-weight:600",
                        "harmless": "color:#059669",
                        "undetected": "color:#94A3B8"}.get(val, "")
            st.dataframe(df.style.map(cc, subset=["Category"]), width='stretch', hide_index=True)
            flagged = df[df["Category"].isin(["malicious","suspicious"])]
            if not flagged.empty:
                with st.expander(f"🚨 Flagging Engines ({len(flagged)})"):
                    for _, r in flagged.iterrows():
                        ic = "🔴" if r["Category"] == "malicious" else "🟡"
                        st.markdown(f"{ic} **{r['Engine']}** — `{r['Result']}`")
            else:
                st.success("✅ No engines flagged this URL.")

    with tabs[1]:
        _render_ssl_section(ssl)

    with tabs[2]:
        if "error" in urlscan_data:
            st.warning(urlscan_data["error"])
        else:
            u1, u2, u3 = st.columns(3)
            u1.metric("Malicious", "🚨 YES" if urlscan_data.get("malicious") else "✅ NO")
            u2.metric("Score", urlscan_data.get("score", 0))
            u3.metric("Total Scans", urlscan_data.get("total_scans", 0))
            st.markdown(f"**Country:** {urlscan_data.get('country')} | **Server:** {urlscan_data.get('server')}")
            rurl = urlscan_data.get("report_url", "")
            if rurl and rurl != "No recent scans":
                st.markdown(f"🔗 [View Full Report]({rurl})")

    with tabs[3]:
        if "error" in abuseipdb_data:
            st.warning(abuseipdb_data["error"])
        else:
            a1, a2, a3 = st.columns(3)
            a1.metric("Abuse Confidence", f"{abuseipdb_data.get('abuseConfidenceScore',0)}%")
            a2.metric("Total Reports", abuseipdb_data.get("totalReports", 0))
            a3.metric("Usage Type", abuseipdb_data.get("usageType", "Unknown"))
            st.markdown(f"**IP:** `{abuseipdb_data.get('ip','')}` | **ISP:** {abuseipdb_data.get('isp','')} | **Country:** {abuseipdb_data.get('countryCode','')}")

    with tabs[4]:
        st.json(result)


# Handle Scan
if scan_clicked:
    urls = [u.strip() for u in urls_text.strip().split("\n") if u.strip()]
    if not urls:
        st.error("Please enter at least one URL.")
    else:
        spinner_msg = f"Scanning {len(urls)} URL(s) across all ICICI Bank intelligence sources…"
        if len(urls) > 15:
            spinner_msg += " Large batches are paced to stay within vendor API rate limits, so this can take a while — it will finish, just be patient."
        with st.spinner(spinner_msg):
            try:
                # Large batches (up to 100 URLs) are intentionally rate-limited
                # against VirusTotal/AbuseIPDB/URLScan (see app/utils/rate_limiter.py),
                # so this can legitimately take tens of minutes — the timeout here
                # is generous on purpose rather than fast.
                resp = requests.post(f"{api_url}/scan-batch", json={"urls": urls}, timeout=3600)
                resp.raise_for_status()
                batch = resp.json()
            except Exception as e:
                st.error(f"❌ Failed to reach backend: {e}")
                st.stop()

        results = batch.get("results", [])
        st.session_state["last_results"] = results
        st.success(f"✅ Scanned {len(results)} URL(s) successfully!")

        for idx, res in enumerate(results, 1):
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            _render_result(res, idx)

# Handle PDF Download Configuration & Button
if st.session_state.get("last_results"):
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"### <span style='color:{ICICI_NAVY}'>📄 Report Configuration</span>", unsafe_allow_html=True)
    
    results = st.session_state["last_results"]

    final_comment = st.text_area(
        "Final Comment",
        value="Based on the assessment, no significant security risks were identified",
        height=100,
    )

    download_pdf_clicked = st.button("⚙️ Generate PDF Report", width='stretch', key='gen_pdf')

    if download_pdf_clicked:
        urls = [r["url"] for r in results]
        with st.spinner("Generating ICICI Bank official PDF report…"):
            try:
                payload = {
                    "urls": urls,
                    "final_comment": final_comment
                }
                # Generous on purpose — same reasoning as the scan-batch call above.
                resp = requests.post(f"{api_url}/report/pdf", json=payload, timeout=3600)
                resp.raise_for_status()
                pdf_data = resp.content
                
                st.download_button(
                    label="⬇️ Download ICICI Bank URL Risk Assessment (PDF)",
                    data=pdf_data,
                    file_name=f"ICICI_URL_Risk_Assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    width='stretch',
                )
            except Exception as e:
                st.error(f"❌ Failed to generate PDF: {e}")


# Footer
render_icici_footer()
