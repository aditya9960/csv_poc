# CSV POC – FastAPI CSV File Management Service

A **FastAPI** application for uploading, storing, and processing CSV files with asynchronous background processing via **Celery**, persistent metadata storage in **PostgreSQL**, and support for pagination, uploads, and robust error handling.

---

## 🚀 Features

* REST API with **FastAPI** and **Pydantic** validation.
* CSV file upload and storage on local filesystem (with timestamped filenames).
* Persistent metadata storage in **PostgreSQL** via **SQLAlchemy** ORM.
* Background processing using **Celery** + **Redis** for asynchronous tasks.
* Paginated retrieval of CSV data to avoid memory issues for large files.
* Duplicate file detection using **checksum** to ensure idempotency.
* Logging and exception handling for production readiness.
* Dockerized setup with `docker-compose`.
* End-to-end unit and integration tests with **pytest**.

---

## 📂 Project Structure

```
csv_poc/
├── app/
│   ├── api/
│   │   └── v1/routes.py            # API endpoints for upload, metadata, data
│   ├── core/
│   │   ├── config.py               # Configuration & environment
│   │   ├── database.py             # DB connection & session
│   │   └── logger.py               # Request logging
│   ├── models/
│   │   └── files.py                # File metadata SQLAlchemy model
│   ├── schemas/
│   │   └── responses/files.py      # Pydantic response schemas
│   ├── storage/
│   |   ├── base.py                 # Abstraction for storage
│   │   └── local.py                # Local file storage backend
│   ├── services/
│   │   └── file_service.py         # DB & business logic for files
│   ├── utils/
│   │   └── csv_utils.py            # CSV parsing / pagination
│   ├── workers/
│   │   └── tasks.py                # Celery background tasks
│   └── main.py                     # FastAPI app initialization
├── tests/
|   ├── test files                  # Unit & integration tests
│   └── data/sample.csv             # Shared test CSV
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── local_cmds.txt                  # just for developer
└── README.md
```

---

## ⚙️ Prerequisites

* Docker & Docker Compose installed
* Python 3.11 (optional if running outside Docker)
* `curl` or Postman for API testing

---

## 🐳 Docker Setup

1. Build and start all services:

```bash
docker-compose up --build
```

2. Services will run at:

* **API**: `http://localhost:8000`
* **PostgreSQL**: `localhost:5432` (user/password: `postgres`)
* **Redis**: `localhost:6379`
* **Celery worker**: processes file uploads in the background

3. Stop services:

```bash
docker-compose down
```

4. Remove persisted files (if needed):

```bash
docker volume rm csv_poc_data
```

---

## ⚡ API Endpoints

### 1. Upload CSV

```
POST /upload
```

**Params**:

* `file` – CSV file (required)

**Response**:

```json
{
  "file_id": "<uuid>",
  "status": "uploaded"
}
```

* Duplicate files are blocked by checksum.
* Background processing populates `rows`, `columns`, `size`, and `status`.

---

### 2. List Files

```
GET /files?page=1&page_size=10
```

**Response**:

```json
[
  {
    "id": "<uuid>",
    "filename": "genes_human.csv",
    "size": 6051585,
    "rows": 57992,
    "columns": 7,
    "status": "ready",
    "created_at": "2026-02-26T21:06:31.314252Z"
  }
]
```

* Supports pagination via `page` and `page_size`.

---

### 3. File Metadata

```
GET /files/{file_id}/metadata
```

**Response**:

```json
{
  "id": "<uuid>",
  "filename": "genes_human.csv",
  "size": 123456,
  "rows": 100,
  "columns": 5,
  "status": "ready",
  "created_at": "2026-02-26T15:30:00Z"
}
```

---

### 4. File Data (Paginated)

```
GET /files/{file_id}/data?page=1&page_size=100
```

**Response**:

```json
{
  "file_id": "decc888d-d1ef-4a56-a523-6e96f64c6fd8",
  "filename": "genes_human.csv",
  "page": 1,
  "page_size": 100,
  "rows_returned": 100,
  "data": [
    {
      "Ensembl": "ENSG00000250577",
      "Gene symbol": "",
      "Name": "",
      "Biotype": "Linc R N A",
      "Chromosome": "4",
      "Seq region start": "138923930",
      "Seq region end": "138924232"
    },
    ...
  ]
}
```

* Avoids loading the full file into memory.

---

## 🔧 Running Tests

All test cases use a shared sample CSV (`tests/data/sample.csv`) for consistency.

```bash
pytest -v tests/
```

* Covers upload, metadata, data retrieval, duplicates, pagination, and end-to-end flow.

---

## 🛡️ Logging & Monitoring

* Structured logging via Python `logging` module.
* Logs exceptions with stack traces.
* Request logging middleware captures API call metadata.
* Celery logs all background tasks with `file_id`.

---

## 🧩 Future Enhancements

* TUS protocol for resumable uploads.
* S3 or cloud storage backend via `StorageBackend` abstraction.
* Enum for file `status` instead of string.
* More granular validation of CSV content.

---

## 📌 Notes

* Uploaded files are saved in Docker volume:

```text
/data/files
```

* File names include timestamp and UUID to avoid collisions.
* Idempotency is ensured via checksum — uploading the same file twice is blocked.
