import os
import sqlite3

db_path = "outputs/test_pipeline.db"
os.makedirs("outputs", exist_ok=True)

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

with open("database/schema.sql", "r") as f:
    schema_script = f.read()

cursor.executescript(schema_script)
print("Tables created successfully!")

try:
    patient_id = "@SRR1234567.1"
    cursor.execute("INSERT INTO patients (patient_id) VALUES (?)", (patient_id,))

    test_seq = "GCTAGCTAGCATGATT"
    cursor.execute(
        """
        INSERT INTO genomic_sequences (patient_id, sequence_string, sequence_length, avg_quality_score)
        VALUES (?, ?, ?, ?)
        """,
        (patient_id, test_seq, len(test_seq), 39.8),
    )
    sequence_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO biomarker_alerts (sequence_id, patient_id, matched_window)
        VALUES (?, ?, ?)
        """,
        (sequence_id, patient_id, "ATGATT"),
    )

    cursor.execute(
        """
        INSERT INTO ml_features (sequence_id, patient_id, feature_shape, label)
        VALUES (?, ?, ?, ?)
        """,
        (sequence_id, patient_id, "(1, 100, 4)", 1),
    )

    conn.commit()
    print("Dummy relational data inserted successfully!")

    cursor.execute(
        """
        SELECT 
            p.patient_id, 
            g.sequence_string, 
            g.sequence_length, 
            g.avg_quality_score,
            a.matched_window,
            f.label
        FROM patients p
        JOIN genomic_sequences g ON p.patient_id = g.patient_id
        JOIN biomarker_alerts a ON g.sequence_id = a.sequence_id
        JOIN ml_features f ON g.sequence_id = f.sequence_id
        """
    )
    row = cursor.fetchone()

    print("\nQueried Relational Record:")
    print(f"  Patient ID:      {row[0]}")
    print(f"  Sequence:        {row[1]}")
    print(f"  Sequence Length: {row[2]}")
    print(f"  Avg Quality:     {row[3]}")
    print(f"  Biomarker Alert: {row[4]}")
    print(f"  ML Label:        {row[5]}")

except Exception as e:
    print(f"Database error: {e}")
finally:
    conn.close()