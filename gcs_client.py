# import os
# from google.cloud import storage
# from dotenv import load_dotenv

# load_dotenv()

# BUCKET = os.getenv("GCS_BUCKET")

# def upload_bytes(data: bytes, dest_path: str, content_type: str = "application/octet-stream") -> str:
#     client = storage.Client()
#     bucket = client.bucket(BUCKET)
#     blob = bucket.blob(dest_path)
#     blob.upload_from_string(data, content_type=content_type)
#     return dest_path
