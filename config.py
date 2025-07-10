import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",")]

# Stability AI
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_ENGINE = os.getenv("STABILITY_ENGINE", "stable-diffusion-xl-1024-v1-0")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cosplay.db")

# Payments
TON_API_KEY = os.getenv("TON_API_KEY")
TON_WALLET = os.getenv("TON_WALLET")

# Paths
TEMP_DIR = "temp"
RESULTS_DIR = "results"