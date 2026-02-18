from db.connection import get_conn

def get_db_metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT pg_size_pretty(pg_database_size('student_docs'));")
    db_size = cur.fetchone()[0]

    cur.execute("SELECT pg_size_pretty(pg_total_relation_size('documents'));")
    metadata_size = cur.fetchone()[0]

    cur.execute("SELECT pg_size_pretty(pg_total_relation_size('documents_blob'));")
    blob_size = cur.fetchone()[0]

    cur.close()
    conn.close()

    return db_size, metadata_size, blob_size
