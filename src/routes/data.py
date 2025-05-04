from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from numpy.core.records import record
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
import os.path
import aiofiles
from src.models.ChunkModel import ChunkModel
from src.models.enums.ResponseEnums import ResponseSignal
import logging
from src.routes.schemes.data import ProcessRequest
from src.models.AssetModel import AssetModel
from src.models.ProjectModel import ProjectModel
from src.models.db_schemes import DataChunk, Asset
from src.models.enums.AssetTypeEnum import AssetTypeEnum


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    if not hasattr(request.app, "db_client"):
        logger.error("Database client is not initialized in app")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "Database client not initialized."},
            media_type="application/json"
        )

    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

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

    #store the asset into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
    asset_project_id = project.id,
    asset_type = AssetTypeEnum.FILE.value,
    asset_name= file_id,
    asset_size = os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset= asset_resource)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
        },
        media_type="application/json"
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
        request: Request,
        project_id: str,
        process_request: ProcessRequest
):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id= project.id,
            asset_name= process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }

    #else:


    project_files =await asset_model.get_all_project_assets(
        asset_project_id= project.id,
        asset_type= AssetTypeEnum.FILE.value,
    )

    project_files_ids = {
        record.id : record.asset_name
        for record in project_files
    }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )

    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    for asset_id, file_id in project_files_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file : {file_id}")
            continue

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

        file_chunks_records = [
            DataChunk(
                chunk_text = chunk.page_content,
                chunk_metadata = chunk.metadata,
                chunk_order = i+1,
                chunk_project_id = project.id,
                chunk_asset_id= asset_id

            )
            for i , chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks= file_chunks_records)

        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files" : no_files
        }
    )



