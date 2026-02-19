import io
from db.queries import create_student, insert_metadata, insert_blob, insert_blob_timed
from storage.gcs import upload_file_timed
from utils.timer import TimedBlock
from utils.cost_calculator import estimate_cost


def upload_document_both(student_id, name, doc_type, file):
    """
    Upload the same file to BOTH Cloud SQL (as BYTEA) and GCS simultaneously.
    Returns a dict with timing and cost info for comparison.
    """
    create_student(student_id, name)

    file_bytes = file.read()
    file_size = len(file_bytes)
    filename = file.name

    # --- Upload to Cloud SQL (BYTEA) ---
    sql_ms = insert_blob_timed(student_id, doc_type, filename, file_bytes)

    # --- Upload to GCS ---
    path = f"students/{student_id}/{filename}"
    gcs_path, gcs_ms = upload_file_timed(io.BytesIO(file_bytes), path)

    # --- Save GCS metadata reference ---
    insert_metadata(student_id, doc_type, filename, gcs_path, file_size)

    return {
        "filename": filename,
        "file_size_bytes": file_size,
        "sql_upload_ms": sql_ms,
        "gcs_upload_ms": gcs_ms,
        "gcs_path": gcs_path,
    }
    

