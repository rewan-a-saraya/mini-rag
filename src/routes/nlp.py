from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from src.models import ResponseSignal
from src.routes.schemes.nlp import PushRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.controllers import NLPController
from src.models.enums import ResponseEnums
import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix= "/api/v1/nlp",
    tags= ["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str,push_request: PushRequest ):

    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    chunk_model = await  ChunkModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id= project_id
    )

    if not project :
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    nlp_controller = NLPController(
        vectordb_client= request.app.vectordb_client,
        generation_client= request.app.generation_client,
        embedding_client= request.app.embedding_client,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records :
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids,
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

    #chunks = chunk_model.get_project_chunks(project_id=project.project_id)