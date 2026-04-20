# backend/config.py
"""
إعدادات البوت - نسخة منظمة للمشروع الجديد
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env في جذر المشروع
load_dotenv()

# ==================== إعدادات البوت الأساسية ====================

BOT_TOKEN = os.getenv('BOT_TOKEN', '8446018051:AAGOFSu5hsIAyUoVlXnooX3iFGOK4jeOrqI')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required in .env file")

# معرفات الأدمن
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '8268443100').split(',') if id.strip()]

# بيئة التشغيل
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# رابط التطبيق - استخدم رابط Cloudflare مباشرة
WEBAPP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev'

BOT_NAME = os.getenv('BOT_NAME', 'RockyTap')

# ==================== إعدادات قاعدة البيانات ====================

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(DATA_DIR, "bot_database.db")}')

# ==================== إعدادات العملات ====================

POINTS_TO_TON_RATE = float(os.getenv('POINTS_TO_TON_RATE', '10'))

# ==================== إعدادات السحب ====================

WITHDRAWAL_MIN = float(os.getenv('WITHDRAWAL_MIN', '0.02'))

# ==================== إعدادات الإعلانات ====================

DAILY_ADS_LIMIT = int(os.getenv('DAILY_ADS_LIMIT', '10'))
AD_REWARD_POINTS = int(os.getenv('AD_REWARD_POINTS', '15'))

# ==================== إعدادات عجلة الحظ ====================

DAILY_WHEEL_SPINS = int(os.getenv('DAILY_WHEEL_SPINS', '3'))
WHEEL_REWARDS = [int(x.strip()) for x in os.getenv('WHEEL_REWARDS', '5,10,15,20,25,50,75,100').split(',')]

# ==================== إعدادات API ====================

API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))

# ==================== إعدادات التسجيل ====================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

print(f"✅ Config loaded - Environment: {ENVIRONMENT}")
print(f"✅ WebApp URL: {WEBAPP_URL}")
print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")