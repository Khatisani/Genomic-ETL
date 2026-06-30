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

if __name__ == "__main__":
    unittest.main()