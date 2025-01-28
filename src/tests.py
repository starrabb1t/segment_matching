import unittest
from match import match_groups

class TestMatchFunction(unittest.TestCase):

    def test_1(self):

        G1 = {
            'A': (1, 4),
            'B': (6, 11),
            'C': (2, 11)
        }

        G2 = {
            'D': (2, 8),
            'E': (8, 11),
            'F': (1, 4),
            'G': (6, 11)
        }

        expected_result = {
            'A': ['F'], 
            'B': ['G'], 
            'C': ['D', 'E']
        }

        _, result = match_groups(G1, G2)

        self.assertEqual(result, expected_result)

    def test_2(self):

        G1 = {
            'A': (1, 4),
            'B': (6, 11),
            'C': (2, 11)
        }

        G2 = {
            'D': (3, 7),
            'E': (8, 11),
            'F': (1, 2),
            'G': (6, 10)
        }

        expected_result = {
            'A': ['F'], 
            'B': ['G'], 
            'C': ['D', 'E']
        }

        _, result = match_groups(G1, G2)

        self.assertEqual(result, expected_result)

    def test_3(self):

        G1 = {
            'A': (1, 4),
            'B': (6, 11)
        }

        G2 = {
            'C': (3, 7),
            'D': (8, 11),
            'E': (1, 2),
            'F': (6, 10)
        }

        expected_result = {
            'A': ['C', 'E'], 
            'B': ['F']
        }

        _, result = match_groups(G1, G2)

        self.assertEqual(result, expected_result)

    def test_4(self):

        G1 = {
            'A': (2, 11)
        }

        G2 = {
            'B': (3, 7),
            'C': (8, 11),
            'D': (1, 2),
            'E': (6, 10)
        }

        expected_result = {
            'A': ['B','C']
        }

        _, result = match_groups(G1, G2)

        self.assertEqual(result, expected_result)

    def test_5(self):

        G1 = {
            'A': (2, 11)
        }

        G2 = {
            'B': (1, 2),
            'C': (2, 3),
            'D': (4, 6),
            'E': (7, 10)
        }

        expected_result = {
            'A': ['C','D','E']
        }

        _, result = match_groups(G1, G2)

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()