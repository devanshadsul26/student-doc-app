import os
import datetime
from google.cloud import storage
from dotenv import load_dotenv
from utils.timer import TimedBlock

load_dotenv()

client = storage.Client()
bucket = client.bucket(os.getenv("GCS_BUCKET"))


def upload_file(file, path):
    """Upload a file to GCS and return the path."""
    blob = bucket.blob(path)
    blob.upload_from_file(file)
    return path


def upload_file_timed(file, path):
    """Upload a file to GCS and return (path, elapsed_ms)."""
    blob = bucket.blob(path)
    with TimedBlock() as t:
        blob.upload_from_file(file)
    return path, t.elapsed_ms


def download_file_timed(path):
    """Download a file from GCS and return (bytes, elapsed_ms)."""
    blob = bucket.blob(path)
    with TimedBlock() as t:
        data = blob.download_as_bytes()
    return data, t.elapsed_ms


def generate_signed_url(path, expiry_minutes=15):
    """Generate a signed URL for a GCS object, valid for expiry_minutes."""
    blob = bucket.blob(path)
    url = blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=expiry_minutes),
        method="GET",
        version="v4",
    )
    return url


def delete_file(path):
    """Delete an object from the GCS bucket."""
    blob = bucket.blob(path)
    blob.delete()
