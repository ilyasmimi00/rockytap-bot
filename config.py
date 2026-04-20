# config.py - النسخة المصححة
"""
إعدادات البوت - النسخة المصححة
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== إعدادات البوت الأساسية ====================

# توكن البوت
BOT_TOKEN = os.getenv('BOT_TOKEN', '7711921898:AAHjbn3KpOU5vWcr-NZc4B9E5MQ6nNaV_aM')

# معرفات الأدمن (ضع معرفات الأدمن هنا مفصولة بفواصل)
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '8268443100').split(',') if id.strip()]

# رابط التطبيق - يدعم التطوير المحلي والإنتاج
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ENVIRONMENT == 'production':
    WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://rockytap-bot.elias-guerbas.workers.dev')
else:
    WEBAPP_URL = os.getenv('WEBAPP_URL_DEV', 'http://localhost:5000')

# اسم البوت
BOT_NAME = os.getenv('BOT_NAME', 'RockyTap')

# ==================== إعدادات قاعدة البيانات ====================

# إنشاء مجلد data إذا لم يكن موجوداً
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
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

# ==================== إعدادات الإحالات ====================

REFERRAL_SETTINGS = {
    'reward_type': os.getenv('REFERRAL_REWARD_TYPE', 'both'),
    'points_value': int(os.getenv('REFERRAL_POINTS_VALUE', '100')),
    'ton_value': float(os.getenv('REFERRAL_TON_VALUE', '0.01')),
    'required_tasks': int(os.getenv('REFERRAL_REQUIRED_TASKS', '6')),
    'auto_grant': os.getenv('REFERRAL_AUTO_GRANT', 'True').lower() == 'true'
}

# ==================== إعدادات الأكواد ====================

GIFTCODE_SETTINGS = {
    'min_amount': float(os.getenv('GIFTCODE_MIN_AMOUNT', '0.0001')),
    'max_amount': float(os.getenv('GIFTCODE_MAX_AMOUNT', '3.0')),
    'min_uses': int(os.getenv('GIFTCODE_MIN_USES', '10')),
    'max_uses': int(os.getenv('GIFTCODE_MAX_USES', '1000'))
}

# ==================== إعدادات إضافية ====================

# مستوى التسجيل
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# تحقق من صحة الإعدادات الأساسية
if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
    print("⚠️ WARNING: BOT_TOKEN not set properly!")

print(f"✅ Config loaded - Environment: {ENVIRONMENT}")
print(f"✅ Database: {DATABASE_URL}")
print(f"✅ WebApp URL: {WEBAPP_URL}")