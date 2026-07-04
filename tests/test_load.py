import unittest
from pipeline.load import one_hot_encode_seq, pad_or_truncate

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

if __name__ == "__main__":
    unittest.main()