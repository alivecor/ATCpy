from datetime import datetime
import io
import os
import tempfile
import unittest

import atc_annotation
import atc_header
import atc_reader
from atc_reader import ATCReader
from atc_writer import ATCWriter


class TestATCWriter(unittest.TestCase):

    def assertFilesBinaryEqual(self, a, b):
        with open(a, 'rb') as fa:
            a_bytes = bytearray(fa.read())
        with open(b, 'rb') as fb:
            b_bytes = bytearray(fb.read())
        b_bytes[8] = atc_header.ATC_VERSION  # Ignore version of original file for comparison.
        for i, (a,b) in enumerate(zip(a_bytes, b_bytes)):
            if a != b:
                print('Bytes at %d not equal: %d != %d' % (i, a ,b))
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
        self.assertEqual(saved_atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertFilesBinaryEqual(temp_file.name, 'atc/test_data/1_lead.atc')
        os.unlink(temp_file.name)

    def test_saves_six_lead(self):
        atc_file = ATCReader('atc/test_data/6_lead.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file.num_leads(), 6)
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
            writer.write_ecg_samples(atc_file.get_ecg_samples(2), 2)
            writer.write_ecg_samples(atc_file.get_ecg_samples(3), 3)
            writer.write_ecg_samples(atc_file.get_ecg_samples(4), 4)
            writer.write_ecg_samples(atc_file.get_ecg_samples(5), 5)
            writer.write_ecg_samples(atc_file.get_ecg_samples(6), 6)
            offsets, beat_types = atc_file.get_annotations()
            writer.write_annotations(offsets, beat_types)
        saved_atc_file = ATCReader(temp_file.name)
        self.assertEqual(saved_atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertFilesBinaryEqual(temp_file.name, 'atc/test_data/6_lead.atc')
        os.unlink(temp_file.name)

    def test_saves_annotations(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        with ATCWriter(temp_file.name) as writer:
            self.assertTrue(
                writer.write_header(
                    'DATE_RECORDED', 'UUID_123', '', 'ATCFileWriterTest', 'TestWritesFile', '', '', {}, 300, 60)
            )
            samples = [0] * (9000)
            # Add in a few annotations, just to make sure they save and don't break.
            offsets = [10, 652]
            beat_types = [atc_annotation.BEAT_NORMAL, atc_annotation.BEAT_NORMAL]

            self.assertEqual(writer.write_ecg_samples(samples, 1), 18012)
            self.assertEqual(writer.write_ecg_samples(samples, 2), 18012)
            self.assertEqual(writer.write_annotations(offsets, beat_types), 28)
        os.unlink(temp_file.name)

    def test_saves_average_beats(self):
        atc_file = ATCReader('atc/test_data/6_lead_ab.atc')
        self.assertEqual(atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertEqual(atc_file.num_leads(), 6)
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
            writer.write_ecg_samples(atc_file.get_ecg_samples(2), 2)
            writer.write_ecg_samples(atc_file.get_ecg_samples(3), 3)
            writer.write_ecg_samples(atc_file.get_ecg_samples(4), 4)
            writer.write_ecg_samples(atc_file.get_ecg_samples(5), 5)
            writer.write_ecg_samples(atc_file.get_ecg_samples(6), 6)
            writer.write_average_beat(atc_file.get_average_beat(1), 1)
            writer.write_average_beat(atc_file.get_average_beat(2), 2)
            offsets, beat_types = atc_file.get_annotations()
            writer.write_annotations(offsets, beat_types)
        saved_atc_file = ATCReader(temp_file.name)
        self.assertEqual(saved_atc_file.status(), atc_reader.READ_SUCCESS)
        self.assertFilesBinaryEqual(temp_file.name, 'atc/test_data/6_lead_ab.atc')
        os.unlink(temp_file.name)

if __name__ == '__main__':
    unittest.main()
