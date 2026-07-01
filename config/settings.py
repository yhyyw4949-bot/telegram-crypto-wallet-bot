"""
Configuration settings for the Telegram Crypto Wallet Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Database
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite or postgresql
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///wallet_bot.db")

# Blockchain
BNB_RPC_URL = os.getenv("BNB_RPC_URL", "https://bsc-dataseed1.binance.org/")
USDT_CONTRACT_ADDRESS = os.getenv("USDT_CONTRACT_ADDRESS", "0x55d398326f99059fF775485246999027B3197955")
USDT_DECIMALS = 18

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-insecure-key-change-in-production")

# Rate Limiting
RATE_LIMIT_MESSAGES_PER_MINUTE = 10
RATE_LIMIT_WITHDRAW_PER_HOUR = 5
RATE_LIMIT_TRANSFER_PER_HOUR = 20

# Wallet Limits
MAX_WALLETS_PER_USER = 2
MIN_WITHDRAWAL_AMOUNT = 1
MAX_WITHDRAWAL_AMOUNT = 10000

# Block confirmation settings
CONFIRMATIONS_REQUIRED = 3
BLOCK_CHECK_INTERVAL = 15  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/bot.log"

print(f"✓ Configuration loaded from environment")
