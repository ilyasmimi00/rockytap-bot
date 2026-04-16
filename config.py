# config.py
"""
إعدادات البوت - النسخة النهائية مع Cloudflare
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== إعدادات البوت الأساسية ====================

# توكن البوت
BOT_TOKEN = os.getenv('BOT_TOKEN', '7711921898:AAHjbn3KpOU5vWcr-NZc4B9E5MQ6nNaV_aM')

# معرفات الأدمن (ضع معرفات الأدمن هنا مفصولة بفواصل)
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '8268443100').split(',')]

# رابط التطبيق على Cloudflare Pages
WEBAPP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev'

# اسم البوت
BOT_NAME = "RockyTap"

# ==================== إعدادات العملات ====================

POINTS_TO_TON_RATE = 10  # 10 نقاط = 1 تون

# ==================== إعدادات السحب ====================

WITHDRAWAL_MIN = 0.02  # الحد الأدنى للسحب بالتون

# ==================== إعدادات الإعلانات ====================

DAILY_ADS_LIMIT = 10     # الحد اليومي للإعلانات
AD_REWARD_POINTS = 15    # مكافأة الإعلان بالنقاط

# ==================== إعدادات عجلة الحظ ====================

DAILY_WHEEL_SPINS = 3                    # المحاولات اليومية
WHEEL_REWARDS = [5, 10, 15, 20, 25, 50, 75, 100]  # جوائز عجلة الحظ

# ==================== إعدادات الإحالات ====================

REFERRAL_SETTINGS = {
    'reward_type': 'both',      # 'points', 'ton', 'both'
    'points_value': 100,        # قيمة المكافأة بالنقاط
    'ton_value': 0.01,          # قيمة المكافأة بالتون
    'required_tasks': 6,        # عدد المهام المطلوبة للمدعو
    'auto_grant': True          # منح المكافأة تلقائياً
}

# ==================== إعدادات الأكواد ====================

GIFTCODE_SETTINGS = {
    'min_amount': 0.0001,
    'max_amount': 3.0,
    'min_uses': 10,
    'max_uses': 1000
}