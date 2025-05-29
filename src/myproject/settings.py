from dotenv import load_dotenv
import os

load_dotenv()

ENVIRONMENT = os.getenv("MYPROJECT_ENV", "DEV").upper()
VALID_ENVS = {"DEV", "UAT", "PROD"}

if ENVIRONMENT not in VALID_ENVS:
    raise ValueError(f"Invalid environment: {ENVIRONMENT}")

IS_DEV = ENVIRONMENT == "DEV"
IS_UAT = ENVIRONMENT == "UAT"
IS_PROD = ENVIRONMENT == "PROD"
