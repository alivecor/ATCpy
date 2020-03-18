"""Defines standard atc file structure and data type for each field."""

endianness = '<'

# Header Block
header_vars = (('signature', '5sBBB'), ('atc_version', 'I'))

# Info Block
info_vars = (('data_length', 'I'), ('date_recorded', '32s'), ('recording_uuid', '40s'),
             ('phone_uuid', '44s'), ('phone_model', '32s'), ('recorded_software', '32s'),
             ('recorded_hardware', '32s'), ('device_data', '52s'), ('checksum', 'I'))

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
