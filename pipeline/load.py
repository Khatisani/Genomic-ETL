
import sys
import os
from flask import json
import numpy as np
from pipeline.transform import parse_staged_records, ascii_to_phred, contains_motif, load_biomarkers


def one_hot_encode_seq(sequence):
    mapping = {
        'A': [1, 0, 0, 0],
        'C': [0, 1, 0, 0],
        'G': [0, 0, 1, 0],
        'T': [0, 0, 0, 1]
    }
    return [mapping.get(base, [0, 0, 0, 0]) for base in sequence.upper()]

def pad_or_truncate(vector_list, max_len, fill_value=None):
    if fill_value is None:
        fill_value = [0, 0, 0, 0] 
        
    if len(vector_list) >= max_len:
        return vector_list[:max_len]
    
    padding_needed = max_len - len(vector_list)
    return vector_list + [fill_value] * padding_needed

def compile_ml_dataset(staging_path, biomarker_path, max_len=100):
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
    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/load.py <transformed_stage.tmp>")
        sys.exit(1)
        
    staging_file = sys.argv[1]
    biomarker_file = "data/biomarkers.fasta"
    
    # Core Production Binary Targets
    output_features_path = "outputs/processed_features.npy"
    output_labels_path = "outputs/processed_labels.npy"
    
    # Demo/Presentation JSON Targets
    output_db_json = "outputs/processed_database.json"
    output_features_json = "outputs/processed_features.json"
    output_labels_json = "outputs/processed_labels.json"
    
    os.makedirs("outputs", exist_ok=True)
    
    print(f"Executing Stage 3 Loader: Compiling tensors from {staging_file}...")
    
    # 1. Compile high-performance ML tensor binary matrices
    X_seq, X_qual, y = compile_ml_dataset(staging_file, biomarker_file, max_len=100)
    np.save(output_features_path, {"sequences": X_seq, "qualities": X_qual})
    np.save(output_labels_path, y)
    
    # ==========================================
    # DEMO EXPORTERS: Plain-Text JSON Files
    # ==========================================
    
    # A. Save the Features Matrix as a JSON (converting numpy arrays to standard nested python lists)
    features_json_payload = {
        "sequences_one_hot_tensors": X_seq.tolist(),
        "qualities_phred_tensors": X_qual.tolist()
    }
    with open(output_features_json, "w") as fj:
        json.dump(features_json_payload, fj, indent=2) # Using 2 spaces to keep it clean but compact
        
    # B. Save the Labels Column as a plain JSON array
    with open(output_labels_json, "w") as lj:
        json.dump(y.tolist(), lj, indent=2)

    # C. Build the human-readable Master Plain English database record log
    biomarkers = load_biomarkers(biomarker_file)
    demo_database_records = []
    
    for header, seq, spacer, qual in parse_staged_records(staging_file):
        has_risk = contains_motif(seq, biomarkers)
        
        record = {
            "patient_id": header.lstrip("@").strip(),
            "sequence_string": seq.strip(),
            "biomarker_risk_detected": "POSITIVE" if has_risk else "NEGATIVE",
            "quality_score_average": float(np.mean(ascii_to_phred(qual))) if qual else 0.0
        }
        demo_database_records.append(record)
        
    with open(output_db_json, "w") as json_file:
        json.dump(demo_database_records, json_file, indent=4)
    
    print("\n📦 Loading and Vectorization Summary:")
    print(f"  - Features Shape (Sequences): {X_seq.shape}")
    print(f"  - Features Shape (Qualities): {X_qual.shape}")
    print(f"  - Labels Shape:               {y.shape}")
    print(f"\n✨ Demo Presentation Files Generated inside 'outputs/':")
    print(f"  - {output_features_json} (Raw Numbers / One-Hot Tensors)")
    print(f"  - {output_labels_json} (Target 1s and 0s)")
    print(f"  - {output_db_json} (Patient History Logs)")
    print("Successfully exported all production and presentation data assets!")


if __name__ == "__main__":
    main()

