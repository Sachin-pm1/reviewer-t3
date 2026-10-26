"""Jobs domain: long-running background tasks (the Analyze lifecycle) + status.

Increment 1 runs jobs in-process via FastAPI background tasks. The ``CollectionJob``
row is the durable record of progress/result, so swapping to a real queue (Celery,
RQ, Arq) later is an executor change, not an API change.
"""
