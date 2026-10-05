import html
import os
import os
from datetime import datetime

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="CodeExplainer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

for key, default in {
    "page": "Home",
    "repo_url": "",
    "analysis": None,
}.items():
    st.session_state.setdefault(key, default)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #050607;
    --panel: rgba(15, 15, 17, .72);
    --red: #ff3038;
    --red-2: #ff6269;
    --text: #f6f6f8;
    --muted: #a7a7ae;
    --green: #34e39b;
}

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    color: var(--text);
    background:
      radial-gradient(circle at 78% 14%, rgba(255, 36, 45, .14), transparent 23%),
      radial-gradient(circle at 15% 80%, rgba(255, 36, 45, .07), transparent 23%),
      #050607;
    overflow-x: hidden;
}

.stApp::before,
.stApp::after {
    content: "";
    position: fixed;
    inset: -10%;
    pointer-events: none;
    background-image:
      radial-gradient(circle, rgba(255,255,255,.82) 0 1px, transparent 1.3px),
      radial-gradient(circle, rgba(255,65,72,.72) 0 1px, transparent 1.4px);
    background-size: 190px 190px, 285px 285px;
    background-position: 12px 15px, 70px 100px;
    opacity: .42;
    mix-blend-mode: screen;
    animation: starDrift 32s linear infinite;
}

.stApp::after {
    opacity: .18;
    transform: scale(1.08);
    animation-duration: 46s;
    animation-direction: reverse;
}

@keyframes starDrift {
    from { transform: translate3d(0, 0, 0) scale(1); }
    to   { transform: translate3d(-70px, 45px, 0) scale(1.02); }
}

@keyframes reveal {
    from {
        opacity: 0;
        transform: translateY(18px) scale(.985);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 12px rgba(255,48,56,.12); }
    50% { box-shadow: 0 0 25px rgba(255,48,56,.25); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8,8,10,.96), rgba(4,5,6,.99));
    border-right: 1px solid rgba(255,255,255,.08);
}

.sidebar-brand {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 6px 4px 20px;
    font-size: 18px;
    font-weight: 800;
}

.brand-icon {
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: linear-gradient(145deg, #7f0b10, #ff333b);
    box-shadow: 0 0 22px rgba(255,48,56,.36);
}

.status-pill {
    position: fixed;
    top: 14px;
    right: 24px;
    z-index: 999;
    padding: 7px 12px;
    border-radius: 999px;
    color: #e9e9ee;
    background: rgba(14,14,17,.7);
    border: 1px solid rgba(255,255,255,.1);
    backdrop-filter: blur(16px);
}

.status-dot {
    color: var(--green);
    margin-left: 8px;
}

.nav-note {
    margin-top: 20px;
    padding: 14px;
    border-radius: 13px;
    border: 1px solid rgba(255,255,255,.09);
    background: rgba(255,255,255,.03);
}

.nav-note .mini {
    margin-bottom: 9px;
    color: var(--muted);
    font-size: 10px;
}

.nav-note .line {
    margin: 5px 0;
    font-size: 12px;
}

.glass-card, .hero-card, .feature-card, .metric-card {
    animation: reveal .65s ease both;
    border: 1px solid rgba(255, 65, 72, .23);
    background:
      linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.014)),
      rgba(12,12,15,.68);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow:
      0 24px 60px rgba(0,0,0,.37),
      inset 0 1px rgba(255,255,255,.045),
      0 0 34px rgba(255,35,44,.045);
    border-radius: 18px;
}

.glass-card:hover, .feature-card:hover, .metric-card:hover {
    transform: translateY(-3px) perspective(800px) rotateX(1deg);
    border-color: rgba(255,80,86,.42);
    box-shadow:
      0 30px 70px rgba(0,0,0,.4),
      0 0 28px rgba(255,40,48,.11),
      inset 0 1px rgba(255,255,255,.06);
    transition: .22s ease;
}

.hero-card {
    min-height: 395px;
    padding: 42px;
    overflow: hidden;
    position: relative;
    transform-style: preserve-3d;
}

.hero-card::after {
    content: "";
    position: absolute;
    width: 360px;
    height: 360px;
    right: -105px;
    bottom: -130px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,41,50,.25), transparent 68%);
    animation: pulseGlow 4s ease-in-out infinite;
}

.eyebrow {
    display: inline-flex;
    padding: 7px 11px;
    border-radius: 999px;
    border: 1px solid rgba(255,74,80,.25);
    background: rgba(255,40,45,.05);
    color: #d7d7dc;
    font-size: 11px;
}

.hero-title {
    margin: 20px 0 8px;
    font-size: 45px;
    line-height: 1.03;
    font-weight: 800;
    letter-spacing: -1.7px;
}

.hero-title span {
    color: var(--red);
    text-shadow: 0 0 24px rgba(255,48,56,.17);
}

.hero-subtitle {
    max-width: 590px;
    color: #c1c1c7;
    font-size: 15px;
    line-height: 1.65;
}

.github-orb {
    width: 168px;
    height: 168px;
    margin: 95px auto 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 38px;
    background: linear-gradient(145deg, rgba(255,56,64,.22), rgba(255,255,255,.025));
    border: 1px solid rgba(255,95,102,.56);
    box-shadow:
      0 0 55px rgba(255,45,54,.23),
      inset 0 1px rgba(255,255,255,.12);
    font-size: 70px;
    animation: floatOrb 5s ease-in-out infinite;
    transform-style: preserve-3d;
}

@keyframes floatOrb {
    0%,100% { transform: translateY(0) rotateX(0deg) rotateY(0deg); }
    50% { transform: translateY(-8px) rotateX(2deg) rotateY(-3deg); }
}

.feature-card {
    min-height: 140px;
    padding: 18px;
    border-color: rgba(255,255,255,.085);
}

.feature-icon {
    width: 38px;
    height: 38px;
    margin-bottom: 11px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,45,53,.1);
    border: 1px solid rgba(255,60,68,.25);
    font-size: 18px;
}

.feature-title {
    margin-bottom: 4px;
    font-size: 14px;
    font-weight: 700;
}

.feature-text {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.45;
}

.page-title {
    margin: 8px 0 5px;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -.8px;
}

.page-subtitle {
    margin-bottom: 22px;
    color: var(--muted);
    font-size: 13px;
}

.section-title {
    margin: 8px 0 14px;
    font-size: 18px;
    font-weight: 700;
}

.metric-card {
    min-height: 120px;
    padding: 18px;
    border-color: rgba(255,255,255,.08);
}

.metric-value {
    margin-top: 7px;
    font-size: 24px;
    font-weight: 800;
}

.metric-label {
    margin-top: 3px;
    color: var(--muted);
    font-size: 11px;
}

.info-row {
    display: grid;
    grid-template-columns: 145px 1fr;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,.055);
    font-size: 12px;
}

.info-label {
    color: var(--muted);
}

.info-value {
    overflow-wrap: anywhere;
}

.step {
    padding: 10px 2px;
    text-align: center;
}

.step-icon {
    width: 46px;
    height: 46px;
    margin: 0 auto 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,40,48,.08);
    border: 1px solid rgba(255,70,78,.35);
    box-shadow: 0 0 17px rgba(255,40,48,.11);
}

.step-title {
    font-size: 12px;
    font-weight: 700;
}

.step-text {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.4;
}

.explanation-box {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(255,60,68,.27);
    background: linear-gradient(135deg, rgba(255,40,48,.05), rgba(255,255,255,.02));
    box-shadow: inset 4px 0 #ff353d, inset 0 1px rgba(255,255,255,.035);
    animation: reveal .7s ease both;
}

.badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    background: rgba(50,229,155,.08);
    border: 1px solid rgba(50,229,155,.2);
    color: #55edb1;
    font-size: 10px;
}

.small-muted {
    color: var(--muted);
    font-size: 11px;
}

.footer-line {
    margin-top: 34px;
    padding-top: 13px;
    border-top: 1px solid rgba(255,255,255,.07);
    color: #84848b;
    font-size: 11px;
}

.smooth-loader {
    padding: 26px;
    text-align: center;
    border-radius: 16px;
    border: 1px solid rgba(255,55,63,.24);
    background: rgba(255,255,255,.028);
    animation: reveal .35s ease both;
}

.loader-ring {
    width: 44px;
    height: 44px;
    margin: 0 auto 12px;
    border-radius: 50%;
    border: 3px solid rgba(255,255,255,.09);
    border-top-color: #ff3a43;
    border-right-color: #ff6067;
    animation: spin .85s linear infinite;
}

div.stButton > button, div.stDownloadButton > button {
    border-radius: 11px !important;
    border: 1px solid rgba(255,72,78,.36) !important;
    background: linear-gradient(180deg, #ff4d54, #e9222b) !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 27px rgba(255,38,46,.17) !important;
    transition: transform .18s ease, box-shadow .18s ease !important;
}

div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    border-color: rgba(255,130,135,.82) !important;
    box-shadow: 0 12px 34px rgba(255,38,46,.28) !important;
}

div.stButton > button:active, div.stDownloadButton > button:active {
    transform: translateY(1px) scale(.99) !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.045) !important;
    border-color: rgba(255,255,255,.1) !important;
}

input, textarea {
    color: #fff !important;
}

.stCodeBlock {
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 13px;
}

@media (max-width: 900px) {
    .hero-title { font-size: 34px; }
    .hero-card { min-height: auto; }
    .status-pill { right: 10px; top: 8px; }
}
</style>
""",
    unsafe_allow_html=True,
)


def status():
    if os.getenv("STREAMLIT_CLOUD"):
        st.markdown(
            '<div class="status-pill">◌ Local AI · SmolLM2 135M'
            '<span class="status-dot">● Ready</span></div>',
            unsafe_allow_html=True,
        )
        return

    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=4,
        )
        data = response.json()
        model = data.get("model", "qwen2.5:3b")
        provider = data.get("provider", "ollama")
        online = data.get("status") == "ok"
    except requests.RequestException:
        model = "qwen2.5:3b"
        provider = "ollama"
        online = False

    label = "Online" if online else "Offline"

    st.markdown(
        f'<div class="status-pill">◌ {html.escape(str(provider))} · '
        f'{html.escape(str(model))}'
        f'<span class="status-dot">● {label}</span></div>',
        unsafe_allow_html=True,
    )


def sidebar():
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="brand-icon">◈</div>
          Code<span style="color:#ff4148;">Explainer</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    items = [
        ("Home", "⌂"),
        ("Explain Repository", "↗"),
        ("Repository Info", "▣"),
        ("Code Structure", "⌗"),
        ("File Viewer", "▤"),
        ("AI Explanation", "◉"),
        ("Summary", "◈"),
    ]

    for name, icon in items:
        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}",
            use_container_width=True,
        ):
            st.session_state.page = name
            st.rerun()

    st.markdown(
        """
        <div class="nav-note">
          <div class="mini">LOCAL AI MODEL</div>
          <div class="line">🟢 Ollama</div>
          <div class="line">🟢 Qwen 2.5 3B</div>
          <div class="line">🟢 Local inference</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(inner: str):
    safe_html = inner.replace("\n", "")
    st.markdown(
        '<div class="glass-card" style="padding:20px;">'
        + safe_html
        + "</div>",
        unsafe_allow_html=True,
    )


def format_number(value):
    try:
        return f"{int(value or 0):,}"
    except (ValueError, TypeError):
        return "0"


def format_date(value):
    if not value:
        return "N/A"

    try:
        dt = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(value)


def require_analysis():
    if st.session_state.analysis:
        return True

    st.info(
        "Analyze a repository first from **Explain Repository**."
    )

    if st.button(
        "Go to Explain Repository",
        type="primary",
    ):
        st.session_state.page = "Explain Repository"
        st.rerun()

    return False


def run_analysis():
    # Start the cloud-local FastAPI backend only after the user requests
    # repository analysis. This prevents the Streamlit health check from
    # racing with heavyweight ML imports/model loading.
    cloud_starter = globals().get("start_backend")

    if cloud_starter is not None and os.getenv("STREAMLIT_CLOUD"):
        try:
            cloud_starter()
        except Exception as exc:
            st.error(
                "Could not start the internal FastAPI service. "
                f"{exc}"
            )
            return

    holder = st.empty()

    holder.markdown(
        '<div class="smooth-loader"><div class="loader-ring"></div>'
        '<div style="font-weight:700">Analyzing Repository...</div>'
        '<div class="small-muted" style="margin-top:6px">'
        'Downloading → Processing → Generating explanation'
        '</div></div>',
        unsafe_allow_html=True,
    )

    try:
        response = requests.post(
            f"{BACKEND_URL}/explain",
            json={
                "repo_url": st.session_state.repo_url.strip()
            },
            timeout=600,
        )

        holder.empty()

        if not response.ok:
            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except Exception:
                detail = response.text

            st.error(detail)
            return

        st.session_state.analysis = response.json()
        st.session_state.page = "AI Explanation"
        st.rerun()

    except requests.RequestException as exc:
        holder.empty()
        st.error(
            "Could not connect to the FastAPI backend on port 8001. "
            f"Error: {exc}"
        )




with st.sidebar:
    sidebar()

status()

page = st.session_state.page


if page == "Home":
    left, right = st.columns([1.4, .82], gap="large")

    with left:
        st.markdown(
            """
            <div class="hero-card">
              <div class="eyebrow">
                OPEN SOURCE &nbsp; • &nbsp; LOCAL AI &nbsp; • &nbsp; NO API KEYS
              </div>
              <div class="hero-title">
                Local GitHub Repository<br>
                <span>Code Explainer</span>
              </div>
              <div class="hero-subtitle">
                Enter a public GitHub repository, analyze its files locally,
                and get a clear explanation using a local AI model.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="glass-card"
                 style="min-height:395px;display:flex;align-items:center;justify-content:center;">
              <div class="github-orb">◉</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    columns = st.columns(4)

    feature_cards = [
        (
            "⇩",
            "Download & Analyze",
            "Download the public repository and process relevant files.",
        ),
        (
            "◉",
            "AI Explanation",
            "Generate a clear explanation using the local LLM.",
        ),
        (
            "⌗",
            "Code Structure",
            "Inspect the analyzed repository file structure.",
        ),
        (
            "✓",
            "100% Local",
            "Use Ollama and Qwen without a cloud LLM API key.",
        ),
    ]

    for col, (icon, title, body) in zip(
        columns,
        feature_cards,
    ):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                  <div class="feature-icon">{icon}</div>
                  <div class="feature-title">{title}</div>
                  <div class="feature-text">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    if st.button(
        "Get Started  →",
        type="primary",
    ):
        st.session_state.page = "Explain Repository"
        st.rerun()


elif page == "Explain Repository":
    st.markdown(
        '<div class="page-title">Explain a GitHub Repository</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">'
        "Enter a public GitHub repository URL to analyze the repository "
        "and generate a detailed explanation."
        "</div>",
        unsafe_allow_html=True,
    )

    card(
        '<div class="section-title">GitHub Repository URL</div>'
        '<div class="small-muted">'
        "Example: https://github.com/username/repository"
        "</div>"
    )

    st.session_state.repo_url = st.text_input(
        "Repository URL",
        value=st.session_state.repo_url,
        placeholder="https://github.com/username/repository",
        label_visibility="collapsed",
    )

    if st.button(
        "Explain Repository  →",
        type="primary",
        use_container_width=True,
    ):
        if not st.session_state.repo_url.strip():
            st.warning(
                "Please enter a public GitHub repository URL."
            )
        else:
            run_analysis()

    st.markdown(
        '<div class="section-title" style="margin-top:24px;">How it works?</div>',
        unsafe_allow_html=True,
    )

    steps = [
        ("⇩", "1. Download", "Download repository locally"),
        ("▤", "2. Process Code", "Extract relevant files"),
        ("◉", "3. Generate Explanation", "Use Qwen 2.5 3B"),
        ("✓", "4. View Results", "Display the explanation"),
    ]

    step_columns = st.columns(4)

    for col, (icon, title, body) in zip(
        step_columns,
        steps,
    ):
        with col:
            st.markdown(
                f"""
                <div class="step">
                  <div class="step-icon">{icon}</div>
                  <div class="step-title">{title}</div>
                  <div class="step-text">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


elif page == "Repository Info":
    if require_analysis():
        data = st.session_state.analysis

        st.markdown(
            '<div class="page-title">Repository Information</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "Basic details and metadata of the analyzed repository."
            "</div>",
            unsafe_allow_html=True,
        )

        left, right = st.columns(
            [.8, 1.5],
            gap="large",
        )

        with left:
            card(
                '<div style="font-size:42px;">◈</div>'
                '<div style="font-size:21px;font-weight:800;margin-top:8px;">'
                + html.escape(data["repository"])
                + "</div>"
                '<div class="small-muted" style="margin-top:7px;">'
                + html.escape(data["description"])
                + "</div>"
                '<div style="margin-top:12px;"><span class="badge">Public</span></div>'
            )

            st.link_button(
                "View on GitHub ↗",
                data["html_url"],
                use_container_width=True,
            )

        with right:
            rows = [
                ("Repository", data["full_name"]),
                ("Full Name", data["html_url"]),
                ("Default Branch", data["default_branch"]),
                ("Description", data["description"]),
                ("Stars", format_number(data["stars"])),
                ("Forks", format_number(data["forks"])),
                ("Language", data["language"]),
                ("Acquisition", data["acquisition_method"]),
                ("Last Updated", format_date(data["updated_at"])),
            ]

            info = "".join(
                '<div class="info-row">'
                '<div class="info-label">'
                + html.escape(str(label))
                + '</div><div class="info-value">'
                + html.escape(str(value))
                + "</div></div>"
                for label, value in rows
            )

            card(
                '<div class="section-title">Repository Details</div>'
                + info
            )


elif page == "Code Structure":
    if require_analysis():
        data = st.session_state.analysis

        st.markdown(
            '<div class="page-title">Repository Structure</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "Visual representation of the analyzed repository file structure."
            "</div>",
            unsafe_allow_html=True,
        )

        tree = (
            '<div class="tree"><b>📁 '
            + html.escape(data["repository"])
            + '/</b>'
        )

        for index, item in enumerate(data["files"]):
            prefix = "└── " if index == len(data["files"]) - 1 else "├── "
            tree += (
                prefix
                + "📄 "
                + html.escape(item["path"])
                + "<br>"
            )

        tree += "</div>"

        card(tree)

        st.markdown(
            '<div class="small-muted" style="margin-top:10px;">'
            + str(data["files_analyzed"])
            + " readable files · "
            + str(data["source_files"])
            + " source files · "
            + format_number(data["lines_of_code"])
            + " source lines</div>",
            unsafe_allow_html=True,
        )


elif page == "File Viewer":
    if require_analysis():
        data = st.session_state.analysis

        st.markdown(
            '<div class="page-title">File Viewer</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "View the contents of files extracted from the repository."
            "</div>",
            unsafe_allow_html=True,
        )

        names = [item["path"] for item in data["files"]]

        if not names:
            st.info("No readable files are available.")
        else:
            selected = st.selectbox(
                "Select file",
                names,
            )

            chosen = next(
                item for item in data["files"]
                if item["path"] == selected
            )

            language = (
                chosen["extension"].lstrip(".")
                or "text"
            )

            st.code(
                chosen["content"],
                language=language,
            )


elif page == "AI Explanation":
    if require_analysis():
        data = st.session_state.analysis

        st.markdown(
            '<div class="page-title">AI Generated Explanation</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "Generated locally using Qwen 2.5 3B through Ollama."
            "</div>",
            unsafe_allow_html=True,
        )

        left, right = st.columns(
            [5, 1],
            gap="medium",
        )

        with left:
            card(
                '<div style="font-size:17px;font-weight:800;">'
                + html.escape(data["full_name"])
                + "</div>"
                '<div class="small-muted" style="margin-top:5px;">'
                + str(data["files_analyzed"])
                + " readable files · "
                + str(data["source_files"])
                + " source files</div>"
            )

        with right:
            st.download_button(
                "Download",
                data["explanation"],
                file_name=(
                    f'{data["repository"]}_explanation.txt'
                ),
                mime="text/plain",
                use_container_width=True,
            )

        st.markdown(
            '<div class="explanation-box">',
            unsafe_allow_html=True,
        )

        st.markdown(data["explanation"])

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


elif page == "Summary":
    if require_analysis():
        data = st.session_state.analysis

        st.markdown(
            '<div class="page-title">Summary</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "Quick summary of the repository analysis."
            "</div>",
            unsafe_allow_html=True,
        )

        metrics = [
            ("📄", format_number(data["files_analyzed"]), "Total Files"),
            ("⌗", format_number(data["source_files"]), "Source Files"),
            ("◉", data["language"], "Primary Language"),
            ("▣", data["repo_type"], "Repository Type"),
        ]

        columns = st.columns(4)

        for col, (icon, value, label) in zip(columns, metrics):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                      <div>{icon}</div>
                      <div class="metric-value">{html.escape(str(value))}</div>
                      <div class="metric-label">{html.escape(label)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        snapshot = [
            ("Repository", data["full_name"]),
            ("Default Branch", data["default_branch"]),
            ("Source Lines", format_number(data["lines_of_code"])),
            ("Stars", format_number(data["stars"])),
            ("Forks", format_number(data["forks"])),
        ]

        info = "".join(
            '<div class="info-row">'
            '<div class="info-label">'
            + html.escape(str(label))
            + '</div><div class="info-value">'
            + html.escape(str(value))
            + "</div></div>"
            for label, value in snapshot
        )

        st.markdown(
            '<div class="section-title" style="margin-top:26px;">'
            "Repository Snapshot</div>",
            unsafe_allow_html=True,
        )

        card(info)


st.markdown(
    '<div class="footer-line">'
    "Local GenAI • FastAPI • Streamlit • Ollama • Qwen 2.5 3B"
    "</div>",
    unsafe_allow_html=True,
)
