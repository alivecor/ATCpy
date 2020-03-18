"""ATCReader reads ECG files in ATC format."""
import dateutil.parser
import os
import struct

import atc_file_structure as afs


# Reader status codes
READ_SUCCESS = 0      # File OK.
NO_FILE = 1           # File does not exist or is not readable.
NO_ATC_SIGNATURE = 2  # File is readable, but has no ATC signature.
MISSING_DATA = 3      # ATC file doesn't have a format block and a data block.
CORRUPT_DATA = 4      # Checksum verification failed, ATC file was modified incorrectly.


def _parse_atc_header(data):
    byte_offset = 0
    parsed_block = {}
    # Reads and validates atc header information
    for (var_name, type_str) in afs.header_vars:
        format_str = afs.endianness + type_str
        var_size = struct.calcsize(format_str)
        x = struct.unpack(format_str, data[byte_offset:byte_offset + var_size])[0]
        parsed_block[var_name] = x
        byte_offset += var_size
    if parsed_block['signature'] != b'ALIVE':
        return parsed_block, 0, NO_ATC_SIGNATURE
    return parsed_block, byte_offset, READ_SUCCESS


def _decode_flags(flag_byte):
    flags = {}
    flags['polarity'] = bool(flag_byte & 1)  # Unused
    flags['mains_frequency_hz'] = [50, 60][(flag_byte >> 1) & 1]
    flags['mains_filter'] = bool((flag_byte >> 2) & 1)
    flags['low_pass_filter'] = bool((flag_byte >> 3) & 1)  # Unused
    flags['baseline_filter'] = bool((flag_byte >> 4) & 1)
    flags['notch_mains_filter'] = bool((flag_byte >> 5) & 1)
    flags['enhanced_filter'] = bool((flag_byte >> 6) & 1)
    return flags


class ATCReader:
    def __init__(self, path_or_file):
        self.__status = READ_SUCCESS
        data = None
        if isinstance(path_or_file, str):
            if not os.path.exists(path_or_file):
                self.__status = NO_FILE
                return
            with open(path_or_file, 'rb') as f:
                data = f.read()  # read atc file in binary mode
        else:
            data = path_or_file.read()
        self.dict = self.__parse_atc_data(data)

    def status(self):
        return self.__status

    def atc_version(self):
        """An integer representing the ATC version of the file."""
        return self.dict['header']['atc_version']

    def num_leads(self):
        """Number of ECG leads in the recording."""
        return sum(l in self.dict for l in afs.lead_ids)

    def get_ecg_samples(self, lead):
        """Get ECG samples for specified lead.
        Args:
            lead (int) The index of the lead. 1 = lead I, 2 = leadII
        """
        block_id = afs.lead_ids[lead - 1]
        return self.dict[block_id]['data']

    def get_average_beat(self, lead):
        """Get the average beat for specified lead.
        Args:
            lead (int) The index of the lead. 1 = lead I, 2 = leadII
        """
        block_id = afs.avg_ids[lead - 1]
        return self.dict[block_id]['data']

    def get_annotations(self):
        """Get beat annotations.  Returns pair of offsets, beat_types"""
        annotations = self.dict['ann']['annotations']
        offsets = [a[0] for a in annotations]
        beat_types = [a[1] for a in annotations]
        return offsets, beat_types

    def mains_frequency_hz(self):
        """The mains frequency where this file was recorded."""
        return self.dict['fmt']['flags']['mains_frequency_hz']

    def sample_rate_hz(self):
        """The sample rate of the recording."""
        return self.dict['fmt']['sample_rate_hz']

    def resolution(self):
        """The resolution of the signal, in nV.  Typically 500 for native ATC units."""
        return self.dict['fmt']['resolution']

    def flags(self):
        """The value of the ATC flags field."""
        return self.dict['fmt']['flags']

    def mains_filtered(self):
        """Was this recording mains-filtered."""
        return self.dict['fmt']['flags']['mains_filter']

    def baseline_filtered(self):
        """Was this recording baseline filtered."""
        return self.dict['fmt']['flags']['baseline_filter']

    def notch_mains_filtered(self):
        """Was this recording filtered with a notch mains filter."""
        return self.dict['fmt']['flags']['notch_mains_filter']

    def enhanced_filtered(self):
        """Was this recording enhanced filtered (AliveCor enhanced filter)."""
        return self.dict['fmt']['flags']['enhanced_filter']

    def date_recorded(self):
        """Returns a datetime.datetime reprsenting the date and time this recording was made"""
        return self.dict['info']['date_recorded']

    def recording_uuid(self):
        """The recording UUID."""
        return self.dict['info']['recording_uuid']

    def phone_uuid(self):
        """The UUID of the recording mobile device (unused)."""
        return self.dict['info']['phone_uuid']

    def phone_model(self):
        """The model of the mobile device used to capture the recording."""
        return self.dict['info']['phone_model']

    def recorder_software(self):
        """The recorder software version."""
        return self.dict['info']['recorder_software']

    def recorder_hardware(self):
        """The recorder hardware."""
        return self.dict['info']['recorder_hardware']

    def device_data(self):
        """The recorder device data, which is a comma-separated string of key-value pairs specific to the device."""
        return self.dict['info']['device_data']

    def __parse_atc_data(self, data):
        """Parse an ATC file from a binary string."""
        num_of_bytes = len(data)  # file size in bytes
        parsed_data = {}
        bytes_read = 0
        # Parse header information
        try:
            header, bytes_read, status = _parse_atc_header(data[bytes_read:])
            parsed_data['header'] = header
        except Exception as e:
            status = NO_ATC_SIGNATURE

        if status != READ_SUCCESS:
            self.__status = status
            return None

        # Parse block information
        while bytes_read < num_of_bytes:
            try:
                block_id = struct.unpack('4s', data[bytes_read:bytes_read + 4])[0]
                block_id_str = block_id.decode('ascii').strip()
            except:
                self.__status = MISSING_DATA
                return None
            bytes_read += 4

            if block_id in dict(afs.block_types):
                try:
                    x, N, chksum_ok = self.__parse_atc_block(data[bytes_read:], block_id)
                    parsed_data[block_id_str] = x
                    bytes_read += N
                except Exception as e:
                    self.__status = MISSING_DATA
                    return None
                if not chksum_ok:
                    self.__status = CORRUPT_DATA
                    return None
            else:
                print('Warning: Unknown ATC block ID %s at byte position %d, ignoring' % (block_id_str, bytes_read - 4))
        # Fails if no format block present.
        if 'fmt' not in parsed_data:
            self.__status = MISSING_DATA
            return None
        return parsed_data

    def __parse_atc_block(self, data, block_id):
        byte_idx, parsed_block = 0, {}
        computed_checksum = sum(bytearray(block_id))
        block_id_str = block_id.decode('ascii').strip()
        # Read in all data fields for this block
        for (var_name, type_str) in dict(afs.block_types)[block_id]:
            format_str = afs.endianness + type_str
            parsed_block[var_name] = []
            if var_name == 'data':
                if block_id_str in ('pre', 'ecg', 'ecg2', 'ecg3', 'ecg4', 'ecg5', 'ecg6', 'avg', 'avg2'):
                    N = int(parsed_block['data_length'] / 2)
                    parsed_block[var_name], byte_idx, computed_checksum = \
                            self.__parse_atc_data_block(data, format_str, N, byte_idx, computed_checksum)
                else:
                    print('Warning: unknown atc data block ID: {0}'.format(block_id_str))
            elif var_name == 'annotations':
                if block_id_str == 'ann':
                    N = int((parsed_block['data_length'] - 4) / 6)
                    parsed_block[var_name], byte_idx, computed_checksum = \
                            self.__parse_atc_annotation_block(data, format_str, N, byte_idx, computed_checksum)
                else:
                    print('Warning: unknown atc annotation block ID: {0}'.format(block_id_str))
            else:
                var_size = struct.calcsize(format_str)
                x = struct.unpack(format_str, data[byte_idx:byte_idx+var_size])[0]
                parsed_block[var_name] = x

                if var_name != 'checksum':
                    # Updates checksum computation for this block
                    computed_checksum += sum(bytearray(
                            data[byte_idx:byte_idx + var_size]))

                if format_str[-1] == 's':
                    # Decodes any strings and strip out trailing NULLs
                    parsed_block[var_name] = parsed_block[var_name].decode('ascii')
                    parsed_block[var_name] = parsed_block[var_name].rstrip('\0')
                    parsed_block[var_name] = str(parsed_block[var_name])

                if var_name == 'date_recorded':
                    # Parses date into a datetime.datetime
                    dt = dateutil.parser.parse(parsed_block[var_name])
                    parsed_block[var_name] = dt

                if var_name == 'flags':
                    parsed_block[var_name] = _decode_flags(parsed_block[var_name])

                byte_idx += var_size
        chksum_ok = parsed_block['checksum'] == computed_checksum
        return parsed_block, byte_idx, chksum_ok

    def __parse_atc_data_block(self, data, format_str, N, byte_idx, computed_checksum):
        parsed_data = []
        var_size = struct.calcsize(format_str)
        for n in range(0, N):
            x = struct.unpack(format_str, data[byte_idx:byte_idx + var_size])
            if len(x) == 1:
                parsed_data.append(x[0])
            else:
                parsed_data.append(x)
            computed_checksum += sum(bytearray(data[byte_idx:byte_idx + var_size]))
            byte_idx += var_size
        return parsed_data, byte_idx, computed_checksum

    def __parse_atc_annotation_block(self, data, format_str, N, byte_idx, computed_checksum):
        parsed_data = []
        var_size = struct.calcsize(format_str)
        for n in range(0, N):
            x = struct.unpack(format_str, data[byte_idx:byte_idx + var_size])
            if len(x) == 2:
                parsed_data.append(x)
            computed_checksum += sum(bytearray(data[byte_idx:byte_idx + var_size]))
            byte_idx += var_size
        return parsed_data, byte_idx, computed_checksum
