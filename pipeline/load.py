"""
Genomic Data Loading and Vectorization (`load.py`).

Transforms filtered genomic records into machine-learning-ready numerical tensors
and exports JSON files for downstream storage and demo purposes.

Outputs generated:
1. One-hot encoded nucleotide tensors (A, C, G, T -> 4D vectors).
2. Numerical Phred quality score matrices.
3. Binary biomarker risk target labels (1 = positive motif match, 0 = negative).
4. Patient-level database records exported in JSON format.
"""

import sys
import os
import json
import sqlite3
import numpy as np
from pipeline.transform import parse_staged_records, ascii_to_phred, contains_motif, load_biomarkers

def one_hot_encode_seq(sequence):
    """
    Converts a raw DNA sequence string into a list of 4-element one-hot binary vectors.

    Base mapping:
        - 'A': [1, 0, 0, 0]
        - 'C': [0, 1, 0, 0]
        - 'G': [0, 0, 1, 0]
        - 'T': [0, 0, 0, 1]
        - Ambiguous/Unknown ('N', etc.): [0, 0, 0, 0]

    Args:
        sequence (str): Target nucleotide base sequence (case-insensitive).

    Returns:
        List[List[int]]: A list of 4-element binary lists representing one-hot encoded bases.
    """
    
    mapping = {
        'A': [1, 0, 0, 0],
        'C': [0, 1, 0, 0],
        'G': [0, 0, 1, 0],
        'T': [0, 0, 0, 1]
    }
    return [mapping.get(base, [0, 0, 0, 0]) for base in sequence.upper()]

def pad_or_truncate(vector_list, max_len, fill_value=None):
    """
    Standardizes sequence feature representations to a fixed uniform length.

    Truncates vectors exceeding `max_len` or pads shorter vectors using `fill_value`.

    Args:
        vector_list (List[Any]): Input list of feature vectors or scalar values.
        max_len (int): Maximum target sequence length constraint.
        fill_value (Optional[Any], optional): Default padding element. Defaults to [0, 0, 0, 0].

    Returns:
        List[Any]: Fixed-length vector padded or truncated to `max_len`.
    """
    
    if fill_value is None:
        fill_value = [0, 0, 0, 0] 
        
    if len(vector_list) >= max_len:
        return vector_list[:max_len]
    
    padding_needed = max_len - len(vector_list)
    return vector_list + [fill_value] * padding_needed

def compile_ml_dataset(staging_path, biomarker_path, max_len=100):
    """
    Compiles staged FASTQ records into structured multi-dimensional NumPy feature arrays.

    Extracts one-hot encoded base arrays, Phred quality arrays, and binary biomarker labels.

    Args:
        staging_path (str): Path to filtered temporary staging file (`.tmp`).
        biomarker_path (str): Path to FASTA reference file containing risk motifs.
        max_len (int, optional): Fixed sequence length for array padding/truncation. Defaults to 100.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]:
            - X_seq (np.ndarray): One-hot sequence tensor of shape `(N, max_len, 4)` and dtype `float32`.
            - X_qual (np.ndarray): Phred quality score tensor of shape `(N, max_len)` and dtype `float32`.
            - y (np.ndarray): Binary target label matrix of shape `(N, 1)` and dtype `int32`.
    """
    
    biomarkers = load_biomarkers(biomarker_path)
    
    sequences_accumulator = []
    qualities_accumulator = []
    labels_accumulator = []
    
    for header, seq, spacer, qual in parse_staged_records(staging_path):
        numeric_scores = ascii_to_phred(qual)
        
        encoded_seq = one_hot_encode_seq(seq)
        padded_seq = pad_or_truncate(encoded_seq, max_len, fill_value=[0, 0, 0, 0])
        sequences_accumulator.append(padded_seq)
        
        padded_qual = pad_or_truncate(numeric_scores, max_len, fill_value=0)
        qualities_accumulator.append(padded_qual)

        is_positive = 1 if contains_motif(seq, biomarkers) else 0
        labels_accumulator.append([is_positive])
        
    if not sequences_accumulator:
        return (
            np.empty((0, max_len, 4), dtype=np.float32),
            np.empty((0, max_len), dtype=np.float32),
            np.empty((0, 1), dtype=np.int32)
        )
        
    return (
        np.array(sequences_accumulator, dtype=np.float32),
        np.array(qualities_accumulator, dtype=np.float32),
        np.array(labels_accumulator, dtype=np.int32)
    )

def main():
#     """
#     CLI Entry point for Stage 3 Loader and Tensor export.
#     """
    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/load.py <transformed_stage.tmp>")
        sys.exit(1)
        
    staging_file = sys.argv[1]
    biomarker_file = "data/biomarkers.fasta"
    db_path = "outputs/genomic_pipeline.db"
    
    os.makedirs("outputs", exist_ok=True)
    
    print(f"Executing Stage 3 Loader: Writing records into SQLite database '{db_path}'...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    with open("database/schema.sql", "r") as f:
        schema_script = f.read()
    cursor.executescript(schema_script)

    X_seq, X_qual, y = compile_ml_dataset(staging_file, biomarker_file, max_len=100)
    biomarkers = load_biomarkers(biomarker_file)

    record_count = 0
    for idx, (header, seq, spacer, qual) in enumerate(parse_staged_records(staging_file)):
        patient_id = header.split()[0].strip()
        phred_scores = ascii_to_phred(qual)
        avg_quality = float(np.mean(phred_scores)) if phred_scores else 0.0
        
        cursor.execute("INSERT OR IGNORE INTO patients (patient_id) VALUES (?)", (patient_id,))

        record_count += 1
        cursor.execute(
            """
            INSERT INTO genomic_sequences (sequence_id, patient_id, sequence_string, avg_quality_score)
            VALUES (?, ?, ?, ?)
            """,
            (record_count, patient_id, seq.strip(), avg_quality)
        )

        matched_motif = contains_motif(seq, biomarkers)
        if matched_motif:
            cursor.execute(
                """
                INSERT INTO biomarker_alerts (alert_id, patient_id, matched_window)
                VALUES (?, ?, ?)
                """,
                (record_count, patient_id, matched_motif)
            )

        cursor.execute(
            """
            INSERT INTO ml_features (feature_id, patient_id, feature_shape, label)
            VALUES (?, ?, ?, ?)
            """,
            (record_count, patient_id, str(X_seq.shape), int(y[idx][0]))
        )

    conn.commit()
    conn.close()

    print(f"\nStage 3 Summary:")
    print(f"  - Total SQL Records Loaded: {record_count}")
    print(f"  - Features Shape (Sequences): {X_seq.shape}")
    print(f"  - Features Shape (Qualities): {X_qual.shape}")
    print(f"  - Labels Shape:               {y.shape}")
    print(f"\nDatabase successfully updated at '{db_path}'!")

if __name__ == "__main__":
    main()
