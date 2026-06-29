Last Updated: 2022/05/31

# schedule_solver

MVP: CSV tasks in, OR-Tools/CP-SAT schedule out. Follow-up solver experiments: GA (#1), greedy (#6), linear programming (#5).

## Run MVP solver

```bash
python3 solve_schedule_ortools.py --input=tasks.csv --output=schedule.csv
```

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
3) Make it run automatically
