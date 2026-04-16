# main.py
"""
البوت الرئيسي - RockyTap
"""

import sys
import os
import logging
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS, BOT_NAME, WELCOME_MESSAGE, WEBAPP_URL
from database import Database
from handlers.start import StartHandler
from handlers.balance import BalanceHandler
from handlers.withdraw import WithdrawHandler
from handlers.referral import ReferralHandler
from handlers.giftcode import GiftCodeHandler
from handlers.tasks import TasksHandler
from handlers.ads import AdsHandler
from handlers.wheel import WheelHandler
from handlers.admin import AdminHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class RockyTapBot:
    def __init__(self):
        self.db = Database()
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # تهيئة المعالجات
        self.start_handler = StartHandler(self)
        self.balance_handler = BalanceHandler(self)
        self.withdraw_handler = WithdrawHandler(self)
        self.referral_handler = ReferralHandler(self)
        self.giftcode_handler = GiftCodeHandler(self)
        self.tasks_handler = TasksHandler(self)
        self.ads_handler = AdsHandler(self)
        self.wheel_handler = WheelHandler(self)
        self.admin_handler = AdminHandler(self)
        
        self.setup_handlers()
        
        logger.info(f"✅ Bot {BOT_NAME} initialized")
    
    def setup_handlers(self):
        """إعداد معالجات الأوامر والأزرار"""
        
        # أوامر
        self.application.add_handler(CommandHandler("start", self.start_handler.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_handler.admin_command))
        
        # معالج الأزرار
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # معالج WebApp
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            self.handle_webapp_data
        ))
        
        # تعيين أوامر البوت
        self.application.bot.set_my_commands([
            BotCommand("start", "🏠 القائمة الرئيسية"),
            BotCommand("admin", "👑 لوحة التحكم"),
        ])
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار الموحد"""
        query = update.callback_query
        data = query.data
        
        await query.answer()
        
        # قائمة المهام
        if data == 'tasks_menu':
            await self.tasks_handler.show_tasks_menu(update, context)
        
        # الإعلانات
        elif data == 'ads_menu':
            await self.ads_handler.show_ads_menu(update, context)
        elif data == 'watch_ad':
            await self.ads_handler.watch_ad(update, context)
        
        # عجلة الحظ
        elif data == 'wheel_menu':
            await self.wheel_handler.show_wheel_menu(update, context)
        elif data == 'spin_wheel':
            await self.wheel_handler.spin_wheel(update, context)
        
        # الرصيد
        elif data == 'balance_menu':
            await self.balance_handler.show_balance(update, context)
        elif data == 'convert_points':
            await self.balance_handler.start_convert(update, context)
        
        # السحب
        elif data == 'withdraw_menu':
            await self.withdraw_handler.show_withdraw_menu(update, context)
        elif data == 'withdraw_history':
            await self.withdraw_handler.show_withdraw_history(update, context)
        
        # الإحالات
        elif data == 'referral_menu':
            await self.referral_handler.show_referral_menu(update, context)
        
        # الأكواد
        elif data == 'giftcode_menu':
            await self.giftcode_handler.show_giftcode_menu(update, context)
        elif data == 'giftcode_history':
            await self.giftcode_handler.show_giftcode_history(update, context)
        
        # الأدمن
        elif data.startswith('admin_'):
            await self.admin_handler.handle_admin_callback(update, context)
        
        # القائمة الرئيسية
        elif data == 'back_to_main':
            await self.start_handler.show_main_menu(update, context)
        
        # صفحة الويب
        elif data == 'open_withdraw_page':
            await self.withdraw_handler.open_webapp(update, context)
        elif data == 'open_referral_page':
            await self.referral_handler.open_webapp(update, context)
        elif data == 'open_giftcode_page':
            await self.giftcode_handler.open_webapp(update, context)
    
    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة البيانات الواردة من WebApp"""
        from utils.webapp_handler import handle_webapp_data
        await handle_webapp_data(self, update, context)
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 Starting bot...")
        self.application.run_polling(allowed_updates=['message', 'callback_query'])


if __name__ == "__main__":
    bot = RockyTapBot()
    bot.run()