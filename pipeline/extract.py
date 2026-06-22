
import os
import sys

def check_validity(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input file path '{input_path}' does not exist.")
    
    if not (input_path.endswith('.fastq') or input_path.endswith('.fq')):
        raise ValueError(f"Invalid file extension. The file '{input_path}' must be a .fastq or .fq file.")
