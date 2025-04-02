"""
Deployment script for NOVAXA Dashboard and Telegram Bot
"""

import os
import subprocess
import logging

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def check_prerequisites():
    logger.info("Checking prerequisites...")

    # Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        logger.info("✅ Docker is installed")
    except Exception:
        logger.error("❌ Docker is not installed.")
        return False

    # Docker Compose
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        logger.info("✅ Docker Compose is installed")
    except Exception:
        logger.error("❌ Docker Compose is not installed.")
        return False

    return True

def deploy():
    logger.info("Preparing deployment...")

    # Check deployment folder
    if not os.path.exists("deployment"):
        logger.error("❌ 'deployment' directory not found. Create it first.")
        return

    # Run docker-compose
    try:
        subprocess.run(["docker-compose", "-f", "deployment/docker-compose.yml", "up", "-d"], check=True)
        logger.info("✅ Deployment started.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Deployment failed: {e}")

if __name__ == "__main__":
    if check_prerequisites():
        deploy()
