import streamlit as st
import time
import json
from orchestrator import run_code_sentry_pipeline

# Predefined Sample Diffs for Multiple Languages
SAMPLE_DIFFS = {
    "Python (SQL Injection & Weak Auth)": """diff --git a/services/user_service.py b/services/user_service.py
index a1b2c3d..e4f5g6h 100644
--- a/services/user_service.py
+++ b/services/user_service.py
@@ -10,8 +10,8 @@ def authenticate_user(db_cursor, username, password):
-    secret = os.getenv("JWT_SECRET")
+    import hashlib
+    # Vulnerable to SQL Injection & Weak MD5 Password Hashing
+    hashed_pwd = hashlib.md5(password.encode()).hexdigest()
+    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_pwd}'"
+    db_cursor.execute(query)
+    return db_cursor.fetchone()""",

    "JavaScript / Node.js (Breaking API Change)": """diff --git a/api/payment.js b/api/payment.js
index 789abcd..012efgh 100644
--- a/api/payment.js
+++ b/api/payment.js
@@ -5,7 +5,8 @@
- export function processPayment(userId, amount, currency = "USD") {
+ // Breaking Change: Renamed userId and removed default currency parameter
+ export function processPayment(customerId, amountInCents) {
    if (!amountInCents || amountInCents <= 0) {
        throw new Error("Invalid amount");
    }
-   return stripe.charges.create({ amount, currency, customer: userId });
+   return stripe.paymentIntents.create({ amount: amountInCents, customer: customerId });
 }""",

    "Rust (Unsafe Memory & Pointer Dereference)": """diff --git a/src/buffer.rs b/src/buffer.rs
index 3b4c5d6..6e7f8g9 100644
--- a/src/buffer.rs
+++ b/src/buffer.rs
@@ -12,6,7 +12,8 @@ pub fn read_raw_buffer(ptr: *const u8, len: usize) -> Vec<u8> {
-    let slice = unsafe { std::slice::from_raw_parts(ptr, len) };
-    slice.to_vec()
+    // Potential null pointer dereference in unsafe block
+    unsafe {
+        let slice = std::slice::from_raw_parts(ptr, len);
+        slice.to_vec()
+    }
 }""",

    "Go (Hardcoded Secrets & Unchecked Errors)": """diff --git a/config/db.go b/config/db.go
index 1122334..5566778 100644
--- a/config/db.go
+++ b/config/db.go
@@ -8,6,7 +8,7 @@ func ConnectDB() (*sql.DB, error) {
-    dbURI := os.Getenv("DATABASE_URL")
+    // Security Issue: Hardcoded DB credentials
+    dbURI := "postgres://admin:Password123!@localhost:5432/production_db?sslmode=disable"
     db, err := sql.Open("postgres", dbURI)
+    // Missing error check on connection attempt
     return db, err
 }"""
}

# Page Configuration
st.set_page_config(
    page_title="CodeSentry — AI PR Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Dark Mode & Gold Accent Styling
st.markdown("""
    <style>
    /* Background & Typography */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header Container & Modern Gradient Header Title */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 4px;
    }
    .header-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 20%, #FFD700 70%, #D4AF37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 28px;
    }

    /* Minimalist Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #131722;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetric"] label {
        color: #64748B !important;
        font-size: 0.85rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700;
        font-size: 1.8rem !important;
    }

    /* Modern Solid Gold Accent Button */
    div.stButton > button {
        background: #D4AF37 !important;
        color: #0B0E14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15) !important;
    }
    div.stButton > button:hover {
        background: #FFD700 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3) !important;
    }

    /* Text Input & Dropdown Formatting */
    .stTextArea textarea, div[data-baseweb="select"] {
        background-color: #131722 !important;
        color: #E2E8F0 !important;
        border-radius: 8px !important;
        font-family: 'Fira Code', 'Courier New', monospace !important;
    }
    .stTextArea textarea {
        border: 1px solid #1E293B !important;
        font-size: 0.9rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #D4AF37 !important;
    }

    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0E121B;
        border-right: 1px solid #1E293B;
    }

    /* Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #1E293B;
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        padding: 10px 20px;
        font-weight: 500;
        border-radius: 6px;
    }
    .stTabs [aria-selected="true"] {
        color: #D4AF37 !important;
        background-color: #131722 !important;
        border-bottom: 2px solid #D4AF37 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Design with SVG Gold Shield Logo & Status Badges
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2Z" fill="#131722" stroke="#D4AF37" stroke-width="2"/>
                <path d="M12 6L16 11H8L12 6Z" fill="#D4AF37"/>
                <path d="M12 18V12" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            <div>
                <div style="font-weight: 800; font-size: 1.35rem; color: #FFFFFF; letter-spacing: -0.5px;">CodeSentry</div>
                <div style="font-size: 0.8rem; color: #D4AF37; font-weight: 500;">AI PR Guardian v1.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<div style='font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>Active Agents</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 12px; font-size: 0.9rem;'>", unsafe_allow_html=True)
    st.markdown("🟢 **Security Agent** `<llama-3.1>`")
    st.markdown("🟢 **Test Generator** `<llama-3.1>`")
    st.markdown("🟢 **Breaking Changes** `<llama-3.1>`")
    st.markdown("🟢 **Changelog Agent** `<llama-3.1>`")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.caption("⚡ Powered by Groq Orchestrator")

# Header Section with Matching Gold Shield Logo
st.markdown("""
    <div class="header-container">
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2Z" fill="#131722" stroke="#D4AF37" stroke-width="2"/>
            <path d="M12 6L16 11H8L12 6Z" fill="#D4AF37"/>
            <path d="M12 18V12" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <div class="header-title">CodeSentry — PR Guardian</div>
    </div>
""", unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Automated Multi-Agent Pull Request Security, Vulnerability & Code Quality Audit</div>', unsafe_allow_html=True)

# Main Controls Layout
col_left, col_right = st.columns([3.2, 1])

with col_left:
    # Multi-Language Diff Selector & Input Mode
    use_sample = st.checkbox("Use Preset Sample PR Diff", value=True)
    
    if use_sample:
        selected_lang = st.selectbox(
            "Select Programming Language Sample:",
            list(SAMPLE_DIFFS.keys())
        )
        pr_diff = st.text_area("Pull Request Diff Input:", value=SAMPLE_DIFFS[selected_lang], height=210)
    else:
        pr_diff = st.text_area("Pull Request Diff Input:", placeholder="Paste custom git diff here...", height=210)

with col_right:
    st.markdown("### Actions")
    st.markdown("<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 14px;'>Trigger parallel agent pipeline for instant audit.</div>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Audit PR Now", use_container_width=True)

st.divider()

# Audit Results Render
if analyze_btn:
    if not pr_diff.strip():
        st.error("Please provide a valid PR diff before auditing.")
    else:
        with st.spinner("Analyzing PR across multi-agent system..."):
            results = run_code_sentry_pipeline(pr_diff)

        # Header Row for Results + Download Report Action
        res_col1, res_col2 = st.columns([3, 1])
        with res_col1:
            st.success(f"Audit completed successfully in **{results.get('execution_time', 0)} seconds**.")
        with res_col2:
            # Download JSON Report Button
            report_json = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Export Report (JSON)",
                data=report_json,
                file_name="codesentry_audit_report.json",
                mime="application/json",
                use_container_width=True
            )

        # Overview Metrics
        security_data = results.get("security_analysis", {})
        score = security_data.get("score", 100)
        issues_count = len(security_data.get("issues", []))
        tests_count = len(results.get("missing_tests", []))
        breaking_count = len(results.get("breaking_changes", []))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Security Rating", f"{score}/100")
        c2.metric("Vulnerabilities", issues_count)
        c3.metric("Drafted Tests", tests_count)
        c4.metric("Breaking Changes", breaking_count)

        st.markdown("<br>", unsafe_allow_html=True)

        # Output Tabs
        t1, t2, t3, t4 = st.tabs([
            "🔒 Security Audit", 
            "🧪 Unit Tests", 
            "⚠️ Breaking Changes", 
            "📝 Changelog Draft"
        ])

        with t1:
            st.markdown("##### Security Findings")
            issues = security_data.get("issues", [])
            if issues:
                for idx, issue in enumerate(issues, 1):
                    st.warning(f"**Issue #{idx} [{issue.get('severity', 'HIGH')}]:** {issue.get('issue')}\n\n*Location:* `{issue.get('file', 'N/A')}` — Line {issue.get('line', 'N/A')}")
            else:
                st.info("No security vulnerabilities detected.")

        with t2:
            st.markdown("##### Generated Test Cases")
            tests = results.get("missing_tests", [])
            if tests:
                for test in tests:
                    st.code(test, language="python")
            else:
                st.info("No test cases generated.")

        with t3:
            st.markdown("##### Compatibility & Breaking Changes")
            breaking = results.get("breaking_changes", [])
            if breaking:
                for change in breaking:
                    st.error(f"• {change}")
            else:
                st.info("No breaking changes detected.")

        with t4:
            st.markdown("##### Release Changelog")
            changelog_text = results.get("draft_changelog", "No changelog available.")
            st.markdown(changelog_text)