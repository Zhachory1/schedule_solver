Last Updated: 2022/05/31

# schedule_solver
Solving the scheduling problem with Genetic Algorithms and Google's OrTools

## TODO(zhach):
1) Complete GA implementation
2) Complete tests for it
3) Add test for or tools (it's freaking weird dude; no documentation at all)
4) Add data file

## Local non-Bazel setup

This repo expects `tasks_pb2.py` to be generated from `tasks.proto` before running Python solvers/tests outside Bazel:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt grpcio-tools
python -m grpc_tools.protoc --python_out=. tasks.proto
python -m unittest discover -p '*test*.py'
```

If you use system `protoc` instead:

```bash
protoc --python_out=. tasks.proto
```

`tasks_pb2.py` is generated code and can be regenerated whenever `tasks.proto` changes.

## Future work
1) Connecting input apps
    a) Like connecting to the tasks api or a kanban server to get tasks
2) Connect output apps
    a) Like connect to my calendar to make these time units for me
    b) Also try to track scheduled stuff in a db
3) Make a hueristic greedy scheduler
4) Make it run automatically
