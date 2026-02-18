import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

client = storage.Client()
bucket = client.bucket(os.getenv("GCS_BUCKET"))

def upload_file(file, path):
    blob = bucket.blob(path)
    blob.upload_from_file(file)
    return path
