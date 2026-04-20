# config.py - النسخة النهائية المصححة
"""
إعدادات البوت - RockyTap
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== إعدادات البوت الأساسية ====================

# توكن البوت الصحيح
BOT_TOKEN = '8446018051:AAGOFSu5hsIAyUoVlXnooX3iFGOK4jeOrqI'

# معرفات الأدمن
ADMIN_IDS = [8268443100]

# رابط التطبيق (Cloudflare)
WEBAPP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev'

# اسم البوت
BOT_NAME = 'RockyTap'

# بيئة التشغيل
ENVIRONMENT = 'production'

# ==================== إعدادات API ====================

API_HOST = '0.0.0.0'
API_PORT = 8080

# ==================== إعدادات قاعدة البيانات ====================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f'sqlite:///{os.path.join(DATA_DIR, "bot_database.db")}'

# ==================== إعدادات العملات ====================

POINTS_TO_TON_RATE = 10

# ==================== إعدادات السحب ====================

WITHDRAWAL_MIN = 0.02

# ==================== إعدادات الإعلانات ====================

DAILY_ADS_LIMIT = 10
AD_REWARD_POINTS = 15

# ==================== إعدادات عجلة الحظ ====================

DAILY_WHEEL_SPINS = 3
WHEEL_REWARDS = [5, 10, 15, 20, 25, 50, 75, 100]

# ==================== إعدادات الإحالات ====================

REFERRAL_SETTINGS = {
    'reward_type': 'both',
    'points_value': 100,
    'ton_value': 0.01,
    'required_tasks': 6,
    'auto_grant': True
}

# ==================== إعدادات الأكواد ====================

GIFTCODE_SETTINGS = {
    'min_amount': 0.0001,
    'max_amount': 3.0,
    'min_uses': 10,
    'max_uses': 1000
}

# ==================== إعدادات إضافية ====================

LOG_LEVEL = 'INFO'

print(f"✅ Config loaded")
print(f"✅ WebApp URL: {WEBAPP_URL}")
print(f"✅ API Port: {API_PORT}")