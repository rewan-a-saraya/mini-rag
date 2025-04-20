from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
import os.path
import aiofiles
from src.models import ResponseSignal
import logging
from src.routes.schemes.data import ProcessRequest

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    controller = DataController()
    controller.app_settings = app_settings

    project_controller = ProjectController()
    project_controller.app_settings = app_settings

    is_valid, result_signal = controller.validate_uploaded_file(file)

    if not is_valid:
        result_signal = result_signal or "Invalid file"
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
            media_type="application/json"
        )

    project_dir_path = project_controller.get_project_path(project_id=project_id)
    os.makedirs(project_dir_path, exist_ok=True)

    file_path, file_id = controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "File upload failed due to an error."},
            media_type="application/json"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id
        },
        media_type="application/json"
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
        project_id: str,
        process_request: ProcessRequest
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if not file_chunks or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value,
            }
        )

    return file_chunks
