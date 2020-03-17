import unittest

import atc_reader
from atc_reader import ATCReader


class TestATCReader(unittest.TestCase):

    def test_nonexistent_file(self):
        reader = ATCReader('/tmp/file_does_not_exist.atc')
        self.assertEqual(reader.status(), atc_reader.NO_FILE)

if __name__ == '__main__':
    unittest.main()
