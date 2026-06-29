
import os
import sys

def check_validity(input_path):
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        sys.exit(1)
    
    if not (input_path.endswith('.fastq') or input_path.endswith('.fq')):
        print(f"Error: Invalid extension. '{input_path}' must be a .fastq or .fq file.")
        sys.exit(1)



def validate_fastq_structure(input_path):
    with open(input_path, 'r') as f:
        lines = [f.readline().strip() for _ in range(4)]
        
        if not lines[0]:
            raise ValueError("The FASTQ file is empty.")
        if any(not line for line in lines):
            raise ValueError("The FASTQ file is malformed.")
        
        if not lines[0].startswith('@'):
            raise ValueError(f"FASTQ Format Error: Line 1 must begin with '@'. Found: '{lines[0][0]}'")
        if not lines[2].startswith('+'):
            raise ValueError(f"FASTQ Format Error: Line 3 must begin with '+'. Found: '{lines[2][0]}'")
        if len(lines[1]) != len(lines[3]):
            raise ValueError(
                f"FASTQ Format Error: Sequence length ({len(lines[1])}) does not match "
                f"Phred Quality Score string length ({len(lines[3])}) in the first record." )

def calculate_average_phred(quality_string):
    total_score = sum(ord(char) - 33 for char in quality_string)
    return total_score / len(quality_string)

def run_extraction(input_path, output_path, min_q):
    check_file_validity(input_path)
    validate_fastq_structure(input_path)
    
    print("File validation passed. Proceeding with quality filtering...")
    
    reads_processed = 0
    reads_retained = 0
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        while True:
            line1 = infile.readline().strip()
            
            if not line1:
                break 
            line2 = infile.readline().strip()
            line3 = infile.readline().strip()
            line4 = infile.readline().strip()
            
            reads_processed += 1
            
            if 'N' in line2:
                continue
                
            avg_q = calculate_average_phred(line4)
            
            if avg_q < min_q:
                continue
            
            fasta_header = f">{line1[1:]}"
            
            outfile.write(f"{fasta_header}\n{line2}\n")
            
            reads_retained += 1

    print(f"Extraction Metrics: ")
    print(f"   - Total Reads Ingested: {reads_processed}")
    print(f"   - Total Reads Retained: {reads_retained} (Drop Rate: {((reads_processed - reads_retained)/reads_processed)*100:.2f}%)")
            
