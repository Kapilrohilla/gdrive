from fastapi import APIRouter, HTTPException, Query

from app.mock_data import drive as mock_drive
from app.schemas.drive import CreateFolderPayload, UploadPayload

router = APIRouter(prefix="/drive", tags=["Drive (Mock)"])


@router.get("/user/me")
def get_current_user():
    return {"data": mock_drive.USER_PROFILE}


@router.get("/browse")
def browse(folder_id: str | None = Query(default=None)):
    return {"data": mock_drive.get_browse(folder_id)}


@router.get("/recent")
def recent():
    return {"data": mock_drive.get_recent()}


@router.get("/starred")
def starred():
    return {"data": mock_drive.get_starred()}


@router.get("/shared")
def shared():
    return {"data": mock_drive.get_shared()}


@router.get("/trash")
def trash():
    return {"data": mock_drive.get_trash()}


@router.get("/files/{file_id}")
def file_details(file_id: str):
    details = mock_drive.get_file_details(file_id)
    if not details:
        raise HTTPException(status_code=404, detail="File not found")
    return {"data": details}


@router.get("/search")
def search(q: str = Query(min_length=1)):
    return {"data": mock_drive.search_files(q)}


@router.post("/folders")
def create_folder(payload: CreateFolderPayload):
    folder = mock_drive.create_folder(payload.name, payload.parent_id)
    return {"data": folder}


@router.post("/upload")
def upload(payload: UploadPayload):
    task = mock_drive.start_upload(payload.name)
    return {"data": task}
