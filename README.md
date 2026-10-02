# Distributed Task Scheduler

A dependency-light distributed task scheduler in Python demonstrating centralized scheduling, concurrent workers, priority/resource-aware placement, heartbeats, failure detection, retries, and benchmarking.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m scheduler.server
```

In other terminals:
```bash
python -m worker.worker --worker-id worker-1 --cpu 4 --memory 4096
python -m worker.worker --worker-id worker-2 --cpu 2 --memory 2048
python -m client.client submit --type sleep --seconds 2 --priority 10
python -m client.client status
```

Run tests with `pytest`.

## Architecture

```text
 Client --> Scheduler --> Worker 1
                 |------> Worker 2
                 |------> Worker 3
                   ^
             heartbeats
```

The scheduler owns the central priority queue, worker registry, scheduling policy, resource accounting, failure detection, and retry/requeue logic. Workers communicate over newline-delimited JSON/TCP and execute tasks concurrently.

## Scheduling policies

- `fifo`: first eligible worker
- `priority`: least-loaded eligible worker
- `priority_resource`: chooses an eligible worker using remaining normalized CPU/memory capacity

## Docker

```bash
docker compose up --build
```

See `docs/architecture.md` for implementation details.
