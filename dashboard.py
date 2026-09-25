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

st.title("Genomic-ETL Clinical & Ingestion Monitor")
st.caption("End-to-end pipeline execution, FASTQ file ingestion, biomarker surveillance, and ad-hoc sequence testing.")

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