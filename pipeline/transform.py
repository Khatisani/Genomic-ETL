
import os
import sys

def parse_staged_records(staging_path):
    
    if not staging_path.lower().endswith('.tmp'):
        print(f"Error: Invalid file format '{staging_path}'. Expected a staged '.tmp' file.")
        sys.exit(1)

    if not os.path.exists(staging_path):
        print(f"Error: Staging file '{staging_path}' not found.")
        print("Make sure you are running from the project root or passing the correct path.")
        sys.exit(1)
        
    with open(staging_path, 'r') as f:
        while True:
            line1 = f.readline()
            if not line1:
                break
                
            line2 = f.readline()
            line3 = f.readline()
            line4 = f.readline()
            
            yield (line1.strip(), line2.strip(), line3.strip(), line4.strip())

def ascii_to_phred(quality_string):
    return [ord(char) - 33 for char in quality_string]

def filter_low_quality(phred_scores, threshold=20):
    if not phred_scores:
        return False
        
    average_score = sum(phred_scores) / len(phred_scores)
    return average_score >= threshold

def load_biomarkers(fasta_path):
    motifs = []
    if not os.path.exists(fasta_path):
        return motifs

    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('>'):
                motifs.append(line.upper())
    return motifs


def contains_motif(sequence, biomarkers):
    seq_upper = sequence.upper()
    for motif in biomarkers:
        if motif in seq_upper:
            return motif
    return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/transform.py <staging_file.tmp>")
        sys.exit(1)
        
    staging_file = sys.argv[1]
    biomarker_file = "data/biomarkers.fasta"
    print(f"Starting Stage 2 transformation on: {staging_file}")
    
    biomarkers = load_biomarkers(biomarker_file)
    print(f"Loaded {len(biomarkers)} pharmacogenomic risk motifs for scanning.\n")

    passed_records = 0
    total_records = 0
    flagged_records = 0

    for header, seq, spacer, qual in parse_staged_records(staging_file):
        total_records += 1
        
        numeric_scores = ascii_to_phred(qual)

        if filter_low_quality(numeric_scores, threshold=20):
            passed_records += 1
            print(f"\nRecord {total_records} PASSED (Avg Q: {sum(numeric_scores)/len(numeric_scores):.1f})")
            print(f"   Sequence: {seq}")
        else:
            print(f"\nRecord {total_records} REJECTED due to low quality parameters.")
            
        matched_motif = contains_motif(seq, biomarkers)
        if matched_motif:
            flagged_records += 1
            print(f"\n   ALERT: Record {total_records} PASSED Quality, but MATCHED biomarker!")
            print(f"   Patient ID: {header.split()[0]}")
            print(f"   Matched Sequence Window: {matched_motif[:15]}...")
        else:
            print(f"\nRecord {total_records}: Passed Quality and cleared of known risk variables.")
            

    print(f"\nTransformation Phase Finished Summary:\n")
    print(f"  - Total processed: {total_records}")
    print(f"  - Retained: {passed_records}/{total_records} high-quality sequences.")
    print(f"  - Quality Passed:  {passed_records}")
    print(f"  - High-Risk Alerts: {flagged_records}")
    print(f"==================================================")


if __name__ == "__main__":
    main()