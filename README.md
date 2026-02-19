# Student Document Manager

A cloud-based document management system that benchmarks **Cloud SQL (PostgreSQL)** against **Google Cloud Storage (GCS)** for real-world upload speed, download speed, and storage cost.

Built with Python and Streamlit.

---

## Features

| Feature | Description |
|---------|-------------|
| **Upload & Compare** | Upload a file to both Cloud SQL and GCS simultaneously and compare upload time and monthly cost side by side |
| **Advanced Search** | Filter documents by student ID, document type, and filename using SQL queries |
| **Download** | Retrieve files directly from GCS per search result |
| **Delete** | Remove a file from both Cloud SQL and GCS in one click |
| **Real Benchmark** | Generate test files (1 KB – 5 MB), run timed uploads and downloads, view charts, and export results to Excel |

---

## Project Structure

```
student-doc-app/
├── app.py                    # Main Streamlit application
├── .env                      # Environment variables (not committed)
├── db/
│   ├── connection.py         # PostgreSQL connection helper
│   └── queries.py            # All SQL queries (insert, search, delete)
├── storage/
│   └── gcs.py                # GCS upload, download, delete helpers
├── services/
│   ├── document_service.py   # Dual-write upload orchestration
│   └── benchmark_service.py  # Benchmark file generation, timing, Excel export
├── utils/
│   ├── timer.py              # TimedBlock context manager (perf_counter)
│   └── cost_calculator.py    # Monthly storage cost estimation
└── keys/                     # GCS service account key (not committed)
```

---

## Requirements

### Python Libraries

```
streamlit
pandas
plotly
python-dotenv
psycopg2-binary
google-cloud-storage
openpyxl
```

Install all at once:

```bash
pip install streamlit pandas plotly python-dotenv psycopg2-binary google-cloud-storage openpyxl
```

---

## Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# PostgreSQL / Cloud SQL
DB_HOST=your-cloud-sql-ip
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-db-username
DB_PASS=your-db-password

# Google Cloud Storage
GCS_BUCKET=your-gcs-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=keys/your-service-account-key.json
```

### GCS Service Account

1. Go to **Google Cloud Console → IAM & Admin → Service Accounts**
2. Create a service account with the **Storage Object Admin** role
3. Download the JSON key and place it in the `keys/` folder
4. Set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` to the key file path

---

## Database Schema

Run the following SQL on your Cloud SQL instance to create the required tables:

```sql
-- Student identity
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    name       VARCHAR(100)
);

-- File metadata (GCS reference)
CREATE TABLE documents (
    student_id      VARCHAR(20) REFERENCES students(student_id),
    doc_type        VARCHAR(50),
    filename        VARCHAR(255),
    gcs_object_name VARCHAR(500),
    file_size_bytes INTEGER,
    uploaded_at     TIMESTAMP DEFAULT NOW()
);

-- Binary file content (SQL blob storage for benchmarking)
CREATE TABLE documents_blob (
    student_id      VARCHAR(20),
    doc_type        VARCHAR(50),
    filename        VARCHAR(255),
    file_bytes      BYTEA,
    file_size_bytes INTEGER,
    uploaded_at     TIMESTAMP DEFAULT NOW()
);
```

---

## Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## How It Works

### Upload Flow
1. User submits a file via the web interface
2. File bytes are inserted as `BYTEA` into `documents_blob` in Cloud SQL — upload time recorded
3. Same file is uploaded to GCS via the SDK — upload time recorded
4. Metadata (`student_id`, `doc_type`, `filename`, `gcs_object_name`, `file_size_bytes`) is inserted into `documents`
5. Both timings and estimated monthly costs are displayed

### Benchmark Flow
1. Binary test files are generated in memory using `os.urandom(n_bytes)`
2. For each file size and each run: SQL upload, GCS upload, SQL download, GCS download are timed
3. Results are averaged across runs and displayed as interactive bar charts
4. Results can be exported to a two-sheet Excel file (raw + averages)

### Delete Flow
1. Clicking Delete on a search result removes:
   - The metadata row from `documents` in Cloud SQL
   - The blob row from `documents_blob` in Cloud SQL
   - The object from GCS
2. The search results list updates immediately without requiring a re-search

---

## Cost Model

| Service | Price |
|---------|-------|
| Cloud SQL SSD | $0.17 / GB / month |
| GCS Standard | $0.023 / GB / month |

GCS is approximately **7.4× cheaper** than Cloud SQL for binary storage at any file size.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web UI | Streamlit |
| Database | Cloud SQL (PostgreSQL 14) |
| Object Storage | Google Cloud Storage |
| DB Driver | psycopg2-binary |
| Data Processing | Pandas |
| Charts | Plotly |
| Excel Export | openpyxl |
| Config | python-dotenv |

---

## Notes

- The `.env` file and `keys/` directory are excluded from version control via `.gitignore`
- Benchmark runs are sequential; results will vary by network condition and time of day
- Cost estimates cover storage only and exclude network egress and Cloud SQL instance compute costs
