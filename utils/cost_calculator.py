# GCP Pricing (as of 2024, us-central1 region)
# Cloud SQL SSD storage: $0.17 per GB per month
# GCS Standard storage:  $0.023 per GB per month

CLOUD_SQL_PRICE_PER_GB = 0.17
GCS_PRICE_PER_GB = 0.023

BYTES_PER_GB = 1024 ** 3


def estimate_cost(size_bytes: int) -> dict:
    """
    Given a file size in bytes, return estimated monthly storage cost
    for Cloud SQL vs GCS.
    """
    size_gb = size_bytes / BYTES_PER_GB

    sql_cost = size_gb * CLOUD_SQL_PRICE_PER_GB
    gcs_cost = size_gb * GCS_PRICE_PER_GB

    return {
        "size_bytes": size_bytes,
        "size_kb": round(size_bytes / 1024, 2),
        "size_mb": round(size_bytes / (1024 ** 2), 4),
        "sql_monthly_usd": round(sql_cost, 6),
        "gcs_monthly_usd": round(gcs_cost, 6),
        "sql_price_per_gb": CLOUD_SQL_PRICE_PER_GB,
        "gcs_price_per_gb": GCS_PRICE_PER_GB,
        "savings_usd": round(sql_cost - gcs_cost, 6),
        "gcs_cheaper_by_x": round(CLOUD_SQL_PRICE_PER_GB / GCS_PRICE_PER_GB, 1),
    }
