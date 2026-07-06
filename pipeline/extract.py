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
            print("Error: The provided FASTQ file is completely empty.")
            sys.exit(1)
        if any(not line for line in lines):
            print("Error: FASTQ file is malformed. Incomplete initial 4-line record block.")
            sys.exit(1)
        
        if not lines[0].startswith('@'):
            print(f" Format Error: Line 1 must begin with '@'. Found: '{lines[0][0]}'")
            sys.exit(1)
        if not lines[2].startswith('+'):
            print(f"Format Error: Line 3 must begin with '+'. Found: '{lines[2][0]}'")
            sys.exit(1)
        if len(lines[1]) != len(lines[3]):
            print(f"Format Error: Sequence length ({len(lines[1])}) mismatch with Quality string length ({len(lines[3])}).")
            sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 extract.py <filename.fastq>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_staging_file = "outputs/extracted_stage.tmp"
    
    check_validity(input_file)
    validate_fastq_structure(input_file)
    
    print(f"File check passed for: {input_file}")
    print("Extracting raw sequences...")
    
    os.makedirs("outputs", exist_ok=True)
    
    total_records = 0
    
    with open(input_file, 'r') as infile, open(output_staging_file, 'w') as outfile:
        while True:
            line1 = infile.readline()
            if not line1:
                break
                
            line2 = infile.readline()
            line3 = infile.readline()
            line4 = infile.readline()
            
            outfile.write(f"{line1}{line2}{line3}{line4}")
            total_records += 1
            
    print(f"Extraction Complete.")
    print(f"Staged {total_records} raw records in '{output_staging_file}'")

if __name__ == "__main__":
    main()
