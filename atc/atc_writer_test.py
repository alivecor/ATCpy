from datetime import datetime
import io
import unittest

from atc_writer import ATCWriter


class TestATCWriter(unittest.TestCase):

    def test_saved_empty_file(self):
        with io.BytesIO() as empty_file:
            writer = ATCWriter(empty_file)
            self.assertTrue(
                writer.write_header(
                    datetime.now(), 'recording uuid', 'phone uuid', 'phone model', 'recorder software',
                    'recorder hardware', 'K=V', 0, 300, 60)
            )
            writer.close()


if __name__ == '__main__':
    unittest.main()
