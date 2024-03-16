from fastapi import APIRouter
from starlette import status

import services.documents

router = APIRouter(prefix="/documents", tags=["Documents"])

router.add_api_route("/upload",
                     services.documents.load_document, methods=["POST"],
                     response_model=services.documents.GenericResponse,
                     status_code=status.HTTP_201_CREATED,
                     )
