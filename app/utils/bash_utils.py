import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def execute_bash(script_name, *args):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script_path = os.path.join(project_root, "scripts", script_name)

    if not os.path.exists(script_path):
        logger.error(f"Script not found: {script_path}")
        return -1

    command = ["/bin/bash", script_path] + list(args)

    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()
            if stdout:
                logger.info(f"Script Output: {stdout.strip()}")
            if stderr:
                logger.warning(f"Script Warning Output: {stderr.strip()}")
            if process.returncode != 0:
                logger.warning("The script did not execute successfully.")
                return -1
    except Exception as e:
        logger.error(f"Failed to execute command: {e}")
        return -1
    return 0

