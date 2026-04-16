# bot.py
"""
RockyTap Bot - النسخة الكاملة المتكاملة مع نظام الإعلانات المدفوعة
"""

import logging
import json
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import Database
from config import (
    BOT_TOKEN, ADMIN_IDS, WEBAPP_URL, BOT_NAME,
    POINTS_TO_TON_RATE, WITHDRAWAL_MIN,
    DAILY_ADS_LIMIT, AD_REWARD_POINTS,
    DAILY_WHEEL_SPINS, WHEEL_REWARDS
)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class RockyTapBot:
    def __init__(self):
        self.db = Database()
        self.bot_name = BOT_NAME
        self.admin_ids = ADMIN_IDS
        self.webapp_url = WEBAPP_URL
        
        # إنشاء التطبيق
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # استيراد المعالجات
        from handlers.start import StartHandler
        from handlers.balance import BalanceHandler
        from handlers.withdraw import WithdrawHandler
        from handlers.referral import ReferralHandler
        from handlers.giftcode import GiftCodeHandler
        from handlers.tasks import TasksHandler
        from handlers.ads import AdsHandler
        from handlers.wheel import WheelHandler
        from handlers.admin import AdminHandler
        from handlers.ads_posting import AdsPostingHandler
        
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
        self.ads_posting_handler = AdsPostingHandler(self)
        
        self.setup_handlers()
        
        logger.info(f"✅ {BOT_NAME} Bot initialized")
    
    def setup_handlers(self):
        """إعداد معالجات الأوامر والأزرار"""
        
        # أوامر
        self.application.add_handler(CommandHandler("start", self.start_handler.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_handler.admin_command))
        
        # معالج الأزرار الرئيسي
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # معالج WebApp
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            self.handle_webapp_data
        ))
        
        # معالج الرسائل النصية للمهام والإعلانات
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_messages
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
        elif data.startswith('complete_task_'):
            await self.tasks_handler.complete_task(update, context)
        
        # الإعلانات العادية
        elif data == 'ads_menu':
            await self.ads_handler.show_ads_menu(update, context)
        elif data == 'watch_ad':
            await self.ads_handler.watch_ad(update, context)
        
        # الإعلانات المدفوعة
        elif data == 'ads_posting_menu':
            await self.ads_posting_handler.show_ads_posting_menu(update, context)
        elif data.startswith('buy_ad_package_'):
            await self.ads_posting_handler.buy_ad_package(update, context)
        elif data == 'my_ads':
            await self.ads_posting_handler.my_ads(update, context)
        elif data == 'my_ads_list':
            await self.ads_posting_handler.my_ads_list(update, context)
        elif data.startswith('ad_manage_'):
            await self.ads_posting_handler.manage_ad(update, context)
        elif data.startswith('ad_refresh_'):
            await self.ads_posting_handler.refresh_ad_stats(update, context)
        elif data.startswith('ad_edit_'):
            await self.ads_posting_handler.edit_ad(update, context)
        elif data.startswith('ad_delete_'):
            await self.ads_posting_handler.delete_ad(update, context)
        elif data.startswith('ad_members_'):
            await self.ads_posting_handler.ad_members_list(update, context)
        elif data.startswith('ad_verify_'):
            await self.ads_posting_handler.verify_channel(update, context)
        
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
        elif data == 'share_referral':
            await self.referral_handler.share_referral(update, context)
        elif data == 'copy_referral_link':
            await self.referral_handler.copy_referral_link(update, context)
        
        # الأكواد
        elif data == 'giftcode_menu':
            await self.giftcode_handler.show_giftcode_menu(update, context)
        elif data == 'enter_giftcode':
            context.user_data['awaiting_giftcode'] = True
            await query.edit_message_text("📝 الرجاء إرسال الكود:", parse_mode='HTML')
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
        elif data == 'open_tasks_page':
            await self.tasks_handler.open_webapp(update, context)
        elif data == 'open_ads_page':
            await self.ads_handler.open_webapp(update, context)
        elif data == 'open_wheel_page':
            await self.wheel_handler.open_webapp(update, context)
    
    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة البيانات الواردة من WebApp"""
        try:
            data = json.loads(update.effective_message.web_app_data.data)
            action = data.get('action')
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            
            logger.info(f"📱 WebApp data: {action} from user {user_id}")
            
            # إجراءات الأدمن
            if action.startswith('admin_'):
                await self.admin_handler.handle_webapp_action(update, context, action, data)
                return
            
            # جلب بيانات المستخدم
            elif action == 'get_user_data':
                user_data = self.db.get_user(user_id)
                today_ads = self.db.get_today_ads_count(user_id)
                
                response = {
                    'action': 'user_data',
                    'ton': user_data['balance_ton'] if user_data else 0,
                    'points': user_data['balance_points'] if user_data else 0,
                    'total_referrals': user_data['total_referrals'] if user_data else 0,
                    'ads_watched': today_ads
                }
                await update.message.reply_text(json.dumps(response))
            
            # جلب إحصائيات الإحالات
            elif action == 'get_referral_stats':
                stats = self.db.get_user_referrals_stats(user_id)
                bot_info = await context.bot.get_me()
                referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
                
                await update.message.reply_text(json.dumps({
                    'action': 'referral_stats',
                    'total': stats['total'],
                    'granted': stats['granted'],
                    'pending': stats['pending'],
                    'total_points_earned': stats['total_points_earned'],
                    'total_ton_earned': stats['total_ton_earned'],
                    'referral_link': referral_link,
                    'referrals': stats['referrals']
                }))
            
            # تحويل النقاط
            elif action == 'convert_points':
                points = data.get('points', 0)
                success, msg = self.db.convert_points_to_ton(user_id, points)
                
                if success:
                    user_data = self.db.get_user(user_id)
                    await update.message.reply_text(json.dumps({
                        'action': 'convert_result',
                        'success': True,
                        'ton': user_data['balance_ton'],
                        'points': user_data['balance_points'],
                        'message': f'✅ تم تحويل {points} نقطة'
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'convert_result',
                        'success': False,
                        'message': f'❌ {msg}'
                    }))
            
            # مشاهدة إعلان عادي
            elif action == 'watch_ad':
                reward = data.get('reward', AD_REWARD_POINTS)
                today_ads = self.db.get_today_ads_count(user_id)
                
                if today_ads >= DAILY_ADS_LIMIT:
                    await update.message.reply_text(json.dumps({
                        'action': 'ad_result',
                        'success': False,
                        'message': f'⚠️ لقد وصلت للحد اليومي للإعلانات ({DAILY_ADS_LIMIT})!'
                    }))
                    return
                
                self.db.update_user_balance(user_id, points_amount=reward, update_earned=True)
                self.db.add_ad_watch(user_id, reward)
                
                user_data = self.db.get_user(user_id)
                remaining = DAILY_ADS_LIMIT - (today_ads + 1)
                
                await update.message.reply_text(json.dumps({
                    'action': 'ad_result',
                    'success': True,
                    'reward': reward,
                    'new_points': user_data['balance_points'],
                    'remaining': remaining
                }))
            
            # عجلة الحظ
            elif action == 'spin_wheel':
                today_spins = self.db.get_today_wheel_spins(user_id)
                
                if today_spins >= DAILY_WHEEL_SPINS:
                    await update.message.reply_text(json.dumps({
                        'action': 'wheel_result',
                        'success': False,
                        'message': '⚠️ لقد استنفدت جميع محاولاتك اليوم!'
                    }))
                    return
                
                reward = random.choice(WHEEL_REWARDS)
                self.db.update_user_balance(user_id, points_amount=reward, update_earned=True)
                self.db.add_wheel_spin(user_id, reward)
                
                user_data = self.db.get_user(user_id)
                remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
                
                await update.message.reply_text(json.dumps({
                    'action': 'wheel_result',
                    'success': True,
                    'reward': reward,
                    'new_points': user_data['balance_points'],
                    'remaining': remaining
                }))
            
            # تفعيل كود
            elif action == 'redeem_code':
                code = data.get('code', '').upper()
                success, result = self.db.use_gift_code(user_id, code)
                
                if success:
                    user_data = self.db.get_user(user_id)
                    await update.message.reply_text(json.dumps({
                        'action': 'code_result',
                        'success': True,
                        'reward_points': result['reward_points'],
                        'reward_ton': result['reward_ton'],
                        'new_points': user_data['balance_points'],
                        'new_ton': user_data['balance_ton']
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'code_result',
                        'success': False,
                        'message': f'❌ {result}'
                    }))
            
            # طلب سحب
            elif action == 'request_withdraw':
                amount = data.get('amount', 0)
                wallet = data.get('wallet', '')
                
                success, withdrawal_id = self.db.create_withdrawal(user_id, username, amount, wallet)
                
                if success:
                    await update.message.reply_text(json.dumps({
                        'action': 'withdraw_result',
                        'success': True,
                        'withdrawal_id': withdrawal_id,
                        'amount': amount
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'withdraw_result',
                        'success': False,
                        'message': f'❌ {withdrawal_id}'
                    }))
            
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON Error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    async def handle_text_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = update.effective_user.id
        
        # معالج إدخال الكود
        if context.user_data.get('awaiting_giftcode'):
            code = update.message.text.strip().upper()
            success, result = self.db.use_gift_code(user_id, code)
            
            if success:
                user_data = self.db.get_user(user_id)
                await update.message.reply_text(
                    f"✅ تم تفعيل الكود بنجاح!\n"
                    f"🎁 حصلت على: {result['reward_points']} نقطة + {result['reward_ton']:.4f} تون\n"
                    f"💰 رصيدك الحالي: {user_data['balance_ton']:.4f} تون\n"
                    f"⭐ نقاطك: {user_data['balance_points']:.0f} نقطة"
                )
            else:
                await update.message.reply_text(f"❌ {result}")
            
            context.user_data['awaiting_giftcode'] = False
            return
        
        # معالج إدخال تحويل النقاط
        if context.user_data.get('awaiting_convert'):
            try:
                points = float(update.message.text.strip())
                success, msg = self.db.convert_points_to_ton(user_id, points)
                
                if success:
                    user_data = self.db.get_user(user_id)
                    await update.message.reply_text(
                        f"✅ {msg}\n"
                        f"💰 رصيد التون: {user_data['balance_ton']:.4f}\n"
                        f"⭐ رصيد النقاط: {user_data['balance_points']:.0f}"
                    )
                else:
                    await update.message.reply_text(f"❌ {msg}")
            except ValueError:
                await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
            
            context.user_data['awaiting_convert'] = False
            return
        
        # معالج إدخال تفاصيل الإعلان
        if context.user_data.get('awaiting_ad_details'):
            await self.ads_posting_handler.handle_ad_details(update, context)
            return
        
        # معالج إدخال تعديل الإعلان
        if context.user_data.get('awaiting_ad_edit'):
            await self.ads_posting_handler.handle_ad_edit(update, context)
            return
        
        # معالج إدخال إنشاء مهمة (للأدمن)
        if context.user_data.get('awaiting_task_creation'):
            await self.admin_handler.handle_task_creation(update, context)
            return
        
        # معالج إدخال حذف مهمة (للأدمن)
        if context.user_data.get('awaiting_task_deletion'):
            await self.admin_handler.handle_task_deletion(update, context)
            return
        
        # رسالة عادية
        await update.message.reply_text(
            "❓ أمر غير معروف. استخدم /start للبدء",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data='back_to_main')
            ]])
        )
    
    def run(self):
        """تشغيل البوت"""
        print("=" * 50)
        print(f"🚀 {self.bot_name} Bot is running...")
        print(f"📱 WebApp URL: {self.webapp_url}")
        print(f"👑 Admins: {self.admin_ids}")
        print("=" * 50)
        
        self.application.run_polling(allowed_updates=['message', 'callback_query'])


if __name__ == "__main__":
    bot = RockyTapBot()
    bot.run()