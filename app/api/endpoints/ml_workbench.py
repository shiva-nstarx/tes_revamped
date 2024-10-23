from fastapi import APIRouter, BackgroundTasks
from app.models import DeployMLWorkbench
from app.services import deploy_ml_workbench_service

router = APIRouter()


@router.post("/deploy")
async def deploy_ml_workbench(deploy_payload: DeployMLWorkbench, background_tasks: BackgroundTasks):
    background_tasks.add_task(deploy_ml_workbench_service, deploy_payload)
    return {"message": f"ML Workbench deployment started successfully for partner_id: {deploy_payload.partner_id}"}
