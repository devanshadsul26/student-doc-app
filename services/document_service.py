import io
from db.queries import create_student, insert_metadata, insert_blob, insert_blob_timed
from storage.gcs import upload_file_timed
from utils.timer import TimedBlock
from utils.cost_calculator import estimate_cost


def upload_document(student_id, name, doc_type, file, store_in_sql=False):
    """Legacy single-destination upload. Kept for backward compatibility."""
    create_student(student_id, name)

    if store_in_sql:
        file_bytes = file.read()
        insert_blob(student_id, doc_type, file.name, file_bytes)
        return "Stored in SQL"
    else:
        path = f"students/{student_id}/{file.name}"
        upload_file_timed(file, path)
        insert_metadata(student_id, doc_type, file.name, path, file.size)
        return "Stored in Cloud Storage"


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


def upload_batch(student_id, name, doc_type, files):
    """
    Upload a list of files to BOTH Cloud SQL and GCS.
    Returns:
      - results: list of per-file dicts with timing + size
      - summary: averages and totals across all files
    """
    create_student(student_id, name)

    results = []

    for file in files:
        file_bytes = file.read()
        file_size = len(file_bytes)
        filename = file.name

        # Upload to SQL
        sql_ms = insert_blob_timed(student_id, doc_type, filename, file_bytes)

        # Upload to GCS
        path = f"students/{student_id}/{filename}"
        gcs_path, gcs_ms = upload_file_timed(io.BytesIO(file_bytes), path)

        # Save GCS metadata
        insert_metadata(student_id, doc_type, filename, gcs_path, file_size)

        cost = estimate_cost(file_size)

        results.append({
            "filename": filename,
            "file_size_kb": round(file_size / 1024, 2),
            "sql_upload_ms": sql_ms,
            "gcs_upload_ms": gcs_ms,
            "sql_cost_usd": cost["sql_monthly_usd"],
            "gcs_cost_usd": cost["gcs_monthly_usd"],
            "faster": "SQL" if sql_ms < gcs_ms else "GCS",
        })

    total_files = len(results)
    avg_sql_ms = round(sum(r["sql_upload_ms"] for r in results) / total_files, 2)
    avg_gcs_ms = round(sum(r["gcs_upload_ms"] for r in results) / total_files, 2)
    total_sql_cost = round(sum(r["sql_cost_usd"] for r in results), 6)
    total_gcs_cost = round(sum(r["gcs_cost_usd"] for r in results), 6)
    total_size_kb = round(sum(r["file_size_kb"] for r in results), 2)

    summary = {
        "total_files": total_files,
        "total_size_kb": total_size_kb,
        "avg_sql_ms": avg_sql_ms,
        "avg_gcs_ms": avg_gcs_ms,
        "total_sql_cost_usd": total_sql_cost,
        "total_gcs_cost_usd": total_gcs_cost,
        "overall_faster": "SQL" if avg_sql_ms < avg_gcs_ms else "GCS",
        "avg_diff_ms": round(abs(avg_sql_ms - avg_gcs_ms), 2),
    }

    return results, summary

