# Architecture

The scheduler maintains job state, a priority queue, worker registry, resource accounting, scheduling policy, heartbeat-based failure detection, and retry/requeue logic.

A worker registers CPU/memory capacity and sends periodic heartbeats. A job is eligible for a worker when both requested CPU and memory fit within currently available capacity. The resource-aware policy scores remaining normalized resources and selects the best eligible worker.

If a worker misses heartbeats beyond the configured timeout, active jobs are released and requeued while retry budget remains. The protocol is newline-delimited JSON over TCP.

Job lifecycle: `queued -> running -> success` or `queued -> running -> failed -> queued` until the retry budget is exhausted.
