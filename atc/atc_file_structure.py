"""Defines standard atc file structure and data type for each field."""

endianness = '<'


# Block IDs - the first 4 bytes of any block tell us which type of block it is.
format_block_id = "fmt "
info_block_id = "info"
annotation_block_id = "ann "
ecg_data_block_id = "ecg "   # Lead I
ecg2_data_block_id = "ecg2"  # Lead II
ecg3_data_block_id = "ecg3"  # Lead III
ecg4_data_block_id = "ecg4"  # Lead aVR
ecg5_data_block_id = "ecg5"  # Lead aVL
ecg6_data_block_id = "ecg6"  # Lead aVF
avg_beat_data_block_id = 'avg '  # Lead I Average Beat
avg_beat2_data_block_id = 'avg2'  # Lead II Average Beat

atc_block_id_len = 4

lead_ids = ['ecg', 'ecg2', 'ecg3', 'ecg4', 'ecg5', 'ecg6']
avg_ids = ['avg', 'avg2']


# Note: Every block starts with atc_block_id_len bytes, followed by uint32_t length, and ends with uint32_t checksum.
block_container_size = atc_block_id_len + (2 * 4)

# Length of format block in bytes.
format_block_size = block_container_size + 2 + (3 * 2)

# Length of info block in bytes.
info_block_size = block_container_size + 32 + 40 + 44 + 32 + 32 + 32 + 52


# Header Block
header_vars = (('signature', '5sBBB'), ('atc_version', 'I'))

# Info Block
info_vars = (('data_length', 'I'), ('date_recorded', '32s'), ('recording_uuid', '40s'),
             ('phone_uuid', '44s'), ('phone_model', '32s'), ('recorder_software', '32s'),
             ('recorder_hardware', '32s'), ('device_data', '52s'), ('checksum', 'I'))

# Format Block
fmt_vars = (('data_length', 'I'), ('ecg_format', 'B'), ('sample_rate_hz', 'H'),
            ('resolution', 'H'), ('flags', 'B'), ('reserved', 'H'),
            ('checksum', 'I'))

# ECG data block
ecg_vars = (('data_length', 'I'), ('data', 'h'), ('checksum', 'I'))

# Average beat block (optional)
avg_vars = (('data_length', 'I'), ('data', 'h'), ('checksum', 'I'))

# Annotation block (optional)
ann_vars = (('data_length', 'I'), ('tick_frequency', 'I'), ('annotations', 'IH'),
            ('checksum', 'I'))

block_types = ((b'info', info_vars), (b'fmt ', fmt_vars), (b'pre ', ecg_vars),
               (b'ecg ', ecg_vars), (b'ecg2', ecg_vars), (b'ecg3', ecg_vars), (b'ecg4', ecg_vars), (b'ecg5', ecg_vars), (b'ecg6', ecg_vars),
               (b'avg ', avg_vars), (b'avg2', avg_vars), (b'ann ', ann_vars))
