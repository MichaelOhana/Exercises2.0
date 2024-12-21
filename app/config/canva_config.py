import os
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the absolute paths to possible .env files
root_env_path = Path(__file__).resolve().parent.parent.parent / '.env'
app_env_path = Path(__file__).resolve().parent.parent / '.env'

logger.debug(f"Looking for root .env file at: {root_env_path}")
logger.debug(f"Root .env file exists: {root_env_path.exists()}")
logger.debug(f"Looking for app .env file at: {app_env_path}")
logger.debug(f"App .env file exists: {app_env_path.exists()}")

# Try to load from both locations
load_dotenv(root_env_path)
load_dotenv(app_env_path)

# Get credentials from environment variables
CANVA_CLIENT_ID = os.getenv('CANVA_CLIENT_ID')
logger.debug(f"Loaded Canva Client ID: {CANVA_CLIENT_ID}")

if not CANVA_CLIENT_ID:
    logger.error("CANVA_CLIENT_ID not found in environment variables")
    logger.debug(f"All environment variables: {dict(os.environ)}")
    raise ValueError("CANVA_CLIENT_ID not found in environment variables")

CANVA_CLIENT_SECRET = os.getenv('CANVA_CLIENT_SECRET')
logger.debug(f"Loaded Canva Client Secret: {'*' * len(CANVA_CLIENT_SECRET) if CANVA_CLIENT_SECRET else 'None'}")

if not CANVA_CLIENT_SECRET:
    logger.error("CANVA_CLIENT_SECRET not found in environment variables")
    raise ValueError("CANVA_CLIENT_SECRET not found in environment variables")

# API endpoints
CANVA_API_BASE_URL = "https://api.canva.com"
CANVA_AUTH_URL = "https://www.canva.com/oauth/authorize"
CANVA_TOKEN_URL = "https://api.canva.com/oauth/token"
CANVA_DESIGN_API = f"{CANVA_API_BASE_URL}/v1/designs"
CANVA_BRANDS_API = f"{CANVA_API_BASE_URL}/v1/brands"

# OAuth2 settings
CANVA_REDIRECT_URL = "http://127.0.0.1:3001/oauth/redirect"
CANVA_RETURN_URL = "http://127.0.0.1:3001/return-nav"

# Log final configuration
logger.debug("Final Canva Configuration:")
logger.debug(f"API Base URL: {CANVA_API_BASE_URL}")
logger.debug(f"Auth URL: {CANVA_AUTH_URL}")
logger.debug(f"Redirect URL: {CANVA_REDIRECT_URL}")
logger.debug(f"Return URL: {CANVA_RETURN_URL}")