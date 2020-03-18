from datetime import datetime
import io
import os
import tempfile
import unittest

import atc_reader
from atc_reader import ATCReader
from atc_writer import ATCWriter


class TestATCWriter(unittest.TestCase):

    def assertFilesBinaryEqual(self, a, b):
        with open(a, 'rb') as fa:
            a_bytes = bytearray(fa.read())
        with open(b, 'rb') as fb:
            b_bytes = bytearray(fb.read())
        self.assertListEqual(list(a_bytes), list(b_bytes))

    def test_saved_empty_file(self):
        with io.BytesIO() as empty_file:
            writer = ATCWriter(empty_file)
            self.assertTrue(
                writer.write_header(
                    datetime.now(), 'recording uuid', 'phone uuid', 'phone model', 'recorder software',
                    'recorder hardware', 'K=V', {}, 300, 60)
            )
            writer.close()

    def test_saves_single_lead(self):
        reader = ATCReader('atc/test_data/1_lead.atc')
        self.assertEqual(reader.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(reader.num_leads(), 1)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        with ATCWriter(temp_file.name) as writer:
            self.assertTrue(
                writer.write_header(
                    reader.date_recorded(), reader.recording_uuid(), reader.phone_uuid(), reader.phone_model(),
                    reader.recorder_software(), reader.recorder_hardware(), reader.device_data(), reader.flags(),
                    reader.sample_rate_hz(), reader.mains_frequency_hz())
            )
            writer.write_ecg_samples(reader.get_ecg_samples(1), 1)
            offsets, beat_types = reader.get_annotations()
            writer.write_annotations(offsets, beat_types)
        saved_atc_file = ATCReader(temp_file.name)
        self.assertTrue(saved_atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertFilesBinaryEqual(temp_file.name, 'atc/test_data/1_lead.atc')
        os.unlink(temp_file.name)

if __name__ == '__main__':
    unittest.main()
