import datetime
import io
import multiprocessing

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue
from typing import Annotated, Union

import cv2
import numpy as np
from fastapi import UploadFile, Depends, BackgroundTasks
from pydantic import BaseModel
from pypdf import PdfReader, PageObject

import services.image_processing
from models.user import User
from services import users, storage
from services.storage import UploadResult


class GenericResponse(BaseModel):
    message: str


queue: Queue = multiprocessing.Queue()


def stop():
    queue.put({"signal": "STOP"})


def id_filter(page: PageObject) -> bool:
    print("ID")
    if len(page.images) == 0 or len(page.images) > 2:
        return False

    front = page.images[0].data
    if len(page.images) == 1:
        return services.image_processing.detect_face(front)
    back = page.images[1].data
    return services.image_processing.detect_face(front) or services.image_processing.detect_face(back)


def job_certificate_filter(page: PageObject) -> bool:
    text = page.extract_text().lower()
    return "certificado" in text and "laboral" in text


def funds_certificate(page: PageObject) -> bool:
    text = page.extract_text().lower()
    return "ingresos" in text and "egresos" in text and f"{datetime.date.today().year - 1}" in text


def send_to_review():
    print("Sending to review")


def reject_documents(reason: str) -> None:
    print(f"Reject file. Reason: {reason}")


def process_file(file_content: bytes):
    pdf = PdfReader(io.BytesIO(file_content))
    pages = pdf.pages
    if len(pages) != 3:
        return reject_documents("Invalid format")

    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(id_filter, pages[0])
        future2 = executor.submit(job_certificate_filter, pages[1])
        future3 = executor.submit(funds_certificate, pages[2])

        filters_results = [future1.result(), future2.result(), future3.result()]

    if all(result for result in filters_results):
        return send_to_review()
    if not filters_results[0]:
        return reject_documents("Invalid ID document")
    if not filters_results[1]:
        return reject_documents("Invalid job certificate")

    return reject_documents("Invalid funds certificate")


def documents_processor():
    print("Processor initialized")
    while True:
        info = queue.get(block=True, timeout=None)
        if not info.get("uploaded", False):
            break
        process_file(info["file_content"])


def enqueue_document(file: UploadResult, file_content: bytes):
    queue.put({"uploaded": file, "file_content": file_content})


async def load_document(
    background_tasks: BackgroundTasks,
    file: Union[UploadFile | None] = None,
    user: Annotated[Union[None | User], Depends(users.mock_user)] = None,
):
    if file:
        file_content = await file.read()
        result = await storage.save_document(file, file_content, user)
        background_tasks.add_task(enqueue_document, result, file_content)
    return GenericResponse(message="Document saved successfully")
