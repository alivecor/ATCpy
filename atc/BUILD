package(
    default_visibility = ["//visibility:public"],
)


py_library(
    name = "atc_file_structure",
    srcs = ["atc_file_structure.py"],
)

py_library(
    name = "atc_flags",
    srcs = ["atc_flags.py"],
)

py_library(
    name = "atc_header",
    srcs = ["atc_header.py"],
)

py_library(
    name = "atc_reader",
    srcs = ["atc_reader.py"],
    deps = [
        ":atc_file_structure",
    ],
)

py_test(
    name = "atc_reader_test",
    srcs = ["atc_reader_test.py"],
    deps = [
        ":atc_reader",
    ],
)

py_library(
    name = "atc_writer",
    srcs = ["atc_writer.py"],
)
