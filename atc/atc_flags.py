"""Values in the ATC format block flags bitfield."""

POLARITY = 1             # (Unused)
MAINS_FREQUENCY_60 = 2   # Set for 60Hz, unset for 50Hz
MAINS_FILTER = 4         # Mains filter
LP_FILTER = 8            # Low Pass Filter (Unused)
BASELINE_FILTER = 16     # 0.1Hz Baseline filter
NOTCH_MAINS_FILTER = 32  # Notch mains filter
ENHANCED_FILTER = 64     # Enhanced filter
