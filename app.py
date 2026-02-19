import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

from services.document_service import upload_document_both
from db.queries import search_documents, delete_document_by_filename, delete_blob_by_filename
from storage.gcs import download_file_timed, delete_file
from utils.cost_calculator import estimate_cost
from services.benchmark_service import run_benchmark, results_to_excel, BENCHMARK_SIZES


st.set_page_config(page_title="Student Document Manager", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:      #F9F8F6;
    --card:    #EFE9E3;
    --border:  #D9CFC7;
    --accent:  #C9B59C;
    --text:    #111111;
    --muted:   #5a5550;
    --accent-dark: #a8906e;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

/* ── Remove default Streamlit dark chrome ── */
[data-testid="stHeader"] {
    background-color: var(--bg) !important;
}

/* ── Page title ── */
h1 {
    color: var(--text) !important;
    font-weight: 700 !important;
    font-size: 1.9rem !important;
    letter-spacing: -0.3px;
    border-bottom: 2px solid var(--accent) !important;
    padding-bottom: 0.5rem;
    margin-bottom: 0.2rem !important;
}

/* ── Section headers ── */
h2 {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 1.15rem !important;
    letter-spacing: 0.3px;
    margin-top: 0 !important;
}

/* ── Subheaders ── */
h3 {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 0.97rem !important;
}

/* ── Body text ── */
p, span, div, li {
    color: var(--text) !important;
}

/* ── Muted caption ── */
[data-testid="stCaptionContainer"] p,
.stCaption, small {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
}

/* ── Section label pill ── */
.section-label {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 0.18rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 0.5rem;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2.5rem 0 !important;
}

/* ── Inputs ── */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #fff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
[data-baseweb="select"] > div {
    background-color: #fff !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] p {
    color: var(--text) !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
}

/* ── Primary button (amber) ── */
[data-testid="stButton"] button[kind="primary"] {
    background-color: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.4rem !important;
    transition: background 0.2s;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: var(--accent-dark) !important;
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] button {
    background-color: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.4rem !important;
    transition: background 0.2s;
}
[data-testid="stFormSubmitButton"] button:hover {
    background-color: var(--accent-dark) !important;
}

/* ── Secondary button ── */
[data-testid="stButton"] button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent-dark) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    margin-bottom: 0.35rem !important;
}
[data-testid="stDownloadButton"] button:hover {
    background-color: var(--border) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    color: var(--muted) !important;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: none !important;
}
/* info */
div[data-testid="stAlert"] > div[class*="info"] {
    background-color: #eef2f7 !important;
    border-left: 4px solid #7a9cbf !important;
    color: var(--text) !important;
}
/* success */
div[data-testid="stAlert"] > div[class*="success"] {
    background-color: #eef7f1 !important;
    border-left: 4px solid #5aaa78 !important;
    color: var(--text) !important;
}
/* warning */
div[data-testid="stAlert"] > div[class*="warning"] {
    background-color: #fdf6ec !important;
    border-left: 4px solid var(--accent) !important;
    color: var(--text) !important;
}
/* error */
div[data-testid="stAlert"] > div[class*="error"] {
    background-color: #fdf0f0 !important;
    border-left: 4px solid #d9534f !important;
    color: var(--text) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
}

/* ── Form container ── */
[data-testid="stForm"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary p {
    color: var(--text) !important;
    font-weight: 500;
}
[data-testid="stExpander"] summary svg {
    fill: var(--accent) !important;
    stroke: var(--accent) !important;
}
[data-testid="stExpander"] summary:hover p {
    color: var(--accent-dark) !important;
}

/* ── Selectbox / dropdown popover ── */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[data-baseweb="menu"] {
    background-color: #fff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}
[data-baseweb="menu"] li,
[data-baseweb="option"] {
    background-color: #fff !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover {
    background-color: var(--card) !important;
    color: var(--text) !important;
}
/* Selected option highlight */
[aria-selected="true"][data-baseweb="option"] {
    background-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── Date picker calendar ── */
[data-baseweb="calendar"] {
    background-color: #fff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}
[data-baseweb="calendar"] * {
    color: var(--text) !important;
}
/* Day cells */
[data-baseweb="calendar"] [role="gridcell"] button {
    color: var(--text) !important;
    background-color: transparent !important;
    border-radius: 50% !important;
}
[data-baseweb="calendar"] [role="gridcell"] button:hover {
    background-color: var(--card) !important;
}
/* Selected day */
[data-baseweb="calendar"] [aria-selected="true"] button,
[data-baseweb="calendar"] [data-selected="true"] button {
    background-color: var(--accent) !important;
    color: #fff !important;
}
/* Today highlight */
[data-baseweb="calendar"] [data-today="true"] button {
    border: 1px solid var(--accent) !important;
}
/* Month/year nav arrows */
[data-baseweb="calendar"] button[aria-label*="previous"],
[data-baseweb="calendar"] button[aria-label*="next"],
[data-baseweb="calendar"] button[aria-label*="Previous"],
[data-baseweb="calendar"] button[aria-label*="Next"] {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
}
/* Month/year header text */
[data-baseweb="calendar"] [data-baseweb="select"] div,
[data-baseweb="calendar"] [role="heading"] {
    color: var(--text) !important;
    background-color: #fff !important;
}
/* Weekday labels */
[data-baseweb="calendar"] [role="columnheader"] {
    color: var(--muted) !important;
}


/* ── Slider track ── */
[data-baseweb="slider"] [data-testid="stSliderThumb"] {
    background-color: var(--accent) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background-color: var(--accent) !important;
}

/* ── File uploader drop zone ── */
[data-testid="stFileUploader"] section {
    background-color: #fff !important;
    border: 2px dashed var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--accent) !important;
    background-color: var(--card) !important;
}
[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span {
    color: var(--text) !important;
}
[data-testid="stFileUploader"] section svg {
    fill: var(--accent) !important;
}
/* Browse files button inside uploader */
[data-testid="stFileUploader"] button {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploader"] button:hover {
    background-color: var(--border) !important;
    border-color: var(--accent) !important;
}

/* ── Code block ── */
code, pre {
    background-color: var(--card) !important;
    color: #3a3530 !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* ── Result banner ── */
.result-banner {
    background-color: var(--card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 0.9rem 1.4rem;
    margin: 1rem 0;
    color: var(--text);
    font-weight: 500;
    font-size: 0.95rem;
}

/* ── Winner badge ── */
.winner-badge {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-weight: 700;
    font-size: 0.88rem;
    padding: 0.2rem 0.9rem;
    border-radius: 20px;
    margin-left: 0.4rem;
}
/* ── Dropdown / selectbox popover (renders in a portal outside main DOM) ── */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li,
[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[data-baseweb="menu"] li,
ul[role="listbox"],
ul[role="listbox"] li {
    background-color: #fff !important;
    color: #111111 !important;
    border-color: #D9CFC7 !important;
}

/* Popover wrapper card */
div[data-baseweb="popover"] > div {
    border: 1px solid #D9CFC7 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}

/* Each option row */
[role="option"],
li[role="option"] {
    background-color: #fff !important;
    color: #111111 !important;
}
[role="option"]:hover,
li[role="option"]:hover {
    background-color: #EFE9E3 !important;
    color: #111111 !important;
}

/* Highlighted / selected option */
[aria-selected="true"],
[data-highlighted="true"] {
    background-color: #D9CFC7 !important;
    color: #111111 !important;
}

/* Any stray dark backgrounds from BaseWeb theme */
[data-baseweb] {
    color: #111111 !important;
}
[data-baseweb="select"] * {
    color: #111111 !important;
}

</style>
""", unsafe_allow_html=True)

# ─── Plotly layout defaults ────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#111111", family="Inter", size=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="#D9CFC7",
        borderwidth=1,
        font=dict(color="#111111", size=12),
    ),
    xaxis=dict(
        gridcolor="#D9CFC7",
        linecolor="#D9CFC7",
        tickfont=dict(color="#111111", size=11),
        title_font=dict(color="#111111", size=12),
    ),
    yaxis=dict(
        gridcolor="#D9CFC7",
        linecolor="#D9CFC7",
        tickfont=dict(color="#111111", size=11),
        title_font=dict(color="#111111", size=12),
    ),
)
C_SQL = "#C9B59C"   # warm tan — Cloud SQL
C_GCS = "#8a9fae"   # muted steel — GCS

# ─── Page title ────────────────────────────────────────────────────────────
st.title("Student Document Manager")
st.caption("Compare Cloud SQL and Google Cloud Storage — upload speed, download speed, and cost.")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — UPLOAD & COMPARE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Section 1</div>', unsafe_allow_html=True)
st.header("Upload Document")
st.caption(
    "Every upload is written to both Cloud SQL (raw BYTEA) and GCS simultaneously. "
    "Upload time and monthly storage cost are compared instantly."
)

col1, col2 = st.columns(2)
with col1:
    student_id   = st.text_input("Student ID", key="upload_sid")
    student_name = st.text_input("Student Name")
with col2:
    doc_type = st.selectbox("Document Type", ["ID", "Transcript", "Certificate", "Other"])
    file     = st.file_uploader("Choose a file")

if st.button("Upload to Both and Compare", type="primary"):
    if not student_id:
        st.error("Student ID is required.")
        st.stop()
    if file is None:
        st.error("Please select a file.")
        st.stop()

    with st.spinner("Uploading to Cloud SQL and GCS..."):
        try:
            result     = upload_document_both(student_id, student_name, doc_type, file)
            sql_ms     = result["sql_upload_ms"]
            gcs_ms     = result["gcs_upload_ms"]
            size_bytes = result["file_size_bytes"]
            cost       = estimate_cost(size_bytes)

            st.success(f"'{result['filename']}' uploaded to both destinations.")

            st.subheader("Upload Speed")
            c1, c2 = st.columns(2)
            with c1:
                st.metric(
                    label="Cloud SQL Upload Time",
                    value=f"{sql_ms} ms",
                    delta=f"{round(sql_ms - gcs_ms, 2)} ms vs GCS",
                    delta_color="inverse"
                )
            with c2:
                st.metric(
                    label="GCS Upload Time",
                    value=f"{gcs_ms} ms",
                    delta=f"{round(gcs_ms - sql_ms, 2)} ms vs SQL",
                    delta_color="inverse"
                )

            winner_upload = "Cloud SQL" if sql_ms < gcs_ms else "GCS"
            st.markdown(
                f'<div class="result-banner">Faster upload: '
                f'<span class="winner-badge">{winner_upload}</span></div>',
                unsafe_allow_html=True
            )

            st.subheader("Monthly Storage Cost Estimate")
            c3, c4 = st.columns(2)
            with c3:
                st.metric(
                    label="Cloud SQL Cost / month",
                    value=f"${cost['sql_monthly_usd']:.6f}",
                    help=f"${cost['sql_price_per_gb']}/GB/month (SSD)"
                )
            with c4:
                st.metric(
                    label="GCS Cost / month",
                    value=f"${cost['gcs_monthly_usd']:.6f}",
                    help=f"${cost['gcs_price_per_gb']}/GB/month (Standard)"
                )

            st.info(
                f"File size: {cost['size_kb']} KB — "
                f"GCS is {cost['gcs_cheaper_by_x']}x cheaper than Cloud SQL for storage."
            )

        except Exception as e:
            st.error(f"Upload failed: {e}")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — ADVANCED SEARCH & FILTER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Section 2</div>', unsafe_allow_html=True)
st.header("Advanced Search and Filter")
st.caption(
    "Cloud SQL strength: filter by student, document type, filename, and date range using SQL WHERE clauses. "
    "GCS has no query language — this is not possible natively."
)

with st.form("search_form"):
    sf1, sf2 = st.columns(2)
    with sf1:
        s_student_id = st.text_input("Student ID (optional)")
        s_filename   = st.text_input("Filename contains (optional)")
    with sf2:
        s_doc_type = st.selectbox("Document Type", ["All", "ID", "Transcript", "Certificate", "Other"])

    submitted = st.form_submit_button("Search", type="primary")

if submitted:
    try:
        results = search_documents(
            student_id=s_student_id or None,
            doc_type=s_doc_type,
            filename_query=s_filename or None,
        )
        # Store results in session_state so they survive reruns (e.g. after delete)
        st.session_state["search_results"] = results
        st.session_state["search_params"] = {
            "student_id": s_student_id,
            "doc_type": s_doc_type,
            "filename": s_filename,
        }
    except Exception as e:
        st.error(f"Search error: {e}")

# ── Render results from session_state (persists after delete reruns) ─────────
if "search_results" in st.session_state:
    results = st.session_state["search_results"]
    params  = st.session_state.get("search_params", {})

    if results:
        st.success(f"Found {len(results)} document(s) matching your filters.")

        df_search = pd.DataFrame(results)
        df_search.columns = [
            "Row Key", "Student ID", "Student Name", "Doc Type",
            "Filename", "GCS Path", "Size (KB)", "Uploaded At"
        ]
        st.dataframe(df_search.drop(columns=["Row Key", "GCS Path"]), use_container_width=True)

        st.markdown("**Actions per document**")

        for doc in results:
            col_info, col_dl, col_del = st.columns([4, 2, 1])

            with col_info:
                st.markdown(
                    f"**{doc['filename']}** &nbsp;·&nbsp; "
                    f"{doc['student_id']} &nbsp;·&nbsp; "
                    f"{doc['doc_type']} &nbsp;·&nbsp; "
                    f"{doc['size_kb']} KB",
                    unsafe_allow_html=True
                )

            with col_dl:
                try:
                    data, elapsed = download_file_timed(doc["gcs_object_name"])
                    st.download_button(
                        label=f"Download ({elapsed} ms)",
                        data=data,
                        file_name=doc["filename"],
                        key=f"dl_{doc['row_key']}"
                    )
                except Exception:
                    st.warning("GCS unavailable")

            with col_del:
                if st.button("Delete", key=f"del_{doc['row_key']}",
                             help=f"Permanently delete {doc['filename']} from Cloud SQL and GCS",
                             type="secondary"):
                    try:
                        delete_document_by_filename(doc["student_id"], doc["filename"])
                        delete_blob_by_filename(doc["student_id"], doc["filename"])
                        delete_file(doc["gcs_object_name"])
                        # Remove from session_state immediately so rerun shows updated list
                        st.session_state["search_results"] = [
                            r for r in st.session_state["search_results"]
                            if r["row_key"] != doc["row_key"]
                        ]
                        st.success(f"'{doc['filename']}' deleted from Cloud SQL and GCS.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Delete failed: {ex}")

            st.divider()

        with st.expander("View SQL query used"):
            conditions_display = []
            if params.get("student_id"):
                conditions_display.append(f"d.student_id = '{params['student_id']}'")
            if params.get("doc_type") and params["doc_type"] != "All":
                conditions_display.append(f"d.doc_type = '{params['doc_type']}'")
            if params.get("filename"):
                conditions_display.append(f"d.filename ILIKE '%{params['filename']}%'")
            where = ("WHERE " + " AND ".join(conditions_display)) if conditions_display else "(no filters — all records)"
            st.code(f"""
SELECT d.student_id, s.name, d.doc_type, d.filename,
       d.file_size_bytes / 1024.0 AS size_kb, d.uploaded_at
FROM documents d
JOIN students s ON d.student_id = s.student_id
{where}
ORDER BY d.uploaded_at DESC;
            """, language="sql")
    else:
        st.warning("No documents found matching your filters.")


st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — REAL BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Section 3</div>', unsafe_allow_html=True)
st.header("Real Upload and Download Benchmark")
st.caption(
    "Generates actual binary test files (1 KB to 5 MB), uploads them to both Cloud SQL and GCS, "
    "measures real upload and download times, and exports the results to Excel."
)

st.info(
    f"{len(BENCHMARK_SIZES)} file sizes will be tested: "
    + ", ".join(s[0] for s in BENCHMARK_SIZES)
)

runs_per_size = st.slider(
    "Runs per file size — more runs produce more accurate averages",
    min_value=1, max_value=5, value=3
)

st.warning(
    f"This will perform {len(BENCHMARK_SIZES) * runs_per_size * 4} real network operations "
    f"({len(BENCHMARK_SIZES) * runs_per_size} uploads and downloads to each service). "
    "Expect 1 to 3 minutes depending on your connection."
)

btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    run_clicked = st.button("Run Benchmark", type="primary", key="run_benchmark")
with btn_col2:
    if st.button("Reset Results", key="reset_benchmark"):
        st.session_state.pop("benchmark_results", None)
        st.rerun()

if run_clicked:
    progress_bar = st.progress(0, text="Starting benchmark...")
    status_text  = st.empty()

    def update_progress(current, total, label):
        pct = int((current / total) * 100)
        progress_bar.progress(pct, text=f"[{current}/{total}] {label}")
        status_text.caption(f"Currently testing: {label}")

    try:
        with st.spinner("Running benchmark — please wait..."):
            bench_results = run_benchmark(
                runs_per_size=runs_per_size,
                progress_callback=update_progress
            )
        st.session_state["benchmark_results"] = bench_results
        progress_bar.progress(100, text="Benchmark complete.")
        status_text.empty()

    except Exception as e:
        st.error(f"Benchmark failed: {e}")

# ── Results (persisted in session_state) ──────────────────────────────────
if "benchmark_results" in st.session_state:
    bench_results = st.session_state["benchmark_results"]
    st.success(f"Benchmark complete — {len(bench_results)} measurements recorded.")

    df_raw = pd.DataFrame(bench_results)

    st.subheader("Raw Results")
    df_display = df_raw[[
        "size_label", "run",
        "sql_upload_ms", "gcs_upload_ms",
        "sql_download_ms", "gcs_download_ms",
        "faster_upload", "faster_download"
    ]].copy()
    df_display.columns = [
        "Size", "Run",
        "SQL Upload (ms)", "GCS Upload (ms)",
        "SQL Download (ms)", "GCS Download (ms)",
        "Faster Upload", "Faster Download"
    ]
    st.dataframe(df_display, use_container_width=True, height=350)

    st.subheader("Averages per File Size")
    df_avg = df_raw.groupby("size_label", sort=False).agg(
        avg_sql_upload=("sql_upload_ms", "mean"),
        avg_gcs_upload=("gcs_upload_ms", "mean"),
        avg_sql_download=("sql_download_ms", "mean"),
        avg_gcs_download=("gcs_download_ms", "mean"),
        sql_cost=("sql_cost_usd", "first"),
        gcs_cost=("gcs_cost_usd", "first"),
    ).round(6).reset_index()

    size_order = [s[0] for s in BENCHMARK_SIZES]
    df_avg["size_label"] = pd.Categorical(df_avg["size_label"], categories=size_order, ordered=True)
    df_avg = df_avg.sort_values("size_label")
    size_labels = df_avg["size_label"].tolist()

    st.dataframe(df_avg.rename(columns={
        "size_label":       "Size",
        "avg_sql_upload":   "Avg SQL Upload (ms)",
        "avg_gcs_upload":   "Avg GCS Upload (ms)",
        "avg_sql_download": "Avg SQL Download (ms)",
        "avg_gcs_download": "Avg GCS Download (ms)",
        "sql_cost":         "SQL Cost/mo ($)",
        "gcs_cost":         "GCS Cost/mo ($)",
    }), use_container_width=True)

    # ── Upload time chart ──
    st.subheader("Upload Time by File Size")
    fig_up = go.Figure(data=[
        go.Bar(name="Cloud SQL", x=size_labels, y=df_avg["avg_sql_upload"].tolist(),
               marker_color=C_SQL),
        go.Bar(name="GCS",       x=size_labels, y=df_avg["avg_gcs_upload"].tolist(),
               marker_color=C_GCS),
    ])
    fig_up.update_layout(barmode="group", xaxis_title="File Size",
                         yaxis_title="Avg Upload Time (ms)", height=380, **PLOT_LAYOUT)
    st.plotly_chart(fig_up, use_container_width=True)

    # ── Download time chart ──
    st.subheader("Download Time by File Size")
    fig_dl = go.Figure(data=[
        go.Bar(name="Cloud SQL", x=size_labels, y=df_avg["avg_sql_download"].tolist(),
               marker_color=C_SQL),
        go.Bar(name="GCS",       x=size_labels, y=df_avg["avg_gcs_download"].tolist(),
               marker_color=C_GCS),
    ])
    fig_dl.update_layout(barmode="group", xaxis_title="File Size",
                         yaxis_title="Avg Download Time (ms)", height=380, **PLOT_LAYOUT)
    st.plotly_chart(fig_dl, use_container_width=True)

    # ── Cost chart ──
    st.subheader("Monthly Storage Cost Estimate")
    st.caption("Cost per file stored for one month — Cloud SQL (SSD) vs GCS (Standard).")
    sql_costs_micro = [round(v * 1_000_000, 4) for v in df_avg["sql_cost"].tolist()]
    gcs_costs_micro = [round(v * 1_000_000, 4) for v in df_avg["gcs_cost"].tolist()]
    fig_cost = go.Figure(data=[
        go.Bar(
            name="Cloud SQL (~$0.17/GB)",
            x=size_labels, y=sql_costs_micro,
            marker_color=C_SQL,
            text=[f"${v:.4f}" for v in sql_costs_micro],
            textposition="outside",
            textfont=dict(color="#111111"),
        ),
        go.Bar(
            name="GCS (~$0.023/GB)",
            x=size_labels, y=gcs_costs_micro,
            marker_color=C_GCS,
            text=[f"${v:.4f}" for v in gcs_costs_micro],
            textposition="outside",
            textfont=dict(color="#111111"),
        ),
    ])
    fig_cost.update_layout(
        barmode="group",
        xaxis_title="File Size",
        yaxis_title="Monthly Cost (millionths of a dollar)",
        height=400,
        **PLOT_LAYOUT
    )
    st.plotly_chart(fig_cost, use_container_width=True)

    gcs_cheaper = round(0.17 / 0.023, 1)
    st.markdown(
        f'<div class="result-banner">GCS is <span class="winner-badge">{gcs_cheaper}x cheaper</span> '
        f'than Cloud SQL for storage. For large files, this difference is very significant.</div>',
        unsafe_allow_html=True
    )

    st.subheader("Export Results")
    excel_bytes = results_to_excel(bench_results)
    st.download_button(
        label="Download benchmark_results.xlsx",
        data=excel_bytes,
        file_name="benchmark_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.caption("Two sheets: Raw Results (every individual run) and Averages by Size.")
