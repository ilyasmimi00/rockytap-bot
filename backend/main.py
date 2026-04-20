# backend/main.py
"""
نقطة الدخول الرئيسية - تجمع بين FastAPI و Telegram Bot
"""

import logging
import threading
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.config import API_HOST, API_PORT, ENVIRONMENT, WEBAPP_URL
from backend.api.router import api_router
from backend.bot.bot import RockyTapBot

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ==================== تهيئة البوت ====================

bot = RockyTapBot()


def run_bot():
    """تشغيل البوت في thread منفصل"""
    try:
        # إنشاء event loop جديد لهذا الـ thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run_polling())
    except Exception as e:
        logger.error(f"Bot thread error: {e}")


# ==================== تهيئة FastAPI ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    logger.info("🚀 Starting FastAPI server...")
    
    # بدء البوت في thread منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🤖 Bot started in background thread")
    
    yield
    
    logger.info("👋 Shutting down...")


app = FastAPI(
    title="RockyTap API",
    description="API for RockyTap Telegram Bot",
    version="2.0.0",
    lifespan=lifespan
)

# إضافة CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ENVIRONMENT == "development" else [WEBAPP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إضافة المسارات
app.include_router(api_router)

# خدمة الملفات الثابتة (Frontend) - إنشاء مجلد فارغ إذا لم يكن موجوداً
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path, exist_ok=True)
    # إنشاء ملف index.html بسيط
    with open(os.path.join(frontend_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RockyTap</title>
    <style>
        body { background: linear-gradient(135deg, #0A0F1A 0%, #05080F 100%); font-family: Arial, sans-serif; color: white; text-align: center; padding: 50px; }
        h1 { color: #00BFFF; }
    </style>
</head>
<body>
    <h1>🎮 RockyTap</h1>
    <p>API is running. Frontend files will be added later.</p>
    <p>📡 API: /api/health</p>
</body>
</html>
        """)

try:
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"✅ Frontend mounted from: {frontend_path}")
except Exception as e:
    logger.warning(f"Could not mount frontend directory: {e}")


# ==================== مسار إضافي للتحقق ====================

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "bot_running": True, "version": "2.0.0"}


# ==================== التشغيل ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 50)
    logger.info(f"🎯 RockyTap v2.0")
    logger.info(f"📡 API: http://{API_HOST}:{API_PORT}")
    logger.info(f"🌐 WebApp: {WEBAPP_URL}")
    logger.info(f"🤖 Bot: @{bot.bot_name}")
    logger.info("=" * 50)
    
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=ENVIRONMENT == "development"
    )