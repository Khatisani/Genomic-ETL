import unittest
from pipeline.extract import check_validity

class TestExtraction(unittest.TestCase):

    def test_actual_example_file_is_valid(self):
        actual_path = "data/example.fastq"
        
        try:
            check_validity(actual_path)
        except SystemExit:
            self.fail(f"check_validity unexpectedly failed on your real file at: {actual_path}")

if __name__ == "__main__":
    unittest.main()