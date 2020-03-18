import unittest

import atc_reader
from atc_reader import ATCReader


class TestATCReader(unittest.TestCase):

    def test_nonexistent_file(self):
        reader = ATCReader('nonexistent_file.atc')
        self.assertEqual(reader.status(), atc_reader.NO_FILE)

    def test_loads_valid_file(self):
        reader = ATCReader('atc/test_data/1_lead.atc')
        self.assertEqual(reader.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(reader.atc_version(), 3);
        self.assertEqual(len(reader.get_ecg_samples(1)), 9000)
        self.assertEqual(reader.mains_frequency_hz(), 60)
        self.assertEqual(reader.sample_rate_hz(), 300)
        self.assertTrue(reader.mains_filtered())
        self.assertEqual(reader.num_leads(), 1)
        samples = reader.get_ecg_samples(1)
        self.assertEqual(len(samples), 9000)
        # Check the first few samples for match with expected values.
        self.assertEqual(samples[0], 995)
        self.assertEqual(samples[1], 1055)
        self.assertEqual(samples[2], 1024)
        # Check a few in the middle
        self.assertEqual(samples[543], 130)
        self.assertEqual(samples[3822], -11)
        self.assertEqual(samples[7583], -134)
        # Check last few samples.
        self.assertEqual(samples[8997], -163)
        self.assertEqual(samples[8998], -93)
        self.assertEqual(samples[8999], -179)


if __name__ == '__main__':
    unittest.main()
