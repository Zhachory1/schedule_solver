load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")
load("@py_deps//:requirements.bzl", "requirement")

py_proto_library(
    name = "tasks_py_proto",
    srcs = ["tasks.proto"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "solve_interface",
    srcs = ["solve_interface.py"],
    deps = [
        ":tasks_py_proto",
        requirement("numpy"),
    ],
    srcs_version = "PY3",
)

py_library(
    name = "solve_schedule_ga",
    srcs = ["solve_schedule_ga.py"],
    deps = [
        ":tasks_py_proto",
        requirement("numpy"),
    ],
    srcs_version = "PY3",
)

py_test(
    name = "solve_schedule_ga_test",
    srcs = ["solve_schedule_ga_test.py"],
    deps = [
        ":solve_schedule_ga",
        ":tasks_py_proto",
        requirement("numpy"),
        requirement("protobuf"),
        requirement("pandas"),
    ],
)

py_binary(
    name = "solve_schedule_main",
    srcs = ["solve_schedule_main.py"],
    srcs_version = "PY3",
    deps = [
        ":solve_schedule_ga",
        ":tasks_py_proto",
        requirement("matplotlib"),
        requirement("absl-py"),
        requirement("pandas"),
    ]
)

filegroup(
    name = "templates",
    srcs = glob([
        "templates/*.html",
    ])
)

filegroup(
    name = "static",
    srcs = glob([
        "static/**/*",
    ])
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    srcs_version = "PY3",
    deps = [
        requirement("flask"),
    ],
    data = [
        ":templates",
        ":static",
    ]
)