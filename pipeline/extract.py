
import os
import sys

def check_validity(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input file path '{input_path}' does not exist.")
    
    if not (input_path.endswith('.fastq') or input_path.endswith('.fq')):
        raise ValueError(f"Invalid file extension. The file '{input_path}' must be a .fastq or .fq file.")

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
            
