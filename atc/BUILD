package(
    default_visibility = ["//visibility:public"],
)

py_library(
    name = "atc_annotation",
    srcs = ["atc_annotation.py"],
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
        ":atc_header",
        ":atc_reader",
        ":atc_writer",
    ],
    data = [
        "//atc/test_data:atc_test_files",
    ]
)

py_library(
    name = "atc_writer",
    srcs = ["atc_writer.py"],
    deps = [
        ":atc_file_structure",
        ":atc_flags",
        ":atc_header",
    ],
)

py_test(
    name = "atc_writer_test",
    srcs = ["atc_writer_test.py"],
    deps = [
        ":atc_annotation",
        ":atc_header",
        ":atc_reader",
        ":atc_writer",
    ],
    data = [
        "//atc/test_data:atc_test_files",
    ]
)
