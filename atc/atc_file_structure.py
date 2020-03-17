"""Defines standard atc file structure and data type for each field."""

endianness = '<'

# Header Block
header_vars = (('FileSig', '5sBBB'), ('FileVer', 'I'))

# Info Block
info_vars = (('DataLen', 'I'), ('DateRec', '32s'), ('RecUUID', '40s'),
             ('PhoneUDID', '44s'), ('PhoneModel', '32s'), ('RecSW', '32s'),
             ('RecHW', '32s'), ('Loc', '52s'), ('Checksum', 'I'))

# Format Block
fmt_vars = (('DataLen', 'I'), ('ECGFormat', 'B'), ('Fs', 'H'),
            ('AmpRes_nV', 'H'), ('Flags', 'B'), ('Reserved', 'H'),
            ('Checksum', 'I'))

# ECG data block
ecg_vars = (('DataLen', 'I'), ('Data', 'h'), ('Checksum', 'I'))

# Average beat block (optional)
avg_vars = (('DataLen', 'I'), ('Data', 'h'), ('Checksum', 'I'))

# Annotation block (optional)
ann_vars = (('DataLen', 'I'), ('TickFreq', 'I'), ('Data', 'IH'),
            ('Checksum', 'I'))

block_types = ((b'info', info_vars), (b'fmt ', fmt_vars), (b'pre ', ecg_vars),
               (b'ecg ', ecg_vars), (b'ecg2', ecg_vars), (b'ecg3', ecg_vars), (b'ecg4', ecg_vars), (b'ecg5', ecg_vars), (b'ecg6', ecg_vars),
               (b'avg ', avg_vars), (b'avg2', avg_vars), (b'ann ', ann_vars))
