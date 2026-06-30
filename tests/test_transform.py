from io import StringIO
import unittest
import os
import sys
from pipeline.transform import ascii_to_phred, contains_motif, filter_low_quality, load_biomarkers, main, parse_staged_records

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

    def test_filter_low_quality_pass(self):
        high_quality = [30, 35, 40, 25]
        self.assertTrue(filter_low_quality(high_quality, threshold=20))

    def test_filter_low_quality_drop(self):
        low_quality = [10, 12, 15, 8]
        self.assertFalse(filter_low_quality(low_quality, threshold=20))

    def test_filter_low_quality_exact_boundary(self):
        boundary_quality = [20, 20, 20, 20]
        self.assertTrue(filter_low_quality(boundary_quality, threshold=20))

    def test_filter_low_quality_empty_scores(self):
        self.assertFalse(filter_low_quality([], threshold=20))

    def test_load_biomarkers_success(self):
        real_fasta_path = "data/biomarkers.fasta"
    
        if not os.path.exists(real_fasta_path):
            self.skipTest(f"Skipping: '{real_fasta_path}' not found in data directory.")
            
        motifs = load_biomarkers(real_fasta_path)
    
        self.assertIsInstance(motifs, list, "Function should return a list.")
        self.assertGreater(len(motifs), 0, "Biomarker list should not be empty.")
        
        for motif in motifs:
            self.assertTrue(motif.isupper(), f"Motif '{motif}' was not properly converted to uppercase.")
            self.assertFalse(motif.startswith('>'), f"Header line '{motif}' was incorrectly included in motifs.")

    def test_load_biomarkers_missing_file(self):
        missing_fasta = "data/non_existent_biomarkers_file.fasta"
    
        if os.path.exists(missing_fasta):
            os.remove(missing_fasta)
            
        motifs = load_biomarkers(missing_fasta)
        self.assertEqual(motifs, [], "A missing file should return an empty list.")

    def test_load_biomarkers_with_empty_and_whitespace_lines(self):
        temp_fasta = "data/temp_whitespace_test.fasta"
        with open(temp_fasta, "w") as f:
            f.write(">Sequence_1\nATCG\n\n   \n>Sequence_2\nGCTA\n")
            
        try:
            motifs = load_biomarkers(temp_fasta)
            self.assertEqual(motifs, ["ATCG", "GCTA"], "Failed to strip out empty or whitespace-only lines.")
        finally:
            if os.path.exists(temp_fasta):
                os.remove(temp_fasta)

    def test_load_biomarkers_only_headers(self):
        temp_fasta = "data/temp_headers_only.fasta"
        with open(temp_fasta, "w") as f:
            f.write(">Header1\n>Header2\n>Header3\n")
            
        try:
            motifs = load_biomarkers(temp_fasta)
            self.assertEqual(motifs, [], "Returned data from a file that contained zero sequence lines.")
        finally:
            if os.path.exists(temp_fasta):
                os.remove(temp_fasta)

    def test_contains_motif_success_case_insensitive(self):
        biomarkers = ["AATTGG", "CCGGAA"]
        sequence = "atcaattggctga"
        
        self.assertEqual(contains_motif(sequence, biomarkers), "AATTGG")

    def test_contains_motif_returns_first_match(self):
        biomarkers = ["CCGGAA", "AATTGG"]
        sequence = "AATTGGCCGGAA" 
        
        self.assertEqual(contains_motif(sequence, biomarkers), "CCGGAA")

    def test_contains_motif_no_match(self):
        biomarkers = ["AAAAAA", "CCCCCC"]
        sequence = "GTTTGGCCGGAA"
        
        self.assertIsNone(contains_motif(sequence, biomarkers))

    def test_contains_motif_empty_inputs(self):
        self.assertIsNone(contains_motif("", ["AATT"]), "Empty sequence should return None.")
        self.assertIsNone(contains_motif("AATTGG", []), "Empty biomarker list should return None.")


    def setUp(self):
        self.integration_stage = "data/integration_test_stage.tmp"
        self.real_biomarker_file = "data/biomarkers.fasta"
        self.saved_argv = sys.argv[:] 
        os.makedirs("data", exist_ok=True)

    def tearDown(self):
        sys.argv = self.saved_argv
        if os.path.exists(self.integration_stage):
            os.remove(self.integration_stage)

    def test_main_missing_arguments(self):
        sys.argv = ["transform.py"]
        
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 1)
            self.assertIn("Usage: python3 pipeline/transform.py", captured_stdout.getvalue())
        finally:
            sys.stdout = saved_stdout

    def test_main_metrics_capture(self):
        with open(self.integration_stage, "w") as f:
            f.write("@Patient01 Info\nAAAA\n+\nIIII\n@Patient02 Info\nTTTT\n+\nIIII\n")
            
        sys.argv = ["transform.py", self.integration_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            main()
            output = captured_stdout.getvalue()
            self.assertIn("Total processed: 2", output)
            self.assertIn("Quality Passed:  2", output)
        finally:
            sys.stdout = saved_stdout

    def test_main_triggers_alert(self):
        if not os.path.exists(self.real_biomarker_file) or os.path.getsize(self.real_biomarker_file) == 0:
            self.skipTest("biomarkers.fasta empty or missing.")
            
        with open(self.real_biomarker_file, "r") as f:
            lines = f.readlines()
            real_motif = [line.strip() for line in lines if line.strip() and not line.startswith(">")][0]
        with open(self.integration_stage, "w") as f:
            f.write(f"@PatientTarget\n{real_motif}\n+\n" + ("I" * len(real_motif)) + "\n")

        sys.argv = ["transform.py", self.integration_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            main()
            output = captured_stdout.getvalue()
            self.assertIn("ALERT:", output)
            self.assertIn("Patient ID: @PatientTarget", output)
            self.assertIn("High-Risk Alerts: 1", output)
        finally:
            sys.stdout = saved_stdout

    def test_main_corrupted_header(self):
        if not os.path.exists(self.real_biomarker_file) or os.path.getsize(self.real_biomarker_file) == 0:
            self.skipTest("biomarkers.fasta empty or missing.")
            
        with open(self.real_biomarker_file, "r") as f:
            lines = f.readlines()
            real_motif = [line.strip() for line in lines if line.strip() and not line.startswith(">")][0]
        with open(self.integration_stage, "w") as f:
            f.write(f"@Patient99_NoSpaces|Metadata_Details\n{real_motif}\n+\n" + ("I" * len(real_motif)) + "\n")

        sys.argv = ["transform.py", self.integration_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            main()
            self.assertIn("Patient ID: @Patient99_NoSpaces|Metadata_Details", captured_stdout.getvalue())
        finally:
            sys.stdout = saved_stdout

    def test_main_rejected_record(self):
        with open(self.integration_stage, "w") as f:
            f.write("@PatientLowQual\nATCG\n+\n!!!!\n")  

        sys.argv = ["transform.py", self.integration_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            main()
            output = captured_stdout.getvalue()
            self.assertIn("REJECTED due to low quality parameters.", output)
            self.assertIn("Quality Passed:  0", output)
        finally:
            sys.stdout = saved_stdout

    def test_main_empty_staging_file(self):
        with open(self.integration_stage, "w") as f:
            f.write("")

        sys.argv = ["transform.py", self.integration_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        
        try:
            sys.stdout = captured_stdout
            main()
            output = captured_stdout.getvalue()
            self.assertIn("Total processed: 0", output)
            self.assertIn("Quality Passed:  0", output)
        finally:
            sys.stdout = saved_stdout


if __name__ == "__main__":
    unittest.main()

