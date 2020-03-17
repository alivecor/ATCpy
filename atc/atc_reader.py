"""ATCReader reads ECG files in ATC format."""
import os
import struct

import atc_file_structure


# Reader status codes
READ_SUCCESS = 0      # File OK.
NO_FILE = 1           # File does not exist or is not readable.
NO_ATC_SIGNATURE = 2  # File is readable, but has no ATC signature.
MISSING_DATA = 3      # ATC file doesn't have a format block and a data block.
CORRUPT_DATA = 4      # Checksum verification failed, ATC file was modified incorrectly.


def parse_atc_header_(data):
    byte_offset = 0
    parsed_block = {}
    error_msg = None

    # Reads and validates atc header information
    for (var_name, type_str) in atc_file_structure.header_vars:
        format_str = atc_file_structure.endianness + type_str
        var_size = struct.calcsize(format_str)
        x = struct.unpack(format_str, data[byte_offset:byte_offset + var_size])
        parsed_block[var_name] = x
        byte_offset += var_size

    if (parsed_block['FileSig'][0] != b'ALIVE' or parsed_block['FileSig'][1:] != (0, 0, 0)):
        return parsed_block, 0,
        error_msg = "Invalid atc file signature"

    return parsed_block, byte_offset, READ_SUCCESS


class ATCReader:
    def __init__(self, path):
        if not os.path.exists(path):
            self.status_ = NO_FILE
            return
        with open(atc_file, 'rb') as f:
            data = f.read()  # read atc file in binary mode
        self.dict = self.parse_atc_data(data)

    def status(self):
        return self.status_

    def atc_version():
        return self.dict['']

    def parse_atc_data(self, data):
        """Parse an ATC file from a binary string."""
        num_of_bytes = len(data)  # file size in bytes
        parsed_data = {}
        bytes_read = 0
        error_msg = None

        # Parse header information
        try:
            header, bytes_read, error_msg = parse_atc_header(data[bytes_read:])
            parsed_data['header'] = header
        except:
            error_msg = "Unable to parse atc header"

        if error_msg:
            return None, error_msg

        # Parse block information
        while bytes_read < num_of_bytes:
            try:
                block_ID = struct.unpack('4s', data[bytes_read:bytes_read + 4])[0]
                block_ID_str = block_ID.decode('ascii').strip()
            except:
                error_msg = "Unable to decode block ID %s" % block_ID_str
                return None, error_msg

            bytes_read += 4

            if block_ID in dict(atc_fs.block_types):
                try:
                    x, N, chksum_ok, error_msg = parse_atc_block(data[bytes_read:],
                                                                 block_ID)
                    parsed_data[block_ID_str] = x
                    bytes_read += N
                except Exception as e:
                    error_msg = "Problem parsing %s block" % block_ID_str
                    error_msg += "\n" + str(e)

                if error_msg:
                    return None, error_msg

                if not chksum_ok:
                    error_msg = "Checksum failed for %s block" % block_ID_str
            else:
                error_msg = ("Unknown atc block ID %s at byte position %d" %
                             (block_ID_str, bytes_read - 4))
                return None, error_msg

        return parsed_data, error_msg
