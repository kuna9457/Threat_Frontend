import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="URL Threat Intelligence Platform", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    .main .block-container { padding-top: 2rem; }
    div[data-testid="metric-container"] {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 10px; padding: 14px 20px;
    }
    .badge { display: inline-block; padding: 6px 18px; border-radius: 20px;
             font-weight: 700; font-size: 1.1rem; letter-spacing: 1px; }
    .badge-allow  { background: #0d3d1c; color: #3fb950; border: 1px solid #3fb950; }
    .badge-review { background: #3d2d00; color: #d29922; border: 1px solid #d29922; }
    .badge-block  { background: #3d0000; color: #f85149; border: 1px solid #f85149; }
    .cat-malicious  { color: #f85149; font-weight: 600; }
    .cat-suspicious { color: #d29922; font-weight: 600; }
    .cat-harmless   { color: #3fb950; }
    .cat-undetected { color: #8b949e; }
    h3 { color: #c9d1d9; }
    .section-divider { border-top: 1px solid #21262d; margin: 1.5rem 0; }
    .grade-badge { display: inline-block; padding: 8px 20px; border-radius: 12px;
                   font-weight: 800; font-size: 1.8rem; letter-spacing: 2px; }
    .grade-a { background: #0d3d1c; color: #3fb950; border: 2px solid #3fb950; }
    .grade-b { background: #1a3d2c; color: #3fb990; border: 2px solid #3fb990; }
    .grade-c { background: #3d2d00; color: #d29922; border: 2px solid #d29922; }
    .grade-d { background: #3d1a00; color: #e08f30; border: 2px solid #e08f30; }
    .grade-f { background: #3d0000; color: #f85149; border: 2px solid #f85149; }
    .security-pass { color: #3fb950; } .security-fail { color: #f85149; }
    .security-warn { color: #d29922; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.virustotal.com/gui/images/favicon.png", width=30)
    st.markdown("### ⚙️ Settings")
    default_api = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")
    api_url = st.text_input("Backend API URL", value=default_api)
    st.info("Make sure the backend server is running.")
    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown("- 🔬 VirusTotal (90+ engines)\n- 🔍 WHOIS / Domain Age\n- 🛡️ Google Safe Browsing\n- 🌐 URLScan.io\n- 🚫 AbuseIPDB\n- 🔒 SSL Labs (Qualys)\n- 📧 MX / DNS Analysis")

# Header
st.markdown("## 🛡️ URL Threat Intelligence Platform")
st.markdown("Analyze URLs across **90+ security engines**, **SSL/TLS grading**, and **mail-server analysis**.")
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Multi-URL Input
st.markdown("### 📝 Enter URLs to Scan")
st.markdown("*Enter one URL per line for batch scanning*")
urls_text = st.text_area("URLs", placeholder="https://google.com\nhttps://example.com\nhttps://github.com",
                         label_visibility="collapsed", height=120)

col_btn1, col_btn2, col_spacer = st.columns([1, 1, 4])
with col_btn1:
    scan_clicked = st.button("🔍 Scan All URLs", use_container_width=True)
with col_btn2:
    download_pdf = st.button("📄 Download PDF", use_container_width=True)


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
            pdf = pd.DataFrame(protos)
            st.dataframe(pdf, use_container_width=True, hide_index=True)

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
            st.dataframe(pd.DataFrame(vuln_rows), use_container_width=True, hide_index=True)

    ciphers = ssl.get("cipher_suites", [])
    if ciphers:
        with st.expander(f"🔑 Cipher Suites ({ssl.get('total_cipher_suites', len(ciphers))})"):
            st.dataframe(pd.DataFrame(ciphers), use_container_width=True, hide_index=True)


def _render_mx_section(mx):
    if not mx or "error" in mx:
        st.warning(mx.get("error", "MX data not available") if mx else "No MX data")
        return

    ms = mx.get("mail_security", {})
    mscore = ms.get("score", 0)
    color = "#3fb950" if mscore >= 75 else ("#d29922" if mscore >= 50 else "#f85149")
    st.markdown(f"**Mail Security Score:** <span style='color:{color};font-size:1.4rem;font-weight:700'>{mscore}/100</span>", unsafe_allow_html=True)

    checks = ms.get("checks", {})
    for name, info in checks.items():
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(info.get("status"), "❓")
        st.markdown(f"{icon} **{name.upper()}**: {info.get('detail', '')}")

    mx_recs = mx.get("mx_records", [])
    if mx_recs:
        with st.expander(f"📧 MX Records ({len(mx_recs)})"):
            st.dataframe(pd.DataFrame(mx_recs), use_container_width=True, hide_index=True)
            mx_ips = mx.get("mx_host_ips", {})
            if mx_ips:
                st.markdown("**MX Host IPs:**")
                for host, ips in mx_ips.items():
                    st.markdown(f"- `{host}` → {', '.join(ips)}")

    spf = mx.get("spf", {})
    dmarc = mx.get("dmarc", {})
    dkim = mx.get("dkim", {})
    with st.expander("🔐 Email Authentication Records"):
        st.markdown(f"**SPF:** `{spf.get('record', 'Not found')}`")
        st.markdown(f"**DMARC:** `{dmarc.get('record', 'Not found')}`")
        if dmarc.get("policy"):
            pol = dmarc["policy"]
            st.markdown(f"  - Policy: `{pol.get('policy')}` | Subdomain: `{pol.get('subdomain_policy', 'inherit')}` | PCT: `{pol.get('pct', 100)}%`")
        if dkim.get("exists"):
            st.markdown(f"**DKIM Selectors:** {', '.join(dkim.get('selectors_found', []))}")
        else:
            st.markdown("**DKIM:** No common selectors found")

    with st.expander("🌐 DNS Records"):
        for label, key in [("A Records", "a_records"), ("AAAA Records", "aaaa_records"),
                           ("NS Records", "ns_records"), ("CNAME", "cname_records")]:
            recs = mx.get(key, [])
            if recs: st.markdown(f"**{label}:** {', '.join(recs)}")
        soa = mx.get("soa", {})
        if soa:
            st.markdown(f"**SOA:** Primary NS: `{soa.get('mname','')}` | Email: `{soa.get('rname','')}` | Serial: `{soa.get('serial','')}`")
        txt = mx.get("txt_records", [])
        if txt:
            st.markdown("**TXT Records:**")
            for t in txt: st.markdown(f"- `{t}`")
        rdns = mx.get("reverse_dns", {})
        if rdns:
            st.markdown("**Reverse DNS:**")
            for ip, ptr in rdns.items(): st.markdown(f"- `{ip}` → `{ptr}`")

    banners = mx.get("smtp_banners", {})
    if banners:
        with st.expander("📡 SMTP Banners"):
            for host, banner in banners.items():
                st.markdown(f"**{host}:** `{banner}`")


def _render_result(result, idx=None):
    data = result.get("data", {})
    vt = data.get("virustotal", {})
    urlscan_data = data.get("urlscan", {})
    abuseipdb_data = data.get("abuseipdb", {})
    ssl = data.get("ssl_labs", {})
    mx = data.get("mx_tools", {})

    header = f"### {'#' + str(idx) + ' — ' if idx else ''}{result.get('url', '')}"
    st.markdown(header)

    verdict = result.get("verdict", "UNKNOWN")
    badge_class = f"badge-{verdict.lower()}"
    verdict_icon = {"ALLOW": "✅", "REVIEW": "⚠️", "BLOCK": "🚫"}.get(verdict, "❓")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Risk Score", f"{result.get('score', 0)} / 100")
    c2.metric("🔴 Malicious", vt.get("malicious", 0))
    c3.metric("🟡 Suspicious", vt.get("suspicious", 0))
    c4.metric("🟢 Harmless", vt.get("harmless", 0))
    c5.metric("⚪ Undetected", vt.get("undetected", 0))

    st.markdown(f"**Verdict:** <span class='badge {badge_class}'>{verdict_icon} {verdict}</span>", unsafe_allow_html=True)

    # Tabs for all data sources
    tabs = st.tabs(["🔬 VirusTotal", "🔒 SSL Labs", "📧 MX Tools", "🌐 URLScan", "🚫 AbuseIPDB", "📄 Raw JSON"])

    with tabs[0]:
        st.markdown("### 🌐 URL Metadata")
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
            st.markdown("#### 🏷️ Categories")
            st.dataframe(pd.DataFrame([{"Vendor": k, "Category": v} for k, v in categories.items()]),
                         use_container_width=True, hide_index=True)
        analysis_results = vt.get("last_analysis_results", {})
        if analysis_results:
            st.markdown(f"#### 🔬 Engine Results ({len(analysis_results)})")
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
                return {"malicious":"color:#f85149;font-weight:600","suspicious":"color:#d29922;font-weight:600",
                        "harmless":"color:#3fb950","undetected":"color:#8b949e"}.get(val,"")
            st.dataframe(df.style.applymap(cc, subset=["Category"]), use_container_width=True, hide_index=True)
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
        _render_mx_section(mx)

    with tabs[3]:
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

    with tabs[4]:
        if "error" in abuseipdb_data:
            st.warning(abuseipdb_data["error"])
        else:
            a1, a2, a3 = st.columns(3)
            a1.metric("Abuse Confidence", f"{abuseipdb_data.get('abuseConfidenceScore',0)}%")
            a2.metric("Total Reports", abuseipdb_data.get("totalReports", 0))
            a3.metric("Usage Type", abuseipdb_data.get("usageType", "Unknown"))
            st.markdown(f"**IP:** `{abuseipdb_data.get('ip','')}` | **ISP:** {abuseipdb_data.get('isp','')} | **Country:** {abuseipdb_data.get('countryCode','')}")

    with tabs[5]:
        st.json(result)


# Handle Scan
if scan_clicked:
    urls = [u.strip() for u in urls_text.strip().split("\n") if u.strip()]
    if not urls:
        st.error("Please enter at least one URL.")
    else:
        with st.spinner(f"Scanning {len(urls)} URL(s) across all intelligence sources…"):
            try:
                resp = requests.post(f"{api_url}/scan-batch", json={"urls": urls}, timeout=300)
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

# Handle PDF Download
if download_pdf:
    urls = [u.strip() for u in urls_text.strip().split("\n") if u.strip()]
    if not urls:
        st.error("Please enter at least one URL to generate a report.")
    else:
        with st.spinner("Generating PDF report…"):
            try:
                resp = requests.post(f"{api_url}/report/pdf", json={"urls": urls}, timeout=300)
                resp.raise_for_status()
                pdf_data = resp.content
            except Exception as e:
                st.error(f"❌ Failed to generate PDF: {e}")
                st.stop()
        st.download_button(
            label="⬇️ Download Report (PDF)",
            data=pdf_data,
            file_name=f"threat_intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# Footer
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#484f58;font-size:0.8rem;'>URL Threat Intelligence Platform · Powered by VirusTotal, SSL Labs, MX Tools & more</div>", unsafe_allow_html=True)
