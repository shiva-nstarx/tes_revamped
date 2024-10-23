from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import ZonePartner
from app.services import create_zone_partner_service, delete_zone_partner_service, redeploy_zone_partner_service

router = APIRouter()


@router.post("/")
async def create_zone_partner(zone_partner: ZonePartner, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(create_zone_partner_service, zone_partner)
        return {"message": f"Zone partner creation started for partner_id: {zone_partner.partner_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{partner_id}")
async def update_zone_partner(partner_id: str, zone_partner: ZonePartner):
    return {"message": "Not implemented. Zone partner updated successfully"}


@router.delete("/{partner_id}")
async def delete_zone_partner(partner_id: str, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(delete_zone_partner_service, partner_id)
        return {"message": f"Zone partner deletion started for partner_id: {partner_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/re-deploy/{partner_id}")
async def redeploy_pz(partner_id: str, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(redeploy_zone_partner_service, partner_id)
        return {"message": f"Redeployment of Zone partner started for partner_id: {partner_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
