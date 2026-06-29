import os
import sys
import subprocess

def main():
    if len(sys.argv) != 3:
        print("Usage Error!")
        print("Usage: python3 main.py <inputfile.fastq> <outputfile.npy>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    extracted_stage = "data/extracted_stage.tmp"
    
    print("==================================================")
    print("Starting Genomic-ETL Pipeline Engine 🧬")
    print("==================================================")
  
    print("\n[STEP 1/3] Launching Extraction ...")
    extract_proc = subprocess.run(["python3", "extract.py", input_file])
    
    if extract_proc.returncode != 0:
        print("Pipeline failed at Stage 1: Extraction aborted.")
        sys.exit(1)
        
    print("\n==================================================")
    print("🎉 Genomic-ETL Pipeline Successfully Executed!")
    print("==================================================\n")

if __name__ == "__main__":
    main()