from db.connection import get_conn
import psycopg2
from utils.timer import TimedBlock


def create_student(student_id, name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (student_id, name)
        VALUES (%s, %s)
        ON CONFLICT (student_id) DO NOTHING
    """, (student_id, name))

    conn.commit()
    cur.close()
    conn.close()


def insert_metadata(student_id, doc_type, filename, path, size):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO documents
        (student_id, doc_type, filename, gcs_object_name, file_size_bytes)
        VALUES (%s, %s, %s, %s, %s)
    """, (student_id, doc_type, filename, path, size))

    conn.commit()
    cur.close()
    conn.close()


def insert_blob(student_id, doc_type, filename, file_bytes):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO documents_blob
        (student_id, doc_type, filename, file_bytes, file_size_bytes)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        student_id,
        doc_type,
        filename,
        psycopg2.Binary(file_bytes),
        len(file_bytes)
    ))

    conn.commit()
    cur.close()
    conn.close()


def insert_blob_timed(student_id, doc_type, filename, file_bytes):
    """Insert blob into SQL and return elapsed_ms."""
    conn = get_conn()
    cur = conn.cursor()

    with TimedBlock() as t:
        cur.execute("""
            INSERT INTO documents_blob
            (student_id, doc_type, filename, file_bytes, file_size_bytes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            doc_type,
            filename,
            psycopg2.Binary(file_bytes),
            len(file_bytes)
        ))
        conn.commit()

    cur.close()
    conn.close()
    return t.elapsed_ms


def fetch_blob_timed(student_id, filename):
    """Fetch a blob from SQL by student_id and filename, return (bytes, elapsed_ms)."""
    conn = get_conn()
    cur = conn.cursor()

    with TimedBlock() as t:
        cur.execute(
            "SELECT file_bytes FROM documents_blob WHERE student_id=%s AND filename=%s LIMIT 1",
            (student_id, filename)
        )
        row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return bytes(row["file_bytes"]), t.elapsed_ms
    return None, t.elapsed_ms


def delete_document_by_filename(student_id, filename):
    """Delete a GCS metadata record by student_id + filename."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM documents WHERE student_id=%s AND filename=%s",
        (student_id, filename)
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_blob_by_filename(student_id, filename):
    """Delete a SQL blob record by student_id + filename."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM documents_blob WHERE student_id=%s AND filename=%s",
        (student_id, filename)
    )
    conn.commit()
    cur.close()
    conn.close()

# ── SEARCH & FILTER QUERIES ────────────────────────────────────────────────

def search_documents(student_id=None, doc_type=None, filename_query=None,
                     date_from=None, date_to=None):
    """
    Flexible search across the documents table.
    All filters are optional — only applied when provided.
    """
    conn = get_conn()
    cur = conn.cursor()

    conditions = []
    params = []

    if student_id:
        conditions.append("d.student_id = %s")
        params.append(student_id)

    if doc_type and doc_type != "All":
        conditions.append("d.doc_type = %s")
        params.append(doc_type)

    if filename_query:
        conditions.append("d.filename ILIKE %s")
        params.append(f"%{filename_query}%")

    if date_from:
        conditions.append("DATE(d.uploaded_at) >= %s")
        params.append(date_from)

    if date_to:
        conditions.append("DATE(d.uploaded_at) <= %s")
        params.append(date_to)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    cur.execute(f"""
        SELECT d.student_id || '|' || d.filename AS row_key,
               d.student_id, s.name AS student_name,
               d.doc_type, d.filename, d.gcs_object_name,
               ROUND(d.file_size_bytes / 1024.0, 2) AS size_kb,
               d.uploaded_at
        FROM documents d
        JOIN students s ON d.student_id = s.student_id
        {where_clause}
        ORDER BY d.uploaded_at DESC
    """, params)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows