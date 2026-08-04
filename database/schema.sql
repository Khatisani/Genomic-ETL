
-- Table 1: Patient Records
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY
);

-- Table 2: Filtered sequences and Quality metrics
CREATE TABLE IF NOT EXISTS genomic_sequences (
    sequence_id INT PRIMARY KEY,
    patient_id TEXT,
    sequence_string TEXT,
    avg_quality_score REAL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Table 3: Biomarker Detections
CREATE TABLE IF NOT EXISTS biomarker_alerts (
    alert_id INT PRIMARY KEY,
    patient_id TEXT,
    matched_window TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Table 4: Processed ML Features 
CREATE TABLE IF NOT EXISTS ml_features (
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);


