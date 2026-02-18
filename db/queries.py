from db.connection import get_conn
import psycopg2


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


def fetch_documents(student_id):
    conn = get_conn()

    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE student_id=%s", (student_id,))
    gcs_docs = cur.fetchall()

    cur.execute("SELECT * FROM documents_blob WHERE student_id=%s", (student_id,))
    blob_docs = cur.fetchall()

    cur.close()
    conn.close()

    return gcs_docs, blob_docs
