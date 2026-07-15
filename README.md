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

## Data interfaces

`data_interfaces.py` provides SQLite persistence plus Kanboard, Google Tasks, and Google Calendar adapters. Google and Kanboard adapters expect caller-provided authenticated clients.

## Future work
1) Wire data interfaces into solver CLI flows
2) Add credential setup docs for Kanboard and Google Workspace
3) Make it run automatically
