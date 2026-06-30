import os
import sys
import subprocess

def main():
    if len(sys.argv) != 2:
        print("Usage Error!")
        print("Usage: python3 main.py <inputfile.fastq>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    staging_file= "data/extracted_stage.tmp"

    print("\n==================================================")
    print("🧬 Starting Genomic-ETL Pipeline Engine 🧬")
    print("==================================================\n")

# --------------------------------------------------
# STAGE 1: EXTRACTION & VALIDATION
# --------------------------------------------------
    
    print("\n--------------------------------------------------")
    print("[STAGE 1] Running Extraction Engine...")
    print("--------------------------------------------------\n")

    extract_proc = subprocess.run(["python3", "pipeline/extract.py", input_file], capture_output=False)
    
    if extract_proc.returncode != 0:
        print("Pipeline failed at Stage 1: Extraction aborted.")
        sys.exit(extract_proc.returncode) 
    print("\n---------------Stage 1 complete.------------------\n")

# --------------------------------------------------
# STAGE 2: QUALITY TRANSFORMATION & FILTERING
# --------------------------------------------------

    print("\n--------------------------------------------------")
    print("[STAGE 2] Running Transformation Engine...")
    print("--------------------------------------------------\n")

    trans_process = subprocess.run(
        ["python3", "pipeline/transform.py", staging_file],
        capture_output=False
    )

    if trans_process.returncode != 0:
        print("\n❌ Pipeline aborted: Stage 2 Transformation failed.")
        sys.exit(trans_process.returncode)

    print("\n---------------Stage 2 complete.------------------\n")

# --------------------------------------------------
# STAGE 3: 
# --------------------------------------------------

    print("\n--------------------------------------------------")
    print("[STAGE 3] Running Loading Engine...")
    print("--------------------------------------------------\n")

    # load_process = subprocess.run(
    #     ["python3", "pipeline/load.py", staging_file],
    #     capture_output=False
    # )

    # if load_process.returncode != 0:
    #     print("\nPipeline aborted: Stage 3 Loading failed.")
    #     sys.exit(load_process.returncode)

    print("\n---------------Stage 3 complete.------------------\n")

    print("\n==================================================")
    print("Genomic-ETL Pipeline Successfully Executed!")
    print("==================================================\n")

if __name__ == "__main__":
    main()