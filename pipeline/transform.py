"""
Genomic Data Transformation (`transform.py`).

Applies quality control (QC) filtering and motif scanning to staged FASTQ records.

This module converts ASCII quality scores to standard Phred scale integers (Phred+33),
filters sequences failing mean quality thresholds (Q20 standard), and scans passing
reads against target pharmacogenomic/biomarker motifs loaded from FASTA reference files.
"""

import os
import sys

def parse_staged_records(staging_path):
    """
    Streams 4-line FASTQ record tuples from a temporary staging file.
    Reads the raw staging file line-by-line.

    Args:
        staging_path (str): Path to the `.tmp` staging file.

    Yields:
        Generator[Tuple[str, str, str, str], None, None]: A tuple containing the 4 record fields:
            - header (str): Sequence header line (starts with '@').
            - sequence (str): Raw nucleotide base string.
            - spacer (str): Record separator line (starts with '+').
            - quality (str): ASCII Phred quality score string.

    Raises:
        SystemExit: If the file lacks a `.tmp` extension or does not exist. 
    """

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
    """
    Converts a standard Sanger ASCII quality string to Phred integer quality scores (Phred+33).

    Calculates error probability scores by shifting ASCII character ordinals by -33 offset.

    Args:
        quality_string (str): ASCII representation of read quality scores.

    Returns:
        List[int]: A list of integer Phred quality scores corresponding to each base call.

    Raises:
        ValueError: If an illegal ASCII character yields a Phred score below 0.
    """
    
    scores = []
    for char in quality_string:
        score = ord(char) - 33
        if score < 0:
            raise ValueError(f"Illegal character '{char}' detected. Resulting Phred score {score} is below 0.")
        scores.append(score)
    return scores

def filter_low_quality(phred_scores, threshold=20):
    """
    Evaluates whether a read passes a mean Phred quality score threshold.

    Default threshold of Q20 corresponds to a 99% accuracy rate across the read.

    Args:
        phred_scores (List[int]): List of integer Phred quality scores for a read sequence.
        threshold (float, optional): Minimum required mean Phred score. Defaults to 20.0.

    Returns:
        bool: True if the read's average Phred score meets or exceeds the threshold; False otherwise.
    """
    
    if not phred_scores:
        return False
        
    average_score = sum(phred_scores) / len(phred_scores)
    return average_score >= threshold

def load_biomarkers(fasta_path):
    """
    Parses target biological sequence motifs from a reference FASTA file.

    Extracts non-header sequence lines and normalizes base strings to uppercase.

    Args:
        fasta_path (str): Path to the target reference FASTA file containing risk motifs.

    Returns:
        List[str]: A list of uppercase target nucleotide sequence motifs. Returns an empty
            list if the file does not exist.
    """
    
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
    """
    Scans a nucleotide sequence for the presence of target biological motifs.

    Performs substring searching against a provided reference set.

    Args:
        sequence (str): Target DNA sequence to scan.
        biomarkers (List[str]): List of reference motif sequences to detect.

    Returns:
        Optional[str]: The first matched biomarker sequence string, or None if no match is found.
    """
    
    seq_upper = sequence.upper()
    for motif in biomarkers:
        if motif in seq_upper:
            return motif
    return None


def main():
    """
    CLI Entry point for running Stage 2 Quality Control and Biomarker Scanning.
    """
    
    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/transform.py <staging_file.tmp>")
        sys.exit(1)
        
    staging_file = sys.argv[1]
    biomarker_file = "data/biomarkers.fasta"
    output_file = "outputs/filtered_stage.tmp" 
    print(f"Starting Stage 2 transformation on: {staging_file}")
    
    biomarkers = load_biomarkers(biomarker_file)
    print(f"Loaded {len(biomarkers)} pharmacogenomic risk motifs for scanning.\n")

    passed_records = 0
    total_records = 0
    flagged_records = 0

    with open(output_file, "w") as out_f:
        for header, seq, spacer, qual in parse_staged_records(staging_file):
            total_records += 1
            
            numeric_scores = ascii_to_phred(qual)

            if filter_low_quality(numeric_scores, threshold=20):
                passed_records += 1
                print(f"\nRecord {total_records} PASSED (Avg Q: {sum(numeric_scores)/len(numeric_scores):.1f})")
                print(f"   Sequence: {seq}")
                
                out_f.write(f"{header}\n{seq}\n{spacer}\n{qual}\n")
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
    print(f"  - Filtered output saved to: {output_file}") 

if __name__ == "__main__":
    main()
