import os
import unittest
from pipeline.extract import check_validity, validate_fastq_structure

class TestExtraction(unittest.TestCase):

    def test_actual_example_file_is_valid(self):
        actual_path = "data/example.fastq"
        
        try:
            check_validity(actual_path)
        except SystemExit:
            self.fail(f"check_validity unexpectedly failed on your real file at: {actual_path}")

    def test_file_does_not_exist(self):
        missing_path = "data/nonexistent.fastq"
        
        try:
            check_validity(missing_path)
            self.fail("check_validity should have exited on a missing file, but it didn't!")
        except SystemExit as error:
            self.assertEqual(error.code, 1)

    def test_invalid_file_extension(self):
        bad_path = "data/example.txt"
        
        with open(bad_path, 'w') as f:
            f.write("This is not genomic data.")
            
        try:
            check_validity(bad_path)
            self.fail("check_validity should have exited on a .txt file, but it didn't!")
        except SystemExit as error:
            self.assertEqual(error.code, 1)
        finally:
            if os.path.exists(bad_path):
                os.remove(bad_path)

    def test_actual_example_structure_is_valid(self):
        actual_path = "data/example.fastq"
        try:
            validate_fastq_structure(actual_path)
        except SystemExit:
            self.fail(f"validate_fastq_structure unexpectedly failed on your real file at: {actual_path}")

    def test_structure_malformed_three_lines_only(self):
        odd_path = "data/malformed_3lines.fastq"
        
        with open(odd_path, 'w') as f:
            f.write("@SRR1234567.1\n")
            f.write("GATT\n")
            f.write("+\n")
            
        try:
            validate_fastq_structure(odd_path)
            self.fail("validate_fastq_structure should have exited on a 3-line file, but it didn't!")
        except SystemExit as error:
            self.assertEqual(error.code, 1)
        finally:
            if os.path.exists(odd_path):
                os.remove(odd_path)

    def test_structure_missing_at_symbol(self):

        bad_path = "data/missing_at.fastq"
        with open(bad_path, 'w') as f:
            f.write("SRR1234567.1\nGATT\n+\nBFFF\n")
            
        try:
            validate_fastq_structure(bad_path)
            self.fail("Should have exited due to missing '@' symbol.")
        except SystemExit as error:
            self.assertEqual(error.code, 1)
        finally:
            if os.path.exists(bad_path): os.remove(bad_path)

    def test_structure_missing_plus_symbol(self):
        bad_path = "data/missing_plus.fastq"
        with open(bad_path, 'w') as f:
            f.write("@SRR1234567.1\nGATT\n=\nBFFF\n")
            
        try:
            validate_fastq_structure(bad_path)
            self.fail("Should have exited due to missing '+' symbol.")
        except SystemExit as error:
            self.assertEqual(error.code, 1)
        finally:
            if os.path.exists(bad_path): os.remove(bad_path)

    def test_structure_length_mismatch(self):
        bad_path = "data/mismatch.fastq"
        with open(bad_path, 'w') as f:
            f.write("@SRR1234567.1\nGATT\n+\nBFF\n")
            
        try:
            validate_fastq_structure(bad_path)
            self.fail("Should have exited due to length mismatch.")
        except SystemExit as error:
            self.assertEqual(error.code, 1)
        finally:
            if os.path.exists(bad_path): os.remove(bad_path)

if __name__ == "__main__":
    unittest.main()