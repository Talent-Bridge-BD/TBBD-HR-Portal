from fastapi import APIRouter
from repositories.recruitment_pipeline import RecruitmentPipelineRepository

router = APIRouter(
    prefix="/api/recruitment",
    tags=["recruitment"],
)

_repository = RecruitmentPipelineRepository()

@router.get("/pipeline")
def get_pipeline():
    return _repository.get_pipeline_counts()
