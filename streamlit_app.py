import streamlit as st
import requests
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="URL Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark base */
    .stApp { background-color: #0d1117; }
    .main .block-container { padding-top: 2rem; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 20px;
    }

    /* Verdict badge */
    .badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 1px;
    }
    .badge-allow  { background: #0d3d1c; color: #3fb950; border: 1px solid #3fb950; }
    .badge-review { background: #3d2d00; color: #d29922; border: 1px solid #d29922; }
    .badge-block  { background: #3d0000; color: #f85149; border: 1px solid #f85149; }

    /* Engine table */
    .engine-row { font-size: 0.85rem; }
    .cat-malicious  { color: #f85149; font-weight: 600; }
    .cat-suspicious { color: #d29922; font-weight: 600; }
    .cat-harmless   { color: #3fb950; }
    .cat-undetected { color: #8b949e; }

    /* Section headers */
    h3 { color: #c9d1d9; }
    .section-divider { border-top: 1px solid #21262d; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://www.virustotal.com/gui/images/favicon.png", width=30)
    st.markdown("### ⚙️ Settings")
    api_url = st.text_input("Backend API URL", value="http://localhost:8000/api/v1")
    st.info("Make sure the backend server is running.")
    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown("- 🔬 VirusTotal (90+ engines)\n- 🔍 WHOIS / Domain Age\n- 🛡️ Google Safe Browsing\n- 🌐 URLScan.io\n- 🚫 AbuseIPDB")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🛡️ URL Threat Intelligence Platform")
st.markdown("Analyze any URL across **90+ security engines** powered by VirusTotal.")
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    url_to_scan = st.text_input("URL to scan", placeholder="Enter a URL — e.g. https://google.com", label_visibility="collapsed")
with col_btn:
    scan_clicked = st.button("🔍 Scan", use_container_width=True)

# ── Scan & Display ────────────────────────────────────────────────────────────
if scan_clicked:
    if not url_to_scan.strip():
        st.error("Please enter a URL.")
    else:
        with st.spinner("Scanning across all intelligence sources…"):
            try:
                response = requests.post(f"{api_url}/scan-url", params={"url": url_to_scan.strip()}, timeout=30)
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"❌ Failed to reach backend: {e}")
                st.stop()

        data = result.get("data", {})
        vt   = data.get("virustotal", {})
        urlscan = data.get("urlscan", {})
        abuseipdb = data.get("abuseipdb", {})

        # ── Top-line summary ──────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Scan Summary")

        verdict = result.get("verdict", "UNKNOWN")
        badge_class = f"badge-{verdict.lower()}"
        verdict_icon = {"ALLOW": "✅", "REVIEW": "⚠️", "BLOCK": "🚫"}.get(verdict, "❓")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Risk Score", f"{result.get('score', 0)} / 100")
        c2.metric("🔴 Malicious",  vt.get("malicious", 0))
        c3.metric("🟡 Suspicious", vt.get("suspicious", 0))
        c4.metric("🟢 Harmless",   vt.get("harmless", 0))
        c5.metric("⚪ Undetected", vt.get("undetected", 0))

        st.markdown(
            f"**Verdict:** <span class='badge {badge_class}'>{verdict_icon} {verdict}</span>",
            unsafe_allow_html=True,
        )

        # ── URL Metadata ──────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🌐 URL Metadata")

        m1, m2, m3 = st.columns(3)
        m1.metric("Domain Age (days)", data.get("domain_age", "Unknown"))
        m2.metric("HTTP Response Code", vt.get("last_http_response_code") or "N/A")
        m3.metric("Times Submitted to VT", vt.get("times_submitted", 0))

        meta_rows = {
            "Final URL":         vt.get("final_url") or result.get("url"),
            "Page Title":        vt.get("title") or "—",
            "Tags":              ", ".join(vt.get("tags", [])) or "None",
            "Google Phishing":   "⚠️ YES" if data.get("phishing") else "✅ No",
            "VT Reputation":     vt.get("reputation", "N/A"),
            "Scan Timestamp":    result.get("timestamp", "—"),
        }
        for label, value in meta_rows.items():
            st.markdown(f"**{label}:** `{value}`")

        # Redirection chain
        chain = vt.get("redirection_chain", [])
        if chain:
            with st.expander(f"🔀 Redirection Chain ({len(chain)} hop(s))"):
                for i, hop in enumerate(chain, 1):
                    st.markdown(f"`{i}.` {hop}")

        # ── External Intelligences ────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🔍 Additional Threat Intelligence")
        
        tab1, tab2 = st.tabs(["🌐 URLScan.io", "🚫 AbuseIPDB"])
        
        with tab1:
            if "error" in urlscan:
                st.warning(urlscan["error"])
            else:
                u1, u2, u3 = st.columns(3)
                u1.metric("Malicious Status", "🚨 YES" if urlscan.get("malicious") else "✅ NO")
                u2.metric("URLScan Score", urlscan.get("score", 0))
                u3.metric("Total Scans", urlscan.get("total_scans", 0))
                st.markdown(f"**Country:** {urlscan.get('country')} | **Server:** {urlscan.get('server')}")
                if urlscan.get("report_url") and urlscan.get("report_url") != "No recent scans":
                    st.markdown(f"🔗 [View Full URLScan Report]({urlscan.get('report_url')})")
                    
        with tab2:
            if "error" in abuseipdb:
                st.warning(abuseipdb["error"])
            else:
                a1, a2, a3 = st.columns(3)
                a1.metric("Abuse Confidence", f"{abuseipdb.get('abuseConfidenceScore', 0)}%")
                a2.metric("Total Reports", abuseipdb.get('totalReports', 0))
                a3.metric("Usage Type", abuseipdb.get('usageType', 'Unknown'))
                st.markdown(f"**Resolved IP:** `{abuseipdb.get('ip', 'Unknown')}` | **ISP:** {abuseipdb.get('isp', 'Unknown')} | **Country Code:** {abuseipdb.get('countryCode', 'Unknown')}")

        # ── Categories ────────────────────────────────────────────────────────
        categories = vt.get("categories", {})
        if categories:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 🏷️ Site Categories (by vendor)")
            cat_df = pd.DataFrame(
                [{"Vendor": k, "Category": v} for k, v in categories.items()]
            )
            st.dataframe(cat_df, use_container_width=True, hide_index=True)

        # ── Engine Results Table ──────────────────────────────────────────────
        analysis_results = vt.get("last_analysis_results", {})
        if analysis_results:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown(f"### 🔬 Engine Analysis Results ({len(analysis_results)} engines)")

            # Filter controls
            filter_col1, filter_col2 = st.columns([3, 1])
            with filter_col1:
                search_engine = st.text_input("🔎 Search engine name", placeholder="e.g. Kaspersky", key="eng_search")
            with filter_col2:
                show_only = st.selectbox("Filter by category", ["All", "malicious", "suspicious", "harmless", "undetected"], key="cat_filter")

            rows = []
            for engine, detail in analysis_results.items():
                rows.append({
                    "Engine":   engine,
                    "Category": detail.get("category", ""),
                    "Result":   detail.get("result", ""),
                    "Method":   detail.get("method", ""),
                })

            df = pd.DataFrame(rows).sort_values(
                by="Category",
                key=lambda s: s.map({"malicious": 0, "suspicious": 1, "harmless": 2, "undetected": 3}).fillna(4)
            )

            # Apply filters
            if show_only != "All":
                df = df[df["Category"] == show_only]
            if search_engine:
                df = df[df["Engine"].str.contains(search_engine, case=False)]

            # Color-map the Category column
            def color_category(val):
                colors = {
                    "malicious":  "color: #f85149; font-weight: 600",
                    "suspicious": "color: #d29922; font-weight: 600",
                    "harmless":   "color: #3fb950",
                    "undetected": "color: #8b949e",
                }
                return colors.get(val, "")

            styled = df.style.applymap(color_category, subset=["Category"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # Flagging engines summary
            flagged = df[df["Category"].isin(["malicious", "suspicious"])]
            if not flagged.empty:
                with st.expander(f"🚨 Flagging Engines ({len(flagged)})"):
                    for _, row in flagged.iterrows():
                        icon = "🔴" if row["Category"] == "malicious" else "🟡"
                        st.markdown(f"{icon} **{row['Engine']}** — `{row['Result']}`")
            else:
                st.success("✅ No engines flagged this URL as malicious or suspicious.")

        # ── Raw JSON ──────────────────────────────────────────────────────────
        with st.expander("📄 View Full Raw JSON"):
            st.json(result)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#484f58;font-size:0.8rem;'>URL Threat Intelligence Platform · Powered by VirusTotal API</div>",
    unsafe_allow_html=True,
)
