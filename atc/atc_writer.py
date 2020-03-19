"""ATCReader writes ECG files in ATC format."""
from datetime import datetime
import io
import struct

from atc import atc_file_structure as afs
from atc import atc_flags
from atc import atc_header


def _encode_flags(d):
    flags = 0
    if d.get('polarity', False):
        flags = flags | atc_flags.POLARITY
    if d.get('mains_frequency_hz', False) == 60:
        flags = flags | atc_flags.MAINS_FREQUENCY_60
    if d.get('mains_filter', False):
        flags = flags | atc_flags.MAINS_FILTER
    if d.get('low_pass_filter', False):
        flags = flags | atc_flags.LP_FILTER
    if d.get('baseline_filter', False):
        flags = flags | atc_flags.BASELINE_FILTER
    if d.get('notch_mains_filter', False):
        flags = flags | atc_flags.NOTCH_MAINS_FILTER
    if d.get('enhanced_filter', False):
        flags = flags | atc_flags.ENHANCED_FILTER
    return flags


def _pad_binary_string(s, l):
    """Return a binary string of length l, containing at most l characters from s."""
    s = s[:l]
    pad = l - len(s)
    if pad > 0:
        s = s.ljust(l, '\0')
    return s.encode('utf-8')


class ATCWriter:
    def __init__(self, path_or_file):
        if isinstance(path_or_file, str):
            self.__f = open(path_or_file, 'wb')
        else:
            self.__f = path_or_file
        self.__sample_rate_hz = None  # Will be set by write_header

    def close(self):
        self.__f.close()
        self.__f = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__f.close()

    def write_header(self, date_recorded, recording_uuid, phone_uuid, phone_model, recorder_software, recorder_hardware,
                     device_data, flags, sample_rate_hz, mains_frequency_hz):
        """Write ATC header and format block.  Should be called before writing data segments.

           Args:
             date_recorded (datetime/str) The date and time recorded.
             recording_uuid (str) The UUID of this recording.  Max length 40.
             phone_uuid (str) The UUID of the mobile phone (unused).  Max length 44.
             phone_model (str) The model name and number of the mobile device used to make the recording.
                               i.e. "iPhone 4 : iPhone OS4.2"  Max length 32.
             recorder_software (str) The software used to generate the recording i.e. AliveECG v1.6.7.  Max length 32.
             recorder_hardware (str) The hardware used to record.  Max length 32.
             device_data (str) A string of comma separated key-value pairs specific to the recording device.
                               i.e. "SER=AC6L100010,BAT=55"  Max length 52.
             flags (dict) A dictionary of boolean values of the ATC flags field.
             sample_rate_hz (int) The recording sample rate in hz.
             mains_frequency_hz (int) The mains frequency in hz.

            Returns: True if write succeeded, False if write failed.
        """
        self.__sample_rate_hz = sample_rate_hz
        # Writes Header
        self.__f.write(atc_header.ALIVE_SIG.encode('ascii'))
        self.__f.write(struct.pack(afs.endianness + 'I', atc_header.ATC_VERSION))
        # Writes info block
        with io.BytesIO() as ib:
            ib.write(afs.info_block_id.encode('ascii'))
            ib.write(struct.pack(afs.endianness + 'I', afs.info_block_size - afs.block_container_size))  # Info block length
            if date_recorded is None:
                date_recorded = datetime.now()
            if isinstance(date_recorded, datetime):
                try:
                    date_recorded = date_recorded.isoformat(timespec='milliseconds')
                except:
                    date_recorded = date_recorded.isoformat()  # Pre python2.7 version without timespec
            ib.write(_pad_binary_string(date_recorded, 32))
            ib.write(_pad_binary_string(recording_uuid, 40))
            ib.write(_pad_binary_string(phone_uuid, 44))
            ib.write(_pad_binary_string(phone_model, 32))
            ib.write(_pad_binary_string(recorder_software, 32))
            ib.write(_pad_binary_string(recorder_hardware, 32))
            ib.write(_pad_binary_string(device_data, 52))
            info_checksum = sum(bytearray(ib.getbuffer()))
            ib.write(struct.pack(afs.endianness + 'I', info_checksum))
            self.__f.write(ib.getbuffer())
        # Writes format block
        with io.BytesIO() as fb:
            fb.write(afs.format_block_id.encode('ascii'))
            fb.write(struct.pack(afs.endianness + 'I', afs.format_block_size - afs.block_container_size))  # Format block length
            fb.write(struct.pack('B', 1))  # format = 1
            fb.write(struct.pack(afs.endianness + 'H', sample_rate_hz))
            fb.write(struct.pack(afs.endianness + 'H', 500))  # resolution = 500
            flags = _encode_flags(flags)
            if mains_frequency_hz == 60:
                flags = flags | atc_flags.MAINS_FREQUENCY_60
            fb.write(struct.pack('B', flags))
            fb.write(struct.pack(afs.endianness + 'H', 0))  # reserved = 0
            fmt_checksum = sum(bytearray(fb.getbuffer()))
            fb.write(struct.pack(afs.endianness + 'I', fmt_checksum))
            self.__f.write(fb.getbuffer())
        return not self.__f.closed

    def write_ecg_samples(self, samples, lead):
        """Writes raw samples to the ATC file.

           Args:
             samples ([int]) List of samples, in ATC units (500nV).
             lead (int) The lead to write. [1, 2, 3, 4, 5, 6]
           Returns: (int) number of bytes written.
        """
        block_id = afs.lead_ids[lead - 1]
        return self.__write_data_block(samples, block_id)

    def write_average_beat(self, average_beat, lead):
        """Writes average beat to the ATC file.

           Args:
             samples ([int]) List of samples, in ATC units (500nV).
             lead (int) The lead to write. [1, 2]
           Returns: (int) number of bytes written.
        """
        block_id = afs.avg_ids[lead - 1]
        return self.__write_data_block(average_beat, block_id)

    def write_annotations(self, offsets, types):
        """Writes annotations to the ATC file.

           Args:
             offsets ([int]) List of beat locations, in samples.
             types ([int]) List of beat types.  Must be same length as offsets.
           Returns: (int) number of bytes written.
        """
        block_length_bytes = 4 + (len(offsets) * 6)
        with io.BytesIO() as ab:
            ab.write(afs.annotation_block_id.encode('ascii'))
            ab.write(struct.pack(afs.endianness + 'I', block_length_bytes))  # Annotation block length
            ab.write(struct.pack(afs.endianness + 'I', self.__sample_rate_hz))  # Annotation tick frequency
            for o, t in zip(offsets, types):
                ab.write(struct.pack(afs.endianness + 'I', o))
                ab.write(struct.pack(afs.endianness + 'h', t))
            data_checksum = sum(bytearray(ab.getbuffer()))
            ab.write(struct.pack(afs.endianness + 'I', data_checksum))
            return self.__f.write(ab.getbuffer())

    def __write_data_block(self, sample_data, block_id):
        """Writes data block, returns bytes written."""
        if block_id is None:
            # Lead not supported in ATC format.
            return 0
        with io.BytesIO() as db:
            db.write(block_id.encode('ascii'))
            data_length_bytes = len(sample_data) * 2
            db.write(struct.pack(afs.endianness + 'I', data_length_bytes))  # Data block length
            for x in sample_data:
                db.write(struct.pack(afs.endianness + 'h', x))
            data_checksum = sum(bytearray(db.getbuffer()))
            db.write(struct.pack(afs.endianness + 'I', data_checksum))
            return self.__f.write(db.getbuffer())
