# backend/bot/bot.py
"""
بوت تليجرام الموحد - نسخة كاملة مع WebApp
"""

import logging
import json
import asyncio
from telegram import Update, BotCommand, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from backend.config import BOT_TOKEN, BOT_NAME, WEBAPP_URL, ADMIN_IDS
from backend.db import Session
from backend.services.user_service import UserService

logger = logging.getLogger(__name__)


class RockyTapBot:
    """البوت الرئيسي"""
    
    def __init__(self):
        self.bot_name = BOT_NAME
        self.admin_ids = ADMIN_IDS
        self.webapp_url = WEBAPP_URL
        
        # تهيئة التطبيق
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة admin_ids إلى bot_data للوصول إليها من المعالجات
        self.application.bot_data['admin_ids'] = self.admin_ids
        
        # تهيئة المعالجات
        self._setup_handlers()
        
        logger.info(f"✅ Bot {self.bot_name} initialized")
    
    def _setup_handlers(self):
        """إعداد معالجات الأوامر"""
        from backend.bot.handlers.start import start_command, show_main_menu
        from backend.bot.handlers.callback import handle_callback
        
        # الأوامر
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # الأزرار
        self.application.add_handler(CallbackQueryHandler(handle_callback))
        
        # WebApp data
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            self.handle_webapp_data
        ))
        
        # تعيين أوامر البوت
        async def set_commands(app: Application):
            await app.bot.set_my_commands([
                BotCommand("start", "🏠 افتح التطبيق"),
                BotCommand("admin", "👑 لوحة التحكم"),
            ])
        
        self.application.post_init = set_commands
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /admin"""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("⛔ أنت لست مشرفاً")
            return
        
        keyboard = [[
            InlineKeyboardButton(
                "👑 فتح لوحة التحكم",
                web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html")
            )
        ]]
        
        await update.message.reply_text(
            f"👑 مرحباً بك في لوحة التحكم - {self.bot_name}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة البيانات من WebApp"""
        try:
            if not update.effective_message or not update.effective_message.web_app_data:
                return
            
            data = json.loads(update.effective_message.web_app_data.data)
            action = data.get('action')
            user_id = update.effective_user.id
            
            logger.info(f"📱 WebApp data: {action} from user {user_id}")
            
            # معالجة الإجراءات
            if action == 'get_user':
                await self._handle_get_user(update, user_id)
            elif action == 'convert_points':
                await self._handle_convert(update, user_id, data)
            elif action == 'watch_ad':
                await self._handle_watch_ad(update, user_id, data)
            elif action == 'spin_wheel':
                await self._handle_spin_wheel(update, user_id)
            elif action == 'redeem_code':
                await self._handle_redeem_code(update, user_id, data)
            elif action == 'request_withdraw':
                await self._handle_withdraw(update, user_id, data)
            else:
                await update.message.reply_text(json.dumps({
                    'action': 'unknown',
                    'message': 'إجراء غير معروف'
                }))
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'error',
                'message': 'خطأ في قراءة البيانات'
            }))
        except Exception as e:
            logger.error(f"Error in handle_webapp_data: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'error',
                'message': f'حدث خطأ: {str(e)}'
            }))
    
    async def _handle_get_user(self, update: Update, user_id: int):
        """جلب بيانات المستخدم"""
        db = Session()
        try:
            user = UserService.get_user(db, user_id)
            if not user:
                user = UserService.get_or_create_user(db, user_id)
            
            response = {
                'action': 'user_data',
                'success': True,
                'ton': user.balance_ton,
                'points': user.balance_points,
                'total_referrals': user.total_referrals,
                'is_blocked': user.is_blocked
            }
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_get_user: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'user_data',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def _handle_convert(self, update: Update, user_id: int, data: dict):
        """تحويل النقاط"""
        points = data.get('points', 0)
        db = Session()
        try:
            from backend.services.wallet_service import WalletService
            success, message = WalletService.convert_points(db, user_id, points)
            
            if success:
                user = UserService.get_user(db, user_id)
                response = {
                    'action': 'convert_result',
                    'success': True,
                    'message': message,
                    'ton': user.balance_ton,
                    'points': user.balance_points
                }
            else:
                response = {
                    'action': 'convert_result',
                    'success': False,
                    'message': message
                }
            
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_convert: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'convert_result',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def _handle_watch_ad(self, update: Update, user_id: int, data: dict):
        """مشاهدة إعلان"""
        reward = data.get('reward', 15)
        db = Session()
        try:
            from backend.services.ad_service import AdService
            from backend.config import DAILY_ADS_LIMIT
            
            today_ads = AdService.get_today_ads_count(db, user_id)
            
            if today_ads >= DAILY_ADS_LIMIT:
                response = {
                    'action': 'ad_result',
                    'success': False,
                    'message': f'⚠️ لقد وصلت للحد اليومي للإعلانات ({DAILY_ADS_LIMIT})!'
                }
            else:
                success, message = AdService.add_ad_watch(db, user_id, reward)
                
                if success:
                    user = UserService.get_user(db, user_id)
                    remaining = DAILY_ADS_LIMIT - (today_ads + 1)
                    response = {
                        'action': 'ad_result',
                        'success': True,
                        'reward': reward,
                        'new_points': user.balance_points,
                        'remaining': remaining,
                        'message': f'✅ +{reward} نقطة!'
                    }
                else:
                    response = {
                        'action': 'ad_result',
                        'success': False,
                        'message': message
                    }
            
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_watch_ad: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'ad_result',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def _handle_spin_wheel(self, update: Update, user_id: int):
        """عجلة الحظ"""
        db = Session()
        try:
            from backend.services.wheel_service import WheelService
            from backend.config import DAILY_WHEEL_SPINS, WHEEL_REWARDS
            import random
            
            today_spins = WheelService.get_today_spins_count(db, user_id)
            
            if today_spins >= DAILY_WHEEL_SPINS:
                response = {
                    'action': 'wheel_result',
                    'success': False,
                    'message': '⚠️ لقد استنفدت جميع محاولاتك اليوم!'
                }
            else:
                reward = random.choice(WHEEL_REWARDS)
                success = WheelService.add_spin(db, user_id, reward)
                
                if success:
                    UserService.update_balance(db, user_id, points_amount=reward, update_earned=True)
                    user = UserService.get_user(db, user_id)
                    remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
                    response = {
                        'action': 'wheel_result',
                        'success': True,
                        'reward': reward,
                        'new_points': user.balance_points,
                        'remaining': remaining,
                        'message': f'🎉 مبروك! ربحت {reward} نقطة!'
                    }
                else:
                    response = {
                        'action': 'wheel_result',
                        'success': False,
                        'message': 'حدث خطأ في اللعب'
                    }
            
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_spin_wheel: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'wheel_result',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def _handle_redeem_code(self, update: Update, user_id: int, data: dict):
        """تفعيل كود ترويجي"""
        code = data.get('code', '').upper()
        db = Session()
        try:
            from backend.services.giftcode_service import GiftCodeService
            
            success, result = GiftCodeService.use_code(db, user_id, code)
            
            if success:
                user = UserService.get_user(db, user_id)
                response = {
                    'action': 'code_result',
                    'success': True,
                    'reward_points': result['reward_points'],
                    'reward_ton': result['reward_ton'],
                    'new_points': user.balance_points,
                    'new_ton': user.balance_ton,
                    'message': f'✅ تم تفعيل الكود! حصلت على {result["reward_points"]} نقطة + {result["reward_ton"]} تون'
                }
            else:
                response = {
                    'action': 'code_result',
                    'success': False,
                    'message': result
                }
            
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_redeem_code: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'code_result',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def _handle_withdraw(self, update: Update, user_id: int, data: dict):
        """طلب سحب"""
        amount = data.get('amount', 0)
        wallet = data.get('wallet', '')
        username = data.get('username', '')
        
        db = Session()
        try:
            from backend.services.wallet_service import WalletService
            
            success, result = WalletService.create_withdrawal(db, user_id, username, amount, wallet)
            
            if success:
                user = UserService.get_user(db, user_id)
                response = {
                    'action': 'withdraw_result',
                    'success': True,
                    'withdrawal_id': result,
                    'amount': amount,
                    'new_balance': user.balance_ton,
                    'message': f'✅ تم إرسال طلب سحب بقيمة {amount} تون'
                }
            else:
                response = {
                    'action': 'withdraw_result',
                    'success': False,
                    'message': result
                }
            
            await update.message.reply_text(json.dumps(response))
        except Exception as e:
            logger.error(f"Error in _handle_withdraw: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'withdraw_result',
                'success': False,
                'message': str(e)
            }))
        finally:
            db.close()
    
    async def run_polling(self):
        """تشغيل البوت مع polling"""
        try:
            logger.info("🚀 Starting bot polling...")
            
            # بدء البوت
            await self.application.initialize()
            await self.application.start()
            
            # بدء polling
            await self.application.updater.start_polling()
            
            # الحفاظ على التشغيل
            while True:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Bot polling cancelled")
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
        finally:
            await self.application.stop()
    
    def run(self):
        """تشغيل البوت في thread منفصل"""
        asyncio.run(self.run_polling())