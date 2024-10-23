import json
import os
from datetime import datetime

from app.core.config import log_level
from app.core.logging import setup_logger
from app.core.constants import STATE_PATH
from app.models import ZonePartner

logger = setup_logger(__name__, log_level)


def save_zone_partner_payload(zone_partner):
    directory = os.path.join(STATE_PATH, str(zone_partner.partner_id))
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"zone_partner_{zone_partner.partner_id}.json")
    with open(filename, 'w') as f:
        json.dump(zone_partner.dict(), f)
    logger.info(f"Zone partner saved to file: {filename}")


def update_status(partner_id, key, value):
    directory = os.path.join(STATE_PATH, str(partner_id), "status")
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"status_{partner_id}.json")

    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        data["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data[key] = value

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        logger.info(f"Status updated for partner_id {partner_id}: {key} = {value}")
    except Exception as e:
        logger.error(f"Error updating status for partner_id {partner_id}: {str(e)}")


def load_zone_partner_json(partner_id: str) -> ZonePartner:
    filename = os.path.join(STATE_PATH, str(partner_id), f"zone_partner_{partner_id}.json")
    if not os.path.exists(filename):
        logger.error(f"No saved zone partner found with id: {partner_id}")
        return None
    with open(filename, 'r') as f:
        zone_partner_dict = json.load(f)
    return ZonePartner(**zone_partner_dict)

def load_status_json(partner_id: str):
    filename = os.path.join(
        STATE_PATH, f"{partner_id}", f"status", f"status_{partner_id}.json"
    )
    if not os.path.exists(filename):
        logger.error(f"No status file found with id: {partner_id}")
        return None
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error loading status JSON: {str(e)}")
        return None