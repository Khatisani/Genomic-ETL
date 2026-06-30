import unittest
import os
import sys
from pipeline.transform import ascii_to_phred, parse_staged_records

class TestTransform(unittest.TestCase):

    def test_parse_staged_records_with_real_data(self):
        real_stage_file = "data/sample1.fastq.tmp"
        if not os.path.exists(real_stage_file):
            self.skipTest(
                f"Skipping: '{real_stage_file}' not found. "
                f"Run 'python3 extract.py data/sample1.fastq' first to generate it."
            )
            
        records = list(parse_staged_records(real_stage_file))
        self.assertGreater(len(records), 0, f"The staged file '{real_stage_file}' was empty.")

        first_record = records[0]
        self.assertEqual(len(first_record), 4, "Streamed record does not have exactly 4 elements.")
    
        header, sequence, spacer, quality = first_record
        self.assertTrue(header.startswith("@"), "First line must start with standard FASTQ '@' symbol.")
        self.assertEqual(spacer, "+", "Third line must be exactly the '+' spacer marker.")
        self.assertEqual(len(sequence), len(quality), "Sequence string length and quality string length mismatch.")

    def test_parse_staged_records_valid_file(self):
        test_file = "data/test_staging.tmp"
        with open(test_file, 'w') as f:
            f.write("@SRR1234567.1\n")
            f.write("GATTACA\n")
            f.write("+\n")
            f.write("IIIIIII\n")
        
        records = list(parse_staged_records(test_file))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], ("@SRR1234567.1", "GATTACA", "+", "IIIIIII"))
        
        os.remove(test_file)

    def test_parse_staged_records_missing_file(self):
        missing_file = "data/nonexistent.tmp"
        with self.assertRaises(SystemExit) as cm:
            list(parse_staged_records(missing_file))
        self.assertEqual(cm.exception.code, 1)

    def test_parse_staged_records_missing_file(self):
        missing_stage_file = "data/non_existent_stage_file_checkpoint.tmp"
        
        if os.path.exists(missing_stage_file):
            os.remove(missing_stage_file)
        with self.assertRaises(SystemExit) as context:
            next(parse_staged_records(missing_stage_file))
            
        self.assertEqual(context.exception.code, 1, "Parser did not exit with code 1 on a missing file path.")

    def test_parse_staged_records_invalid_extension(self):
        illegal_ext_file = "data/sample1.fastq" 
        with self.assertRaises(SystemExit) as context:
            next(parse_staged_records(illegal_ext_file))
            
        self.assertEqual(context.exception.code, 1, "Parser allowed a non-.tmp file format to propagate.")

    def test_ascii_to_phred_with_real_characters(self):
        self.assertEqual(ascii_to_phred("!"), [0])
        self.assertEqual(ascii_to_phred("I"), [40])
        self.assertEqual(ascii_to_phred("@ABC"), [31, 32, 33, 34])

    def test_ascii_to_phred_empty_string(self):
        self.assertEqual(ascii_to_phred(""), [])

    def test_ascii_to_phred_out_of_bounds(self):
        with self.assertRaises(ValueError):
            ascii_to_phred(" ")

if __name__ == "__main__":
    unittest.main()

