import os
import unittest
from pipeline.extract import check_validity

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

if __name__ == "__main__":
    unittest.main()