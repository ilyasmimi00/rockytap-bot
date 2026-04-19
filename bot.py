# bot.py - النسخة الموحدة مع API مدمج (مصححة)
"""
RockyTap Bot - Unified Version
يجمع بين بوت تليجرام و API في ملف واحد
"""

import logging
import json
import os
import random
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
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
    """البوت الموحد مع API مدمج"""
    
    def __init__(self):
        # تهيئة قاعدة البيانات
        self.db = Database()
        
        # إعدادات البوت
        self.bot_name = BOT_NAME
        self.admin_ids = ADMIN_IDS
        self.webapp_url = WEBAPP_URL
        
        # تهيئة تطبيق تليجرام
        self.telegram_app = Application.builder().token(BOT_TOKEN).build()
        
        # تهيئة Flask API
        self.flask_app = Flask(__name__, static_folder='public', static_url_path='')
        CORS(self.flask_app)
        
        # تهيئة المعالجات
        self.init_handlers()
        
        # إعداد مسارات API
        self.setup_api_routes()
        
        # إعداد مسارات الملفات الثابتة
        self.setup_static_routes()
        
        logger.info(f"✅ {BOT_NAME} Bot initialized with integrated API")
    
    def init_handlers(self):
        """تهيئة معالجات البوت"""
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
        
        self.setup_telegram_handlers()
    
    def setup_telegram_handlers(self):
        """إعداد معالجات أوامر تليجرام"""
        self.telegram_app.add_handler(CommandHandler("start", self.start_handler.start_command))
        self.telegram_app.add_handler(CommandHandler("admin", self.admin_handler.admin_command))
        self.telegram_app.add_handler(CallbackQueryHandler(self.handle_telegram_callback))
        self.telegram_app.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            self.handle_webapp_data
        ))
        self.telegram_app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_messages
        ))
        
        # تعيين أوامر البوت
        async def set_commands(app: Application):
            await app.bot.set_my_commands([
                BotCommand("start", "🏠 افتح التطبيق"),
                BotCommand("admin", "👑 لوحة التحكم"),
            ])
        
        self.telegram_app.post_init = set_commands
    
    # ==================== مسارات API ====================
    
    def setup_api_routes(self):
        """إعداد جميع مسارات API"""
        
        @self.flask_app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'bot_running': True,
                'db_connected': True
            })
        
        @self.flask_app.route('/api/user', methods=['GET'])
        def get_user():
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'user_id مطلوب'})
            
            try:
                user = self.db.get_user(int(user_id))
                if not user:
                    return jsonify({'success': False, 'message': 'المستخدم غير موجود'})
                
                today_ads = self.db.get_today_ads_count(int(user_id))
                
                return jsonify({
                    'success': True,
                    'ton': user['balance_ton'],
                    'points': user['balance_points'],
                    'total_referrals': user['total_referrals'],
                    'ads_watched': today_ads,
                    'daily_limit': DAILY_ADS_LIMIT
                })
            except Exception as e:
                logger.error(f"API Error /user: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.route('/api/tasks', methods=['GET'])
        def get_tasks():
            try:
                tasks = self.db.get_active_tasks()
                return jsonify({'success': True, 'tasks': tasks})
            except Exception as e:
                logger.error(f"API Error /tasks: {e}")
                return jsonify({'success': False, 'message': str(e), 'tasks': []})
        
        @self.flask_app.route('/api/complete_task', methods=['POST'])
        def complete_task():
            data = request.get_json()
            user_id = data.get('user_id')
            task_id = data.get('task_id')
            reward = data.get('reward', 0)
            
            try:
                self.db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
                if task_id:
                    self.db.complete_user_task(int(user_id), int(task_id))
                
                user = self.db.get_user(int(user_id))
                
                return jsonify({
                    'success': True,
                    'message': f'✅ +{reward} نقطة',
                    'new_points': user['balance_points']
                })
            except Exception as e:
                logger.error(f"API Error /complete_task: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.route('/api/ads', methods=['GET'])
        def get_ads():
            user_id = request.args.get('user_id')
            
            try:
                today_ads = self.db.get_today_ads_count(int(user_id)) if user_id else 0
                
                ads = [
                    {'id': 1, 'name': 'AdsGram', 'reward': AD_REWARD_POINTS, 'icon': '📺'},
                    {'id': 2, 'name': 'MontageWeb', 'reward': AD_REWARD_POINTS, 'icon': '🎬'},
                    {'id': 3, 'name': 'GigaBI Display', 'reward': AD_REWARD_POINTS, 'icon': '🖥️'},
                    {'id': 4, 'name': 'شركة 4', 'reward': AD_REWARD_POINTS, 'icon': '📱'}
                ]
                
                return jsonify({
                    'success': True,
                    'ads': ads,
                    'watched_today': today_ads,
                    'daily_limit': DAILY_ADS_LIMIT
                })
            except Exception as e:
                logger.error(f"API Error /ads: {e}")
                return jsonify({'success': False, 'message': str(e), 'ads': []})
        
        @self.flask_app.route('/api/watch_ad', methods=['POST'])
        def watch_ad():
            data = request.get_json()
            user_id = data.get('user_id')
            reward = data.get('reward', AD_REWARD_POINTS)
            
            try:
                today_ads = self.db.get_today_ads_count(int(user_id))
                
                if today_ads >= DAILY_ADS_LIMIT:
                    return jsonify({
                        'success': False,
                        'message': f'⚠️ لقد وصلت للحد اليومي للإعلانات ({DAILY_ADS_LIMIT})!'
                    })
                
                self.db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
                self.db.add_ad_watch(int(user_id), reward)
                
                user = self.db.get_user(int(user_id))
                remaining = DAILY_ADS_LIMIT - (today_ads + 1)
                
                return jsonify({
                    'success': True,
                    'reward': reward,
                    'new_points': user['balance_points'],
                    'remaining': remaining
                })
            except Exception as e:
                logger.error(f"API Error /watch_ad: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.route('/api/wheel_status', methods=['GET'])
        def wheel_status():
            user_id = request.args.get('user_id')
            
            try:
                today_spins = self.db.get_today_wheel_spins(int(user_id))
                user = self.db.get_user(int(user_id))
                
                return jsonify({
                    'success': True,
                    'remaining_spins': max(0, DAILY_WHEEL_SPINS - today_spins),
                    'total_points': user['balance_points'] if user else 0
                })
            except Exception as e:
                logger.error(f"API Error /wheel_status: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.route('/api/spin_wheel', methods=['POST'])
        def spin_wheel():
            data = request.get_json()
            user_id = data.get('user_id')
            
            try:
                today_spins = self.db.get_today_wheel_spins(int(user_id))
                
                if today_spins >= DAILY_WHEEL_SPINS:
                    return jsonify({
                        'success': False,
                        'message': '⚠️ لقد استنفدت جميع محاولاتك اليوم!'
                    })
                
                reward = random.choice(WHEEL_REWARDS)
                self.db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
                self.db.add_wheel_spin(int(user_id), reward)
                
                user = self.db.get_user(int(user_id))
                remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
                
                return jsonify({
                    'success': True,
                    'reward': reward,
                    'new_points': user['balance_points'],
                    'remaining': remaining
                })
            except Exception as e:
                logger.error(f"API Error /spin_wheel: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.route('/api/convert', methods=['POST'])
        def convert_points():
            data = request.get_json()
            user_id = data.get('user_id')
            points = data.get('points', 0)
            
            MIN_CONVERT = 10
            if points < MIN_CONVERT:
                return jsonify({
                    'success': False,
                    'message': f'الحد الأدنى للتحويل هو {MIN_CONVERT} نقاط'
                })
            
            success, msg = self.db.convert_points_to_ton(int(user_id), points)
            
            if success:
                user = self.db.get_user(int(user_id))
                return jsonify({
                    'success': True,
                    'ton': user['balance_ton'],
                    'points': user['balance_points'],
                    'message': msg
                })
            else:
                return jsonify({'success': False, 'message': msg})
        
        @self.flask_app.route('/api/request_withdraw', methods=['POST'])
        def request_withdraw():
            data = request.get_json()
            user_id = data.get('user_id')
            amount = data.get('amount', 0)
            wallet = data.get('wallet', '')
            username = data.get('username', '')
            
            if amount < WITHDRAWAL_MIN:
                return jsonify({
                    'success': False,
                    'message': f'الحد الأدنى للسحب هو {WITHDRAWAL_MIN} تون'
                })
            
            success, result = self.db.create_withdrawal(int(user_id), username, amount, wallet)
            
            return jsonify({
                'success': success,
                'message': 'تم إرسال طلب السحب' if success else result,
                'withdrawal_id': result if success else None
            })
        
        @self.flask_app.route('/api/withdrawals', methods=['GET'])
        def get_withdrawals():
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'user_id مطلوب'})
            
            withdrawals = self.db.get_user_withdrawals(int(user_id))
            return jsonify({'success': True, 'withdrawals': withdrawals})
        
        @self.flask_app.route('/api/redeem_code', methods=['POST'])
        def redeem_code():
            data = request.get_json()
            user_id = data.get('user_id')
            code = data.get('code', '').upper()
            
            success, result = self.db.use_gift_code(int(user_id), code)
            
            if success:
                user = self.db.get_user(int(user_id))
                return jsonify({
                    'success': True,
                    'message': '✅ تم تفعيل الكود',
                    'reward_points': result['reward_points'],
                    'reward_ton': result['reward_ton'],
                    'new_points': user['balance_points'],
                    'new_ton': user['balance_ton']
                })
            else:
                return jsonify({'success': False, 'message': result})
        
        @self.flask_app.route('/api/referral_stats', methods=['GET'])
        def get_referral_stats():
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'user_id مطلوب'})
            
            try:
                stats = self.db.get_user_referrals_stats(int(user_id))
                bot_username = BOT_NAME.lower().replace(' ', '')
                referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
                
                return jsonify({
                    'success': True,
                    'total': stats['total'],
                    'granted': stats['granted'],
                    'pending': stats['pending'],
                    'total_points_earned': stats['total_points_earned'],
                    'total_ton_earned': stats['total_ton_earned'],
                    'referral_link': referral_link,
                    'referrals': stats['referrals']
                })
            except Exception as e:
                logger.error(f"API Error /referral_stats: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.flask_app.errorhandler(404)
        def not_found(e):
            return jsonify({'success': False, 'message': 'Endpoint not found'}), 404
        
        @self.flask_app.errorhandler(500)
        def internal_error(e):
            logger.error(f"Internal server error: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    def setup_static_routes(self):
        """إعداد مسارات الملفات الثابتة"""
        
        @self.flask_app.route('/')
        def serve_index():
            return send_from_directory('public', 'index.html')
        
        @self.flask_app.route('/<path:filename>')
        def serve_static(filename):
            return send_from_directory('public', filename)
    
    # ==================== معالجات تليجرام ====================
    
    def _get_user_id(self, update: Update) -> int:
        """الحصول على معرف المستخدم بشكل آمن"""
        if update.effective_user:
            return update.effective_user.id
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user.id
        if update.message and update.message.from_user:
            return update.message.from_user.id
        return None
    
    async def handle_telegram_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار تليجرام"""
        query = update.callback_query
        
        if not query:
            return
        
        await query.answer()
        data = query.data
        
        # قائمة المهام
        if data == 'tasks_menu':
            await self.tasks_handler.show_tasks_menu(update, context)
        elif data == 'back_to_main':
            await self.start_handler.show_main_menu(update, context)
        elif data == 'balance_menu':
            await self.balance_handler.show_balance(update, context)
        elif data == 'convert_points':
            await self.balance_handler.start_convert(update, context)
        elif data == 'withdraw_menu':
            await self.withdraw_handler.show_withdraw_menu(update, context)
        elif data == 'referral_menu':
            await self.referral_handler.show_referral_menu(update, context)
        elif data == 'giftcode_menu':
            await self.giftcode_handler.show_giftcode_menu(update, context)
        elif data == 'wheel_menu':
            await self.wheel_handler.show_wheel_menu(update, context)
        elif data == 'spin_wheel':
            await self.wheel_handler.spin_wheel(update, context)
        elif data == 'ads_menu':
            await self.ads_handler.show_ads_menu(update, context)
        elif data == 'watch_ad':
            await self.ads_handler.watch_ad(update, context)
        elif data == 'ads_posting_menu':
            await self.ads_posting_handler.show_ads_posting_menu(update, context)
        elif data.startswith('admin_'):
            await self.admin_handler.handle_admin_callback(update, context)
    
    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة البيانات من WebApp"""
        try:
            if not update.effective_message or not update.effective_message.web_app_data:
                return
            
            data = json.loads(update.effective_message.web_app_data.data)
            action = data.get('action')
            user_id = self._get_user_id(update)
            
            if not user_id:
                logger.warning("No user_id found in webapp data")
                return
            
            logger.info(f"📱 WebApp data: {action} from user {user_id}")
            
            # معالجة إجراءات الأدمن
            if action.startswith('admin_'):
                await self.admin_handler.handle_webapp_action(update, context, action, data)
                return
            
            # معالجة الإجراءات العادية
            response = await self.process_api_action(action, data, user_id)
            
            if response and update.message:
                await update.message.reply_text(json.dumps(response))
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON Error: {e}")
        except Exception as e:
            logger.error(f"Error in handle_webapp_data: {e}")
    
    async def process_api_action(self, action: str, data: dict, user_id: int) -> dict:
        """معالجة إجراءات API من WebApp"""
        
        if action == 'get_user_data':
            user = self.db.get_user(user_id)
            today_ads = self.db.get_today_ads_count(user_id)
            return {
                'action': 'user_data',
                'ton': user['balance_ton'] if user else 0,
                'points': user['balance_points'] if user else 0,
                'total_referrals': user['total_referrals'] if user else 0,
                'ads_watched': today_ads
            }
        
        elif action == 'convert_points':
            points = data.get('points', 0)
            success, msg = self.db.convert_points_to_ton(user_id, points)
            if success:
                user = self.db.get_user(user_id)
                return {
                    'action': 'convert_result',
                    'success': True,
                    'ton': user['balance_ton'],
                    'points': user['balance_points']
                }
            else:
                return {'action': 'convert_result', 'success': False, 'message': msg}
        
        elif action == 'watch_ad':
            reward = data.get('reward', AD_REWARD_POINTS)
            today_ads = self.db.get_today_ads_count(user_id)
            
            if today_ads >= DAILY_ADS_LIMIT:
                return {
                    'action': 'ad_result',
                    'success': False,
                    'message': f'⚠️ لقد وصلت للحد اليومي للإعلانات ({DAILY_ADS_LIMIT})!'
                }
            
            self.db.update_user_balance(user_id, points_amount=reward, update_earned=True)
            self.db.add_ad_watch(user_id, reward)
            user = self.db.get_user(user_id)
            remaining = DAILY_ADS_LIMIT - (today_ads + 1)
            
            return {
                'action': 'ad_result',
                'success': True,
                'reward': reward,
                'new_points': user['balance_points'],
                'remaining': remaining
            }
        
        elif action == 'spin_wheel':
            today_spins = self.db.get_today_wheel_spins(user_id)
            
            if today_spins >= DAILY_WHEEL_SPINS:
                return {
                    'action': 'wheel_result',
                    'success': False,
                    'message': '⚠️ لقد استنفدت جميع محاولاتك اليوم!'
                }
            
            reward = random.choice(WHEEL_REWARDS)
            self.db.update_user_balance(user_id, points_amount=reward, update_earned=True)
            self.db.add_wheel_spin(user_id, reward)
            user = self.db.get_user(user_id)
            remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
            
            return {
                'action': 'wheel_result',
                'success': True,
                'reward': reward,
                'new_points': user['balance_points'],
                'remaining': remaining
            }
        
        elif action == 'redeem_code':
            code = data.get('code', '').upper()
            success, result = self.db.use_gift_code(user_id, code)
            
            if success:
                user = self.db.get_user(user_id)
                return {
                    'action': 'code_result',
                    'success': True,
                    'reward_points': result['reward_points'],
                    'reward_ton': result['reward_ton'],
                    'new_points': user['balance_points'],
                    'new_ton': user['balance_ton']
                }
            else:
                return {'action': 'code_result', 'success': False, 'message': result}
        
        elif action == 'request_withdraw':
            amount = data.get('amount', 0)
            wallet = data.get('wallet', '')
            username = data.get('username', '')
            
            success, withdrawal_id = self.db.create_withdrawal(user_id, username, amount, wallet)
            
            if success:
                return {
                    'action': 'withdraw_result',
                    'success': True,
                    'withdrawal_id': withdrawal_id,
                    'amount': amount
                }
            else:
                return {
                    'action': 'withdraw_result',
                    'success': False,
                    'message': withdrawal_id
                }
        
        return None
    
    async def handle_text_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = self._get_user_id(update)
        
        # إذا لم نتمكن من الحصول على معرف المستخدم، تجاهل الرسالة
        if not user_id:
            logger.warning("Cannot get user_id from update, ignoring message")
            return
        
        # معالجة إدخال الكود
        if context.user_data.get('awaiting_giftcode'):
            text = update.message.text.strip() if update.message else ""
            if text:
                success, result = self.db.use_gift_code(user_id, text.upper())
                
                if success:
                    user = self.db.get_user(user_id)
                    await update.message.reply_text(
                        f"✅ تم تفعيل الكود بنجاح!\n"
                        f"🎁 حصلت على: {result['reward_points']} نقطة + {result['reward_ton']:.4f} تون\n"
                        f"💰 رصيدك الحالي: {user['balance_ton']:.4f} تون\n"
                        f"⭐ نقاطك: {user['balance_points']:.0f} نقطة"
                    )
                else:
                    await update.message.reply_text(f"❌ {result}")
                
                context.user_data['awaiting_giftcode'] = False
            return
        
        # معالجة تحويل النقاط
        if context.user_data.get('awaiting_convert'):
            try:
                points = float(update.message.text.strip())
                MIN_CONVERT = 10
                if points < MIN_CONVERT:
                    await update.message.reply_text(f"❌ الحد الأدنى للتحويل هو {MIN_CONVERT} نقاط")
                    context.user_data['awaiting_convert'] = False
                    return
                    
                success, msg = self.db.convert_points_to_ton(user_id, points)
                
                if success:
                    user = self.db.get_user(user_id)
                    await update.message.reply_text(
                        f"✅ {msg}\n"
                        f"💰 رصيد التون: {user['balance_ton']:.4f}\n"
                        f"⭐ رصيد النقاط: {user['balance_points']:.0f}"
                    )
                else:
                    await update.message.reply_text(f"❌ {msg}")
            except ValueError:
                await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
            
            context.user_data['awaiting_convert'] = False
            return
        
        # معالجة تفاصيل الإعلان
        if context.user_data.get('awaiting_ad_details'):
            await self.ads_posting_handler.handle_ad_details(update, context)
            return
        
        # معالجة إنشاء مهمة
        if context.user_data.get('awaiting_task_creation'):
            await self.admin_handler.handle_task_creation(update, context)
            return
        
        # رسالة افتراضية
        if update.message:
            await update.message.reply_text(
                "❓ أمر غير معروف. استخدم /start للبدء",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data='back_to_main')
                ]])
            )
    
    # ==================== التشغيل ====================
    
    def run_flask(self):
        """تشغيل خادم Flask"""
        logger.info("🌐 Starting Flask API server on port 5000...")
        self.flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    
    def run_telegram(self):
        """تشغيل بوت تليجرام"""
        logger.info("🤖 Starting Telegram bot...")
        self.telegram_app.run_polling(allowed_updates=['message', 'callback_query'])
    
    def run(self):
        """تشغيل البوت و API معاً"""
        logger.info("=" * 60)
        logger.info(f"🚀 {self.bot_name} - Unified Bot Starting")
        logger.info(f"📱 WebApp URL: {self.webapp_url}")
        logger.info(f"👑 Admins: {self.admin_ids}")
        logger.info(f"🌐 API: http://localhost:5000/api")
        logger.info("=" * 60)
        
        # تشغيل Flask في thread منفصل
        flask_thread = threading.Thread(target=self.run_flask, daemon=True)
        flask_thread.start()
        
        # تشغيل Telegram في thread الرئيسي
        self.run_telegram()


if __name__ == "__main__":
    bot = RockyTapBot()
    bot.run()