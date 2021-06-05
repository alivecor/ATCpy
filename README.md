# ATCpy

The ATC format is AliveCor's standard for ECG recordings.  ATCpy provides utilities for reading and writing ATC
files in Python.

ATCpy implements the [Alive File Format Specification 1.6](https://docs.google.com/document/d/1UiH-2maPn6-d22obk0-Vic-SBAceyFWyVVwH29i0Drc/edit).


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

    reader = ATCReader('path_to_file.atc')
    if reader.status() == atc_reader.READ_SUCCESS:
        leadI = atc_reader.get_ecg_samples(1)
        # ...
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
