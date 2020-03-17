"""Values in the ATC format block flags bitfield."""

FLAG_POLARITY = 1             # (Unused)
FLAG_MAINS_FREQUENCY_60 = 2   # Set for 60Hz, unset for 50Hz
FLAG_MAINS_FILTER = 4         # Mains filter
FLAG_LP_FILTER = 8            # Low Pass Filter (Unused)
FLAG_BASELINE_FILTER = 16     # 0.1Hz Baseline filter
FLAG_NOTCH_MAINS_FILTER = 32  # Notch mains filter
FLAG_ENHANCED_FILTER = 64     # Enhanced filter
