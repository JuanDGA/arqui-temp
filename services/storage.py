import datetime
import io
import json
import time
from functools import lru_cache
from typing import Union, Annotated, TypedDict

from fastapi import UploadFile, Depends, HTTPException
from google.cloud.storage import Client, Bucket
from pydantic.v1 import BaseSettings

from models.user import User
from services import users

from google.cloud import storage as gcs


class CloudStorageSettings(BaseSettings):
    credentials_path: str = "credentials.json"

@lru_cache()
def get_gcc_client() -> Client:
    return gcs.Client.from_service_account_json("credentials.json")


@lru_cache
def get_storage_client() -> Bucket:
    return get_gcc_client().bucket("documents-losalpes")


class UploadResult(TypedDict):
    status: bool
    destination_path: str


async def save_document(
        file: Union[UploadFile | None],
        file_content: bytes,
        user: Annotated[Union[None | User], Depends(users.mock_user)] = None
) -> UploadResult:
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if file is None:
        raise HTTPException(status_code=400, detail="A file is required")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = f"{user.id}_{time.time_ns()}_{file.filename}"

    blob = get_storage_client().blob(file_path)
    f = io.BytesIO(file_content)
    f.name = file.filename
    blob.upload_from_file(f)
    f.close()

    return {"status": True, "destination_path": file_path}
