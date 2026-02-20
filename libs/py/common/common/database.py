import asyncpg
from prometheus_client import Histogram, Gauge

db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["service", "operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

db_pool_size = Gauge(
    "db_pool_size",
    "Database connection pool size",
    ["service"],
)

db_pool_free = Gauge(
    "db_pool_free_connections",
    "Database connection pool free connections",
    ["service"],
)

db_pool_used = Gauge(
    "db_pool_used_connections",
    "Database connection pool used connections",
    ["service"],
)


async def create_pool(dsn: str, min_size: int = 5, max_size: int = 5) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=dsn, min_size=min_size, max_size=max_size)


def update_pool_metrics(pool: asyncpg.Pool, service_name: str) -> None:
    """Update Prometheus gauges with current pool state."""
    db_pool_size.labels(service=service_name).set(pool.get_size())
    db_pool_free.labels(service=service_name).set(pool.get_idle_size())
    db_pool_used.labels(service=service_name).set(
        pool.get_size() - pool.get_idle_size()
    )
