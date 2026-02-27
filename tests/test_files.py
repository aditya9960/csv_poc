import io
from pathlib import Path
from app.models.files import FileMetadata

SAMPLES_DIR = Path(__file__).parent / "sample_files"
# helper util fun for reading files from sample_files folder
def get_sample_file(name: str):
    """
    Returns a tuple suitable for FastAPI `files` param:
    """
    file_path = SAMPLES_DIR / name
    mime_type = "text/csv" if file_path.suffix == ".csv" else "text/plain"
    return (file_path.name, open(file_path, "rb"), mime_type)

# helper util fun for celery task
def mark_file_ready(db_session_obj):
    db_session_obj.query(FileMetadata).update(
        {FileMetadata.status: "ready"},
        synchronize_session=False,
    )
    db_session_obj.commit()


def test_upload_csv_success(client, db_session):
    response = client.post("/upload", files={"file": get_sample_file("sample.csv")},)
    mark_file_ready(db_session)

    assert response.status_code == 202
    assert "file_id" in response.json()


def test_upload_invalid_extension(client):
    response = client.post("/upload", files={"file": get_sample_file("sample.txt")},)

    assert response.status_code == 400
    assert response.json()["detail"] == "Only CSV allowed"


def test_upload_duplicate_file(client, db_session):
    file_content = b"a;b\n1;2"
    response_1 = client.post("/upload", files={"file": get_sample_file("sample.csv")},)
    # update for celery
    mark_file_ready(db_session)
    response_2 = client.post("/upload", files={"file": get_sample_file("sample.csv")},)

    assert response_2.status_code == 409


def test_list_files_empty(client):
    response = client.get("/files")
    assert response.status_code == 200
    assert response.json() == []


def test_list_files_pagination_validation(client):
    response = client.get("/files?page=0")
    assert response.status_code == 422


def test_list_files_page_size_limit(client):
    response = client.get("/files?page_size=101")
    assert response.status_code == 422


def test_get_metadata_success(client):
    upload = client.post("/upload", files={"file": get_sample_file("sample.csv")}, )

    file_id = upload.json()["file_id"]
    response = client.get(f"/files/{file_id}/metadata")

    assert response.status_code == 200
    assert response.json()["id"] == file_id


def test_get_metadata_not_found(client):
    response = client.get("/files/non-existent-id/metadata")
    assert response.status_code == 404

def test_get_file_data_not_ready(client):
    upload = client.post("/upload", files={"file": get_sample_file("sample.csv")}, )

    file_id = upload.json()["file_id"]

    response = client.get(f"/files/{file_id}/data")
    assert response.status_code == 400


def test_get_file_data_not_found(client):
    response = client.get("/files/invalid-id/data")
    assert response.status_code == 404


def test_get_file_data_success(client, db_session):
    # upload = client.post(
    #     "/upload",
    #     files={"file": ("sample.csv", io.BytesIO(b"a;b\n1;2\n3;4"), "text/csv")},
    # )
    upload = client.post("/upload", files={"file": get_sample_file("sample.csv")}, )
    file_id = upload.json()["file_id"]

    mark_file_ready(db_session)

    response = client.get(f"/files/{file_id}/data?page=1&page_size=10")

    assert response.status_code == 200
    body = response.json()
    assert body["rows_returned"] == 7
    assert len(body["data"]) == 7


def test_e2e_upload_metadata_data(client, db_session):
    # upload
    upload = client.post("/upload", files={"file": get_sample_file("sample.csv")}, )
    assert upload.status_code == 202
    file_id = upload.json()["file_id"]

    # metadata check
    metadata = client.get(f"/files/{file_id}/metadata")
    assert metadata.status_code == 200

    mark_file_ready(db_session)

    # data endpoint
    data = client.get(f"/files/{file_id}/data?page=1&page_size=100")
    assert data.status_code == 200
    assert data.json()["rows_returned"] == 7

