from fastapi import APIRouter, HTTPException, Query

from app.mock_data import drive as mock_drive
from app.schemas.endpoints.drive import (
    CreateFolderPayload,
    DriveDataResponse,
    UploadPayload,
)

router = APIRouter(prefix="/drive", tags=["Drive (Mock)"])


@router.get("/user/me", response_model=DriveDataResponse)
def get_current_user():
    return {"data": mock_drive.USER_PROFILE}


@router.get("/browse", response_model=DriveDataResponse)
def browse(folder_id: str | None = Query(default=None)):
    return {"data": mock_drive.get_browse(folder_id)}


@router.get("/recent", response_model=DriveDataResponse)
def recent():
    return {"data": mock_drive.get_recent()}


@router.get("/starred", response_model=DriveDataResponse)
def starred():
    return {"data": mock_drive.get_starred()}


@router.get("/shared", response_model=DriveDataResponse)
def shared():
    return {"data": mock_drive.get_shared()}


@router.get("/trash", response_model=DriveDataResponse)
def trash():
    return {"data": mock_drive.get_trash()}


@router.get("/files/{file_id}", response_model=DriveDataResponse)
def file_details(file_id: str):
    details = mock_drive.get_file_details(file_id)
    if not details:
        raise HTTPException(status_code=404, detail="File not found")
    return {"data": details}


@router.get("/search", response_model=DriveDataResponse)
def search(q: str = Query(min_length=1)):
    return {"data": mock_drive.search_files(q)}


@router.post("/folders", response_model=DriveDataResponse)
def create_folder(payload: CreateFolderPayload):
    folder = mock_drive.create_folder(payload.name, payload.parent_id)
    return {"data": folder}


@router.post("/upload", response_model=DriveDataResponse)
def upload(payload: UploadPayload):
    task = mock_drive.start_upload(payload.name)
    return {"data": task}
