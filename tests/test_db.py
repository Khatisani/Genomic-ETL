import sqlite3
import os

db_path = "outputs/test_pipeline.db"
os.makedirs("outputs", exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

with open("database/schema.sql", "r") as f:
    schema_script = f.read()

cursor.executescript(schema_script)
print("Tables created successfully!")

try:
    cursor.execute("INSERT INTO patients (patient_id) VALUES ('@SRR1234567.1')")

    cursor.execute(
        """
        INSERT INTO genomic_sequences (sequence_id, patient_id, sequence_string, avg_quality_score)
        VALUES (1, '@SRR1234567.1', 'GCTAGCTAGCATGATT', 39.8)
        """
    )

    conn.commit()
    print("Dummy data inserted successfully!")

    cursor.execute(
        """
        SELECT p.patient_id, g.sequence_string, g.avg_quality_score 
        FROM patients p
        JOIN genomic_sequences g ON p.patient_id = g.patient_id
        """
    )
    row = cursor.fetchone()
    print("\nQueried Record from SQL:")
    print(f"  Patient ID: {row[0]}")
    print(f"  Sequence:   {row[1]}")
    print(f"  Avg Qual:   {row[2]}")

except Exception as e:
    print(f"Database error: {e}")
finally:
    conn.close()