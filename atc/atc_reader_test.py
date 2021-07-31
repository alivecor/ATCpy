import io
import os
import tempfile
import unittest

from atc import atc_header
from atc import atc_reader
from atc.atc_reader import ATCReader
from atc.atc_writer import ATCWriter


class TestATCReader(unittest.TestCase):

    def assertFilesBinaryEqual(self, a, b):
        with open(a, 'rb') as fa:
            a_bytes = bytearray(fa.read())
        with open(b, 'rb') as fb:
            b_bytes = bytearray(fb.read())
        b_bytes[8] = atc_header.ATC_VERSION  # Ignore version of original file for comparison.
        # for i, (a,b) in enumerate(zip(a_bytes, b_bytes)):
        #     if a != b:
        #         print('Bytes at %d not equal: %d != %d' % (i, a ,b))
        self.assertListEqual(list(a_bytes), list(b_bytes))

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

    def test_detects_broken_signature(self):
        with open('atc/test_data/1_lead.atc', 'rb') as f:
            atc_bytes = bytearray(f.read())
        atc_bytes[3] = 99  # Change one byte to break file signature
        with io.BytesIO(bytes(atc_bytes)) as f:
            atc_file = ATCReader(f)
        self.assertEqual(atc_file.status(), atc_reader.NO_ATC_SIGNATURE)

    def test_missing_format_block(self):
        format_block_start = 288
        format_block_end = 308
        with open('atc/test_data/1_lead.atc', 'rb') as f:
            atc_bytes = bytearray(f.read())
        modified_bytes = atc_bytes[:format_block_start] + atc_bytes[format_block_end:]
        with io.BytesIO(bytes(modified_bytes)) as f:
            atc_file = ATCReader(f)
        self.assertEqual(atc_file.status(), atc_reader.MISSING_DATA)

    def test_verifies_format_block_checksum(self):
        with open('atc/test_data/1_lead.atc', 'rb') as f:
            atc_bytes = bytearray(f.read())
        atc_bytes[296] = 0;  # Format block of this file starts at byte 288
        with io.BytesIO(bytes(atc_bytes)) as f:
            atc_file = ATCReader(f)
        self.assertEqual(atc_file.status(), atc_reader.CORRUPT_DATA)

    def test_verifies_data_block_checksum(self):
        with open('atc/test_data/1_lead.atc', 'rb') as f:
            atc_bytes = bytearray(f.read())
        # ECG data block starts at 308, length 18000.  Modifying any byte between 308 and 18308 breaks data block checksum.
        atc_bytes[400] = 0
        with io.BytesIO(bytes(atc_bytes)) as f:
            atc_file = ATCReader(f)
        self.assertEqual(atc_file.status(), atc_reader.CORRUPT_DATA)

    def test_verifies_file_broken_checksum(self):
        atc_file = ATCReader('atc/test_data/broken_checksum.atc')
        self.assertEqual(atc_file.status(), atc_reader.CORRUPT_DATA)

    def test_loads_6_lead_file(self):
        atc_file = ATCReader('atc/test_data/6_lead.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file.num_leads(), 6)
        self.assertFalse(atc_file.mains_filtered())
        atc_file_ef = ATCReader('atc/test_data/6_lead_ef.atc')
        self.assertEqual(atc_file_ef.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file_ef.num_leads(), 6)
        self.assertFalse(atc_file_ef.mains_filtered(), 6)

    def test_loads_6_lead_file(self):
        atc_file = ATCReader('atc/test_data/12_lead.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file.num_leads(), 12)
        self.assertFalse(atc_file.mains_filtered())

    def test_loads_average_beats(self):
        atc_file = ATCReader('atc/test_data/6_lead_ab.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file.num_leads(), 6)
        self.assertFalse(atc_file.mains_filtered())
        leadI_average_beat = atc_file.get_average_beat(1)
        self.assertEqual(len(leadI_average_beat), 450)
        leadII_average_beat = atc_file.get_average_beat(2)
        self.assertEqual(len(leadII_average_beat), 450)
        with self.assertRaises(Exception) as ctx:
            atc_file.get_average_beat(3)

    def test_loads_and_saves_file(self):
        atc_file = ATCReader('atc/test_data/1_lead.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        with ATCWriter(temp_file.name) as writer:
            self.assertTrue(
                writer.write_header(
                    atc_file.date_recorded(), atc_file.recording_uuid(), atc_file.phone_uuid(), atc_file.phone_model(),
                    atc_file.recorder_software(), atc_file.recorder_hardware(), atc_file.device_data(),
                    atc_file.flags(), atc_file.sample_rate_hz(), atc_file.mains_frequency_hz())
            )
            writer.write_ecg_samples(atc_file.get_ecg_samples(1), 1)
            offsets, beat_types = atc_file.get_annotations()
            writer.write_annotations(offsets, beat_types)
        saved_atc_file = ATCReader(temp_file.name)
        self.assertEqual(saved_atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertFilesBinaryEqual(temp_file.name, 'atc/test_data/1_lead.atc')
        os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main()
