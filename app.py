import re
import time
import streamlit as st

from pipeline import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ───────────────────────────── page config ─────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────── styling ─────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e8e4dc; }

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.5rem 3rem 4rem; max-width: 1200px; }

/* sidebar */
section[data-testid="stSidebar"] { background: #0e0e14; border-right: 1px solid rgba(255,140,50,0.12); }

/* hero */
.hero { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero-eyebrow { font-family:'DM Mono',monospace; font-size:.7rem; letter-spacing:.25em;
    text-transform:uppercase; color:#ff8c32; margin-bottom:1rem; }
.hero h1 { font-family:'Syne',sans-serif; font-size:clamp(2.8rem,6vw,4.8rem); font-weight:800;
    line-height:1; letter-spacing:-.03em; color:#f0ebe0; margin:0 0 1rem; }
.hero h1 span { color:#ff8c32; }
.hero-sub { font-size:1.02rem; font-weight:300; color:#a09890; max-width:540px; margin:0 auto; line-height:1.65; }
.divider { height:1px; background:linear-gradient(90deg,transparent,rgba(255,140,50,.3),transparent); margin:1.8rem 0; }
.section-heading { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:#f0ebe0; margin:0 0 .9rem; }
.field-label { font-family:'DM Mono',monospace; font-size:.72rem; letter-spacing:.15em;
    text-transform:uppercase; color:#ff8c32; margin-bottom:.5rem; }
.hint { font-family:'DM Mono',monospace; font-size:.68rem; color:#6a625a; letter-spacing:.1em; margin:.9rem 0 .4rem; }

/* bordered containers = cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.028);
    border: 1px solid rgba(255,140,50,0.16) !important;
    border-radius: 16px !important;
    padding: .6rem .9rem;
}

/* text input */
.stTextInput input {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,140,50,.25) !important;
    border-radius: 10px !important; color: #f0ebe0 !important; font-size: 1rem !important;
    padding: .75rem 1rem !important;
}
.stTextInput input:focus { border-color:#ff8c32 !important; box-shadow:0 0 0 3px rgba(255,140,50,.14) !important; }

/* buttons: primary = run, secondary = example chips / history */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg,#ff8c32 0%,#ff5a1a 100%) !important; color:#0a0a0f !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important; border:none !important;
    border-radius:10px !important; padding:.65rem 1.5rem !important;
    box-shadow:0 4px 20px rgba(255,140,50,.3) !important; transition:transform .15s, box-shadow .15s !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    transform:translateY(-2px); box-shadow:0 8px 28px rgba(255,140,50,.42) !important; }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background: rgba(255,255,255,.04) !important; border:1px solid rgba(255,255,255,.1) !important;
    color:#b5aea4 !important; border-radius:8px !important; font-size:.78rem !important;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color:#ff8c32 !important; color:#ff8c32 !important; }

/* pipeline steps */
.step { display:flex; align-items:center; gap:.9rem; background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.07); border-left:3px solid rgba(255,255,255,.08);
    border-radius:12px; padding:.95rem 1.2rem; margin-bottom:.7rem; transition:all .3s; }
.step.running { border-color:rgba(255,140,50,.4); border-left-color:#ff8c32; background:rgba(255,140,50,.05); }
.step.done    { border-color:rgba(80,200,120,.28); border-left-color:#50c878; background:rgba(80,200,120,.035); }
.step.error   { border-color:rgba(255,80,80,.35);  border-left-color:#ff5050; background:rgba(255,80,80,.05); }
.step-icon { font-size:1.25rem; width:1.8rem; text-align:center; }
.step-body { flex:1; }
.step-title { font-family:'Syne',sans-serif; font-weight:700; font-size:.95rem; color:#f0ebe0; }
.step-desc { font-size:.78rem; color:#7a726a; margin-top:.1rem; }
.step-status { font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.1em; color:#555; }
.step.running .step-status { color:#ff8c32; animation:pulse 1.2s ease-in-out infinite; }
.step.done .step-status { color:#50c878; }
.step.error .step-status { color:#ff5050; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
@media (prefers-reduced-motion: reduce) { .step.running .step-status { animation:none; } }

/* stats */
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; margin-bottom:1.4rem; }
.stat { background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:1rem 1.2rem; }
.stat-val { font-family:'Syne',sans-serif; font-size:1.7rem; font-weight:800; color:#f0ebe0; line-height:1.1; }
.stat-lbl { font-family:'DM Mono',monospace; font-size:.66rem; letter-spacing:.14em; text-transform:uppercase; color:#7a726a; margin-top:.35rem; }
@media (max-width:760px){ .stats{grid-template-columns:repeat(2,1fr);} .block-container{padding:1rem 1rem 3rem;} }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap:.4rem; border-bottom:1px solid rgba(255,255,255,.08); }
.stTabs [data-baseweb="tab"] { font-family:'DM Mono',monospace; font-size:.78rem; letter-spacing:.06em; color:#8a8278; }
.stTabs [aria-selected="true"] { color:#ff8c32 !important; }
.stTabs [data-baseweb="tab-highlight"] { background:#ff8c32 !important; }

/* report text */
.stMarkdown p, .stMarkdown li { line-height:1.75; color:#d3cec4; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { font-family:'Syne',sans-serif; color:#f0ebe0; }
.stMarkdown h2 { color:#ff8c32; font-size:1.25rem; margin-top:1.6rem; }
.stMarkdown a { color:#ff8c32; }

.footer { font-family:'DM Mono',monospace; font-size:.7rem; color:#5a524a; text-align:center; margin-top:3rem; letter-spacing:.08em; }
</style>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── helpers ─────────────────────────────
STEPS = [
    ("🔍", "Search Agent", "Gathers recent web information"),
    ("📖", "Reader Agent", "Scrapes and extracts deep content"),
    ("✍️", "Writer Chain", "Drafts the full research report"),
    ("🧐", "Critic Chain", "Reviews and scores the report"),
]
LABELS = {"pending": "WAITING", "running": "● RUNNING", "done": "✓ DONE", "error": "✕ FAILED"}
EXAMPLES = ["LLM agents in 2026", "CRISPR gene editing", "Fusion energy progress", "Quantum error correction"]


def pipeline_html(states, times):
    out = []
    for (icon, title, desc), state, t in zip(STEPS, states, times):
        status = LABELS[state] + (f" · {t:.1f}s" if state == "done" and t else "")
        out.append(
            f'<div class="step {state}"><div class="step-icon">{icon}</div>'
            f'<div class="step-body"><div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div></div>'
            f'<div class="step-status">{status}</div></div>'
        )
    return "".join(out)


def to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            b if isinstance(b, str) else b.get("text", "")
            for b in content
            if isinstance(b, str) or (isinstance(b, dict) and b.get("type") == "text")
        )
    return str(content)


def run_agent(agent, prompt):
    res = agent.invoke({"messages": [("user", prompt)]})
    msgs = res["messages"]
    calls = [f"{c['name']}({c['args']})" for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
    return to_text(msgs[-1].content), calls


def parse_score(text):
    m = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", text)
    return float(m.group(1)) if m else None


def set_topic(t):
    st.session_state.topic = t


def load_run(i):
    st.session_state.results = st.session_state.history[i]


for k, v in (("results", None), ("history", []), ("topic", "")):
    st.session_state.setdefault(k, v)

# ───────────────────────────── sidebar ─────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-heading">History</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.caption("Your finished research runs show up here.")
    for i, item in reversed(list(enumerate(st.session_state.history))):
        st.button(item["topic"][:34], key=f"hist_{i}", on_click=load_run, args=(i,), use_container_width=True)
    if st.session_state.history and st.button("Clear history", use_container_width=True):
        st.session_state.history = []
        st.session_state.results = None
        st.rerun()

# ───────────────────────────── hero ─────────────────────────────
st.markdown(
    """
<div class="hero">
<div class="hero-eyebrow">Multi-Agent AI System</div>
<h1>Research<span>Mind</span></h1>
<p class="hero-sub">Four specialised agents search, read, write and critique, so you get a sourced research report on any topic.</p>
</div>
<div class="divider"></div>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── input + pipeline ─────────────────────────────
col_in, col_gap, col_pipe = st.columns([5, 0.4, 4])

with col_in:
    with st.container(border=True):
        st.markdown('<div class="field-label">Research topic</div>', unsafe_allow_html=True)
        topic = st.text_input(
            "Research topic",
            key="topic",
            placeholder="e.g. Quantum computing breakthroughs in 2026",
            label_visibility="collapsed",
        )
        run_btn = st.button("⚡  Run research pipeline", type="primary", use_container_width=True)
        st.markdown('<div class="hint">OR TRY ONE OF THESE</div>', unsafe_allow_html=True)
        chip_cols = st.columns(2)
        for i, ex in enumerate(EXAMPLES):
            chip_cols[i % 2].button(ex, key=f"ex_{i}", on_click=set_topic, args=(ex,), use_container_width=True)

with col_pipe:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    pipe_box = st.empty()
    done_state = ["done"] * 4 if st.session_state.results else ["pending"] * 4
    done_times = st.session_state.results["times"] if st.session_state.results else [0] * 4
    pipe_box.markdown(pipeline_html(done_state, done_times), unsafe_allow_html=True)

# ───────────────────────────── run ─────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Enter a research topic first.")
    else:
        topic = topic.strip()
        st.session_state.results = None
        states, times = ["pending"] * 4, [0.0] * 4
        data = {"topic": topic}
        failed = False

        def stage(i, fn):
            """Run one stage, update the live pipeline card, record its time."""
            states[i] = "running"
            pipe_box.markdown(pipeline_html(states, times), unsafe_allow_html=True)
            t0 = time.time()
            try:
                out = fn()
            except Exception as e:
                states[i] = "error"
                pipe_box.markdown(pipeline_html(states, times), unsafe_allow_html=True)
                raise e
            times[i] = time.time() - t0
            states[i] = "done"
            pipe_box.markdown(pipeline_html(states, times), unsafe_allow_html=True)
            return out

        try:
            data["search"], data["search_calls"] = stage(
                0,
                lambda: run_agent(
                    build_search_agent(),
                    f"Find recent, reliable and detailed information about: {topic}. "
                    "Return titles, URLs and key snippets of the best sources.",
                ),
            )
            data["reader"], data["reader_calls"] = stage(
                1,
                lambda: run_agent(
                    build_reader_agent(),
                    f"Based on these search results about '{topic}', pick the single most relevant "
                    "URL and scrape it for deeper content. Return the content with its URL.\n\n"
                    f"Search results:\n{data['search'][:4000]}",
                ),
            )
            research = f"SEARCH RESULTS:\n{data['search']}\n\nSCRAPED CONTENT:\n{data['reader']}"
            data["report"] = stage(2, lambda: writer_chain.invoke({"topic": topic, "research": research}))
            data["feedback"] = stage(3, lambda: critic_chain.invoke({"report": data["report"]}))

            data["times"] = times
            st.session_state.results = data
            st.session_state.history.append(data)
        except Exception as e:
            st.error(f"The pipeline stopped: {e}")

# ───────────────────────────── results ─────────────────────────────
r = st.session_state.results
if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-heading">Results · {r["topic"]}</div>', unsafe_allow_html=True)

    score = parse_score(r["feedback"])
    score_txt = f"{score:g}/10" if score is not None else "n/a"
    score_col = "#50c878" if (score or 0) >= 8 else "#ff8c32" if (score or 0) >= 5 else "#ff5050"
    sources = len(set(re.findall(r"https?://[^\s)>\]]+", r["report"])))
    st.markdown(
        f"""
<div class="stats">
<div class="stat"><div class="stat-val">{sum(r["times"]):.0f}s</div><div class="stat-lbl">Total time</div></div>
<div class="stat"><div class="stat-val">{len(r["report"].split()):,}</div><div class="stat-lbl">Report words</div></div>
<div class="stat"><div class="stat-val">{sources}</div><div class="stat-lbl">Sources cited</div></div>
<div class="stat"><div class="stat-val" style="color:{score_col}">{score_txt}</div><div class="stat-lbl">Critic score</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    tab_rep, tab_crit, tab_search, tab_read = st.tabs(
        ["📝 Final report", "🧐 Critic feedback", "🔍 Search results", "📖 Scraped content"]
    )
    with tab_rep:
        with st.container(border=True):
            st.markdown(r["report"])
        st.download_button(
            "⬇  Download report (.md)",
            data=r["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )
    with tab_crit:
        with st.container(border=True):
            st.markdown(r["feedback"])
    with tab_search:
        if r["search_calls"]:
            with st.expander("Tool calls"):
                for c in r["search_calls"]:
                    st.code(c, language="text")
        with st.container(border=True):
            st.markdown(r["search"])
    with tab_read:
        if r["reader_calls"]:
            with st.expander("Tool calls"):
                for c in r["reader_calls"]:
                    st.code(c, language="text")
        with st.container(border=True):
            st.markdown(r["reader"])

st.markdown('<div class="footer">ResearchMind · LangChain multi-agent pipeline · Streamlit</div>', unsafe_allow_html=True)