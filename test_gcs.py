from google.cloud import storage
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/service_account.json"

client = storage.Client()
bucket = client.bucket("student-docs-acs-123")

blob = bucket.blob("test-folder/hello.txt")
blob.upload_from_string("Hello Devansh — your bucket works!")

print("UPLOAD SUCCESS")
