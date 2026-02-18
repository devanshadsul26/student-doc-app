import streamlit as st

from services.document_service import upload_document
from db.queries import fetch_documents
from utils.metrics import get_db_metrics

st.title("Student Document Manager")

st.write("Upload, browse and compare Cloud SQL vs Cloud Storage.")

# UPLOAD SECTION

st.header("Upload Document")

student_id = st.text_input("Student ID")
student_name = st.text_input("Student Name")
doc_type = st.selectbox(
    "Document Type",
    ["ID", "Transcript", "Certificate", "Other"]
)

file = st.file_uploader("Choose a file")

store_in_sql = st.checkbox("Store file inside Cloud SQL (Demo Only)")

if st.button("Upload File"):

    if not student_id:
        st.error("Student ID is required.")
        st.stop()

    if file is None:
        st.error("Please select a file.")
        st.stop()

    try:
        result = upload_document(
            student_id,
            student_name,
            doc_type,
            file,
            store_in_sql
        )

        st.success(result)

    except Exception as e:
        st.error(f"Upload failed: {e}")

st.divider()

# BROWSE SECTION

st.header("Browse Documents")

search_id = st.text_input("Enter Student ID to search")

if st.button("Load Documents"):

    try:
        gcs_docs, blob_docs = fetch_documents(search_id)

        st.subheader("Cloud Storage Files")

        if gcs_docs:
            st.dataframe(gcs_docs)
        else:
            st.write("No files found in Cloud Storage.")

        st.subheader("SQL Blob Files")

        if blob_docs:
            st.dataframe(blob_docs)
        else:
            st.write("No files found in SQL.")

    except Exception as e:
        st.error(f"Error fetching documents: {e}")

st.divider()

# COMPARISON SECTION

st.header("Cloud SQL vs Cloud Storage")

if st.button("Show Metrics"):

    try:
        db_size, metadata_size, blob_size = get_db_metrics()

        st.write("Total Database Size:", db_size)
        st.write("Metadata Table Size:", metadata_size)
        st.write("Blob Table Size:", blob_size)

        st.write("")
        st.write("Conclusion:")
        st.write("- Cloud Storage is designed for large files.")
        st.write("- Cloud SQL should store structured data only.")
        st.write("- Storing files in SQL increases database size and cost.")

    except Exception as e:
        st.error(f"Metrics error: {e}")
