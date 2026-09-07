
PRAGMA foreign_keys = ON;

-- Table 1: Patient Records
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Filtered sequences and Quality metrics
CREATE TABLE IF NOT EXISTS genomic_sequences (
    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    sequence_string TEXT NOT NULL,
    sequence_length INT NOT NULL,
    avg_quality_score REAL NOT NULL CHECK (avg_quality_score >= 0.0),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Table 3: Biomarker Detections
CREATE TABLE IF NOT EXISTS biomarker_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_id INTEGER NOT NULL,
    patient_id TEXT NOT NULL,
    matched_window TEXT NOT NULL,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sequence_id) REFERENCES genomic_sequences(sequence_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Table 4: Processed ML Features 
CREATE TABLE IF NOT EXISTS ml_features (
    feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_id INTEGER NOT NULL UNIQUE,
    patient_id TEXT NOT NULL,
    feature_shape TEXT NOT NULL,
    label INTEGER NOT NULL CHECK (label IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sequence_id) REFERENCES genomic_sequences(sequence_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);


