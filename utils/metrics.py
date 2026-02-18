from db.connection import get_conn


def get_db_metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT pg_size_pretty(pg_database_size(current_database())) AS size;")
    db_size = cur.fetchone()["size"]

    cur.execute("SELECT pg_size_pretty(pg_total_relation_size('documents')) AS size;")
    metadata_size = cur.fetchone()["size"]

    cur.execute("SELECT pg_size_pretty(pg_total_relation_size('documents_blob')) AS size;")
    blob_size = cur.fetchone()["size"]

    cur.close()
    conn.close()

    return db_size, metadata_size, blob_size
