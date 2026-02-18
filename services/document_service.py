from db.queries import create_student, insert_metadata, insert_blob
from storage.gcs import upload_file


def upload_document(student_id, name, doc_type, file, store_in_sql=False):

    create_student(student_id, name)

    if store_in_sql:
        file_bytes = file.read()
        insert_blob(student_id, doc_type, file.name, file_bytes)
        return "Stored in SQL"

    else:
        path = f"students/{student_id}/{file.name}"
        upload_file(file, path)
        insert_metadata(student_id, doc_type, file.name, path, file.size)
        return "Stored in Cloud Storage"
