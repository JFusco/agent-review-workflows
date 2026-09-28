import unittest
from calculator import average

class AverageTests(unittest.TestCase):
    def test_average(self):
        self.assertEqual(average([2, 4]), 3)

    def test_empty(self):
        with self.assertRaises(ValueError):
            average([])

if __name__ == '__main__':
    unittest.main()
