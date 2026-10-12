import os
import glob
import sqlite3
import subprocess
import pandas as pd
import streamlit as st

DB_PATH = "outputs/genomic_pipeline.db"
BIOMARKERS_PATH = "data/biomarkers.fasta"
DATA_DIR = "data"

st.set_page_config(
    page_title="Genomic-ETL Clinical & Ingestion Monitor",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');

    .stApp {
        background-color: #ffdce5 !important;
        background-image: radial-gradient(#fca5ba 1.5px, transparent 1.5px) !important;
        background-size: 20px 20px !important;
        font-family: 'Fredoka', cursive, sans-serif !important;
        color: #4a0d20 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f76c8c !important;
        border-right: 4px solid #4a0d20 !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        text-shadow: 2px 2px 0px #4a0d20;
        font-family: 'Fredoka', cursive, sans-serif !important;
    }

    h1, h2, h3, h4, p, label {
        font-family: 'Fredoka', cursive, sans-serif !important;
    }

    h1 {
        color: #ff2a6d !important;
        text-shadow: 2px 2px 0px #4e071e, 4px 4px 0px #ffb3c1 !important;
        text-align: center;
        margin-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }

    h2, h3 {
        color: #8c0f34 !important;
    }

    button, .stButton>button {
        background: #ff4d6d !important;
        color: white !important;
        border: 3px solid #4a0d20 !important;
        border-radius: 20px !important;
        box-shadow: 0px 5px 0px #4a0d20 !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 0px #4a0d20;
        transition: transform 0.1s ease, box-shadow 0.1s ease !important;
    }

    button:active, .stButton>button:active {
        transform: translateY(4px) !important;
        box-shadow: 0px 1px 0px #4a0d20 !important;
    }

    button:hover, .stButton>button:hover {
        background: #ff758f !important;
        color: white !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #8c0f34 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stMetricValue"] div {
        color: #ff2a6d !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 3px solid #5c1d30 !important;
        border-radius: 20px !important;
        box-shadow: 4px 4px 0px #5c1d30 !important;
        padding: 10px 15px !important;
    }

    [data-testid="stDataFrame"] {
        border: 3px solid #4a0d20 !important;
        border-radius: 18px !important;
        overflow: hidden !important;
        box-shadow: 4px 4px 0px #4a0d20 !important;
        background-color: #ffffff !important;
    }

    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] canvas {
        filter: invert(0) !important;
    }

    .stTextArea textarea, .stTextInput input, [data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #4a0d20 !important;
        border: 3px solid #4a0d20 !important;
        border-radius: 16px !important;
        font-family: 'Fredoka', cursive, sans-serif !important;
        font-size: 1rem !important;
        box-shadow: 3px 3px 0px #4a0d20 !important;
    }

    [data-testid="stFileUploader"] {
        width: 100% !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border: 3px dashed #ff4d6d !important;
        border-radius: 20px !important;
        padding: 20px 15px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
    }

    [data-testid="stFileUploader"] button {
        background: #ff4d6d !important;
        color: white !important;
        border: 2px solid #4a0d20 !important;
        border-radius: 15px !important;
        box-shadow: 0px 3px 0px #4a0d20 !important;
        padding: 6px 18px !important;
        font-family: 'Fredoka', cursive, sans-serif !important;
        font-size: 0.95rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: static !important;
        height: auto !important;
        width: auto !important;
    }

    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small {
        color: #8c0f34 !important;
        font-family: 'Fredoka', cursive, sans-serif !important;
        font-size: 0.85rem !important;
        display: block !important;
        position: static !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }

    button[data-baseweb="tab"] {
        color: #8c0f34 !important;
        font-weight: 600 !important;
        font-family: 'Fredoka', cursive, sans-serif !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ff2a6d !important;
        border-bottom-color: #ff2a6d !important;
        border-bottom-width: 4px !important;
    }

    .stAlert {
        border-radius: 20px !important;
        border: 3px solid #5c1d30 !important;
        box-shadow: 4px 4px 0px #5c1d30 !important;
    }

    code {
        background-color: #ffcad4 !important;
        color: #4a0d20 !important;
        border: 2px solid #4a0d20 !important;
        border-radius: 10px !important;
        padding: 2px 8px !important;
        font-weight: bold !important;
    }

    hr {
        border: 2px dashed #ff4d6d !important;
    }

    [data-testid="stIcon"], 
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarExpandButton"] span,
    span[class*="material-symbols"], 
    span[class*="icon"],
    .material-symbols-rounded,
    .material-symbols-sharp,
    .material-symbols-outlined {
        font-family: "Material Symbols Rounded", "Source Sans Pro", sans-serif !important;
        font-feature-settings: "liga" 1 !important;
        text-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Genomic-ETL Clinical & Ingestion Monitor")
st.caption("<div style='text-align:center; font-weight:bold; color:#8c0f34;'>End-to-end pipeline execution, FASTQ file ingestion, biomarker surveillance, and ad-hoc sequence testing! ✨</div>", unsafe_allow_html=True)

def load_biomarkers():
    biomarkers = {}
    if os.path.exists(BIOMARKERS_PATH):
        with open(BIOMARKERS_PATH, "r") as f:
            current_id = None
            seq = []
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_id:
                        biomarkers[current_id] = "".join(seq)
                    current_id = line[1:]
                    seq = []
                else:
                    seq.append(line)
            if current_id:
                biomarkers[current_id] = "".join(seq)
    return biomarkers


st.sidebar.header("Pipeline Execution Control")


available_files = glob.glob(f"{DATA_DIR}/*.fastq")
selected_file = st.sidebar.selectbox("Select Dataset to Run", available_files)

if st.sidebar.button("Run Pipeline on Selected File", use_container_width=True):
    with st.spinner(f"Running pipeline on {selected_file}..."):
        result = subprocess.run(
            ["python3", "main.py", selected_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            st.sidebar.success(f"Successfully processed {os.path.basename(selected_file)}!")
        else:
            st.sidebar.error("Pipeline run failed.")
            st.sidebar.code(result.stderr)

st.sidebar.markdown("---")


st.sidebar.subheader("Upload New FASTQ File")
uploaded_file = st.sidebar.file_uploader("Upload .fastq", type=["fastq"])

if uploaded_file is not None:
    upload_save_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(upload_save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Saved to `{upload_save_path}`")
    
    if st.sidebar.button("Run Pipeline on Uploaded File", use_container_width=True):
        with st.spinner("Processing uploaded FASTQ..."):
            result = subprocess.run(
                ["python3", "main.py", upload_save_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.sidebar.success("Upload ingested and processed!")
            else:
                st.sidebar.error("Execution error on uploaded file:")
                st.sidebar.code(result.stderr)


st.header("Target Risk Biomarkers (`data/biomarkers.fasta`)")
biomarkers_dict = load_biomarkers()
if biomarkers_dict:
    b_df = pd.DataFrame(
        [{"Biomarker ID": k, "Motif Sequence": v, "Length (bp)": len(v)} for k, v in biomarkers_dict.items()]
    )
    st.dataframe(b_df, use_container_width=True)
else:
    st.warning("No biomarkers found in `data/biomarkers.fasta`.")

st.markdown("---")


st.header("Sequence Tester")
st.caption("Paste an arbitrary nucleotide string to check for quality validity and clinical risk motifs.")

col_in, col_res = st.columns([2, 1])

with col_in:
    test_seq = st.text_area("Input Nucleotide Sequence (A, C, G, T):", height=100).strip().upper()

with col_res:
    if test_seq:
        valid_bases = set("ACGTN")
        seq_valid = all(base in valid_bases for base in test_seq)
        
        if not seq_valid:
            st.error("Invalid sequence: Contains characters outside {A, C, G, T, N}.")
        else:
            st.success(f"Valid sequence length: {len(test_seq)} bp")
            gc_count = test_seq.count("G") + test_seq.count("C")
            gc_content = (gc_count / len(test_seq)) * 100 if len(test_seq) > 0 else 0
            st.metric("GC Content", f"{gc_content:.1f}%")


            matches = []
            for b_id, motif in biomarkers_dict.items():
                if motif in test_seq:
                    matches.append((b_id, motif))
            
            if matches:
                for b_id, motif in matches:
                    st.error(f"Risk Biomarker Detected: **{b_id}** (`{motif}`)")
            else:
                st.info(" Negative: No known target motifs identified.")

st.markdown("---")

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    try:

        total_patients = pd.read_sql("SELECT COUNT(*) AS count FROM patients;", conn).iloc[0]["count"]
        total_sequences = pd.read_sql("SELECT COUNT(*) AS count FROM genomic_sequences;", conn).iloc[0]["count"]
        total_alerts = pd.read_sql("SELECT COUNT(*) AS count FROM biomarker_alerts;", conn).iloc[0]["count"]
        avg_quality = pd.read_sql("SELECT AVG(avg_quality_score) AS avg FROM genomic_sequences;", conn).iloc[0]["avg"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ingested Patients", int(total_patients))
        c2.metric("Filtered Sequences (Q20+)", int(total_sequences))
        c3.metric("Biomarker Alerts Flagged", int(total_alerts))
        c4.metric("Mean Phred Score", f"{avg_quality:.2f}" if avg_quality is not None else "0.00")

        tab1, tab2, tab3 = st.tabs(["Clinical Alerts", "Processed Sequences & ML Metadata", "Quality Distributions"])

        with tab1:
            alerts_df = pd.read_sql(
                """
                SELECT 
                    a.alert_id,
                    a.patient_id,
                    a.sequence_id,
                    a.matched_window,
                    a.flagged_at
                FROM biomarker_alerts a
                ORDER BY a.flagged_at DESC;
                """,
                conn
            )
            if not alerts_df.empty:
                st.dataframe(alerts_df, use_container_width=True)
            else:
                st.info("No biomarker alerts currently recorded.")

        with tab2:
            sequences_df = pd.read_sql(
                """
                SELECT 
                    s.sequence_id,
                    s.patient_id,
                    s.sequence_length,
                    ROUND(s.avg_quality_score, 2) AS avg_quality,
                    s.sequence_string,
                    f.feature_shape,
                    f.label AS ml_label
                FROM genomic_sequences s
                LEFT JOIN ml_features f ON s.sequence_id = f.sequence_id
                ORDER BY s.sequence_id DESC;
                """,
                conn
            )
            if not sequences_df.empty:
                st.dataframe(sequences_df, use_container_width=True)
            else:
                st.info("No sequences found in database.")

        with tab3:
            if not sequences_df.empty:
                st.bar_chart(sequences_df.set_index("sequence_id")["avg_quality"])

    except sqlite3.OperationalError as e:
        st.warning(f"Database schema query error: {e}")
    finally:
        conn.close()
else:
    st.info("Database file `outputs/genomic_pipeline.db` not found. Select a file on the sidebar and click **Run Pipeline**.")