import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "outputs/genomic_pipeline.db"

st.set_page_config(
    page_title="Genomic ETL Monitor",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Genomic-ETL Pipeline Monitor")
st.caption("Operational metrics, sequence quality distributions, and clinical biomarker alerts.")

def get_connection():
    return sqlite3.connect(DB_PATH)

try:
    conn = get_connection()

    total_patients = pd.read_sql("SELECT COUNT(*) AS count FROM patients;", conn).iloc[0]["count"]
    total_sequences = pd.read_sql("SELECT COUNT(*) AS count FROM genomic_sequences;", conn).iloc[0]["count"]
    total_alerts = pd.read_sql("SELECT COUNT(*) AS count FROM biomarker_alerts;", conn).iloc[0]["count"]
    avg_quality = pd.read_sql("SELECT AVG(avg_quality_score) AS avg FROM genomic_sequences;", conn).iloc[0]["avg"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingested Patients", int(total_patients))
    col2.metric("Filtered Sequences", int(total_sequences))
    col3.metric("Biomarker Alerts", int(total_alerts))
    col4.metric(
        "Mean Phred Score",
        f"{avg_quality:.2f}" if avg_quality is not None else "0.00"
    )

    st.markdown("---")

 
    st.subheader("⚠️ Detected Biomarker Alerts")
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
        st.info("No biomarker alerts currently recorded in the database.")

    st.markdown("---")

    st.subheader("Ingested Genomic Sequences & Feature Shapes")
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

        st.subheader("📊 Quality Score Distribution (Phred+33)")
        st.bar_chart(sequences_df.set_index("sequence_id")["avg_quality"])
    else:
        st.info("No genomic sequences found.")

    conn.close()

except sqlite3.OperationalError as e:
    st.error(f"Unable to read `{DB_PATH}`: {e}")
    st.warning("Ensure the pipeline has run and created the database: `python3 main.py data/example.fastq`")