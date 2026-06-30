
import os
import sys

def parse_staged_records(staging_path):
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/transform.py <staging_file.tmp>")
        sys.exit(1)
        
    staging_file = sys.argv[1]
    print(f"Starting Stage 2 transformation on: {staging_file}")
    
    passed_records = 0
    total_records = 0
    
    for header, seq, spacer, qual in parse_staged_records(staging_file):
        total_records += 1
        
        numeric_scores = ascii_to_phred(qual)

        if filter_low_quality(numeric_scores, threshold=20):
            passed_records += 1
            print(f"Record {total_records} PASSED (Avg Q: {sum(numeric_scores)/len(numeric_scores):.1f})")
            print(f"   Sequence: {seq}")
        else:
            print(f"Record {total_records} REJECTED due to low quality parameters.")
            
    print(f"\nTransformation complete. Retained {passed_records}/{total_records} high-quality sequences.")
    
if __name__ == "__main__":
    main()