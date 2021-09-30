# ATCpy

The ATC format is AliveCor's standard for ECG recordings.  ATCpy provides utilities for reading and writing ATC
files in Python.

ATCpy implements the [Alive File Format Specification 1.7](docs/ATC%20Spec%201.7.md).


## Requirements

__Python 3__

__Bazel__

[Bazel](https://bazel.build)

## Modules


### //atc:atc_reader

Reads and parses an ATC file.

```
    import atc_reader
    from atc_reader import ATCReader
    import numpy as np

    reader = ATCReader('path_to_file.atc')
    if reader.status() == atc_reader.READ_SUCCESS:
        num_leads = atc_reader.num_leads()
        
        # Gets ATC samples for lead I in native int16 format
        leadI_samples = atc_reader.get_ecg_samples(1)  
        
        # Converts ATC samples to mV.  resolution is always in nanovolts (nV)
        atc_to_mv = atc_reader.resolution() * 1e-6
        leadI_samples_mV = np.array(leadI_samples, dtype=np.float32) * atc_to_mv
        
    else:
        # handle error.
```

### //atc:atc_writer

Writes ECG data to an ATC file.

```
    from atc_writer import ATCWriter

    with ATCWriter('path_to_file.atc') as writer:
        writer.write_header(...)
        writer.write_ecg_samples(...)
        ...
```
