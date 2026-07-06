import os
import sys
import unittest
import numpy as np
from io import StringIO
from pipeline.load import one_hot_encode_seq, pad_or_truncate, compile_ml_dataset, main

class TestLoadPipeline(unittest.TestCase):

    def test_one_hot_encode_seq_valid(self):
        self.assertEqual(one_hot_encode_seq("A"), [[1, 0, 0, 0]])
        self.assertEqual(one_hot_encode_seq("C"), [[0, 1, 0, 0]])
        self.assertEqual(one_hot_encode_seq("G"), [[0, 0, 1, 0]])
        self.assertEqual(one_hot_encode_seq("T"), [[0, 0, 0, 1]])
        
    def test_one_hot_encode_seq_unknowns(self):
        self.assertEqual(one_hot_encode_seq("N"), [[0, 0, 0, 0]])

    def test_one_hot_encode_seq_mixed_case(self):
        self.assertEqual(one_hot_encode_seq("a"), [[1, 0, 0, 0]])
        self.assertEqual(one_hot_encode_seq("aCtG"), [
            [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]
        ])

    def test_one_hot_encode_seq_all_unknowns(self):
        self.assertEqual(one_hot_encode_seq("NNN"), [
            [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
        ])

    def test_one_hot_encode_seq_empty(self):
        self.assertEqual(one_hot_encode_seq(""), [])

    def test_one_hot_encode_seq_with_digits(self):
        self.assertEqual(one_hot_encode_seq("A5T"), [
            [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]
        ])

    def test_one_hot_encode_seq_with_whitespace(self):
        self.assertEqual(one_hot_encode_seq("A T"), [
            [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]
        ])

    def test_pad_or_truncate_padding(self):
        short_seq = [[1, 0, 0, 0]]
        padded = pad_or_truncate(short_seq, max_len=3, fill_value=[0, 0, 0, 0])
        
        self.assertEqual(len(padded), 3)
        self.assertEqual(padded, [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

    def test_pad_or_truncate_truncation(self):
        long_seq = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]] 
        truncated = pad_or_truncate(long_seq, max_len=2)
        
        self.assertEqual(len(truncated), 2)
        self.assertEqual(truncated, [[1, 0, 0, 0], [0, 1, 0, 0]])

    def test_pad_or_truncate_exact_match(self):
        exact_vectors = [[1, 0, 0, 0], [0, 1, 0, 0]]
        self.assertEqual(pad_or_truncate(exact_vectors, max_len=2), exact_vectors)

    def test_pad_or_truncate_to_zero_length(self):
        vectors = [[1, 0, 0, 0], [0, 1, 0, 0]]
        self.assertEqual(pad_or_truncate(vectors, max_len=0), [])

    def test_pad_or_truncate_empty_input_padding(self):
        padded = pad_or_truncate([], max_len=2)
        self.assertEqual(padded, [[0, 0, 0, 0], [0, 0, 0, 0]])

    def test_pad_or_truncate_custom_fill_value(self):
        short_qual_scores = [35, 40]
        padded = pad_or_truncate(short_qual_scores, max_len=4, fill_value=[-1])
        self.assertEqual(padded, [35, 40, [-1], [-1]])

    def test_pad_or_truncate_large_truncation(self):
        long_vectors = [[1], [2], [3], [4], [5]]
        self.assertEqual(pad_or_truncate(long_vectors, max_len=1), [[1]])

    def test_pad_or_truncate_negative_max_len(self):
        vectors = [[1, 0, 0, 0]]
        self.assertEqual(pad_or_truncate(vectors, max_len=-5), [])

    def test_pad_or_truncate_fill_value_none_fallback(self):
        short_vectors = [[1, 1, 1, 1]]
        padded = pad_or_truncate(short_vectors, max_len=2, fill_value=None)
        self.assertEqual(padded, [[1, 1, 1, 1], [0, 0, 0, 0]])

class TestLoadIntegration(unittest.TestCase):

    def setUp(self):
        self.test_stage = "data/load_test_stage.tmp"
        self.test_biomarkers = "data/load_test_biomarkers.fasta"
        self.output_features = "data/processed_features.npy"
        self.output_labels = "data/processed_labels.npy"
        self.saved_argv = sys.argv[:]
        
        os.makedirs("data", exist_ok=True)
        
        with open(self.test_stage, "w") as f:
            f.write("@PatientA\nATCG\n+\nIIII\n@PatientB\nGGCC\n+\n!!!!\n")
            
        with open(self.test_biomarkers, "w") as f:
            f.write(">RiskMotif\nATCG\n")

    def tearDown(self):
        sys.argv = self.saved_argv
        for path in [self.test_stage, self.test_biomarkers, self.output_features, self.output_labels]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    pass

    def test_compile_ml_dataset_shapes_and_labels(self):
        max_len = 10
        X_seq, X_qual, y = compile_ml_dataset(self.test_stage, self.test_biomarkers, max_len=max_len)
        self.assertEqual(X_seq.shape, (2, max_len, 4))
        self.assertEqual(X_qual.shape, (2, max_len))
        self.assertEqual(y.shape, (2, 1))
        self.assertEqual(y[0][0], 1)
        self.assertEqual(y[1][0], 0)

    def test_compile_ml_dataset_data_types(self):
        X_seq, X_qual, y = compile_ml_dataset(self.test_stage, self.test_biomarkers, max_len=15)
        self.assertEqual(X_seq.dtype, np.float32)
        self.assertEqual(X_qual.dtype, np.float32)
        self.assertEqual(y.dtype, np.int32)

    def test_compile_ml_dataset_empty_source(self):
        empty_stage = "data/empty_load_test_stage.tmp"
        with open(empty_stage, "w") as f:
            f.write("")
        try:
            X_seq, X_qual, y = compile_ml_dataset(empty_stage, self.test_biomarkers, max_len=20)
            self.assertEqual(X_seq.shape, (0, 20, 4))
            self.assertEqual(X_qual.shape, (0, 20))
            self.assertEqual(y.shape, (0, 1))
        finally:
            if os.path.exists(empty_stage):
                os.remove(empty_stage)

    def test_compile_ml_dataset_truncation_gate(self):
        trunc_stage = "data/trunc_test_stage.tmp"
        with open(trunc_stage, "w") as f:
            f.write("@PatientLongRead\nATCGATCGATCG\n+\nIIIIIIIIIIII\n")
        try:
            X_seq, X_qual, y = compile_ml_dataset(trunc_stage, self.test_biomarkers, max_len=5)
            self.assertEqual(X_seq.shape, (1, 5, 4))
            self.assertEqual(X_qual.shape, (1, 5))
        finally:
            if os.path.exists(trunc_stage):
                os.remove(trunc_stage)

    def test_compile_ml_dataset_no_biomarker_file(self):
        empty_biomarkers = "data/empty_biomarkers.fasta"
        with open(empty_biomarkers, "w") as f:
            f.write("")
        try:
            X_seq, X_qual, y = compile_ml_dataset(self.test_stage, empty_biomarkers, max_len=10)
            self.assertEqual(y[0][0], 0)
            self.assertEqual(y[1][0], 0)
        finally:
            if os.path.exists(empty_biomarkers):
                os.remove(empty_biomarkers)

    def test_main_missing_arguments(self):
        sys.argv = ["load.py"]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        try:
            sys.stdout = captured_stdout
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 1)
            self.assertIn("Usage: python3 pipeline/load.py", captured_stdout.getvalue())
        finally:
            sys.stdout = saved_stdout

    def test_main_tensor_generation_and_shapes(self):
        sys.argv = ["load.py", self.test_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        try:
            sys.stdout = captured_stdout
            main()
            self.assertTrue(os.path.exists(self.output_features))
            self.assertTrue(os.path.exists(self.output_labels))
            
            features_dict = np.load(self.output_features, allow_pickle=True).item()
            labels_matrix = np.load(self.output_labels)
            
            self.assertEqual(features_dict["sequences"].shape, (2, 100, 4))
            self.assertEqual(features_dict["qualities"].shape, (2, 100))
            self.assertEqual(labels_matrix.shape, (2, 1))
        finally:
            sys.stdout = saved_stdout

    def test_main_empty_staging_file_behavior(self):
        empty_stage = "data/empty_main_stage.tmp"
        with open(empty_stage, "w") as f:
            f.write("")
        sys.argv = ["load.py", empty_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        try:
            sys.stdout = captured_stdout
            main()
            features_dict = np.load(self.output_features, allow_pickle=True).item()
            labels_matrix = np.load(self.output_labels)
            self.assertEqual(features_dict["sequences"].shape[0], 0)
            self.assertEqual(labels_matrix.shape[0], 0)
        finally:
            sys.stdout = saved_stdout
            if os.path.exists(empty_stage):
                os.remove(empty_stage)

    def test_main_handles_variable_length_reads(self):
        var_stage = "data/var_main_stage.tmp"
        with open(var_stage, "w") as f:
            f.write("@PatientShort\nATCG\n+\nIIII\n@PatientLong\nATCGATCG\n+\nIIIIIIII\n")
        sys.argv = ["load.py", var_stage]
        captured_stdout = StringIO()
        saved_stdout = sys.stdout
        try:
            sys.stdout = captured_stdout
            main()
            features_dict = np.load(self.output_features, allow_pickle=True).item()
            self.assertEqual(features_dict["sequences"].shape, (2, 100, 4))
            self.assertEqual(features_dict["qualities"].shape, (2, 100))
        finally:
            sys.stdout = saved_stdout
            if os.path.exists(var_stage):
                os.remove(var_stage)


if __name__ == "__main__":
    unittest.main()