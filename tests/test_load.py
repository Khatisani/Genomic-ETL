import unittest
from pipeline.load import one_hot_encode_seq

class TestLoadPipeline(unittest.TestCase):

    def test_one_hot_encode_seq_valid(self):
        self.assertEqual(one_hot_encode_seq("A"), [[1, 0, 0, 0]])
        self.assertEqual(one_hot_encode_seq("C"), [[0, 1, 0, 0]])
        self.assertEqual(one_hot_encode_seq("G"), [[0, 0, 1, 0]])
        self.assertEqual(one_hot_encode_seq("T"), [[0, 0, 0, 1]])
        
    def test_one_hot_encode_seq_unknowns(self):
        self.assertEqual(one_hot_encode_seq("N"), [[0, 0, 0, 0]])