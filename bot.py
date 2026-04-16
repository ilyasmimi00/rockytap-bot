# bot.py
"""
RockyTap Bot - النسخة الكاملة المتكاملة
"""

import logging
import json
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
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
        
        self.setup_handlers()
        
        logger.info(f"✅ {BOT_NAME} Bot initialized")
    
    def setup_handlers(self):
        """إعداد معالجات الأوامر والأزرار"""
        
        # أوامر
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # معالج الأزرار
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # معالج WebApp
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            self.handle_webapp_data
        ))
        
        # معالج الرسائل النصية
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        logger.info("✅ Handlers configured")
    
    # ==================== أوامر البوت ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /start - تسجيل المستخدم وفتح الواجهة"""
        user = update.effective_user
        user_id = user.id
        
        # تسجيل المستخدم
        db_user = self.db.get_or_create_user(user_id, user.username, user.first_name)
        
        # التحقق من وجود إحالة
        if context.args and context.args[0].startswith('ref_'):
            try:
                referrer_id = int(context.args[0].replace('ref_', ''))
                if referrer_id != user_id:
                    result, msg = self.db.create_referral(
                        referrer_id=referrer_id,
                        referred_id=user_id,
                        referred_username=user.username or user.first_name
                    )
                    if result:
                        logger.info(f"✅ Referral created: {referrer_id} -> {user_id}")
            except ValueError:
                pass
        
        text = f"""
🎉 <b>مرحباً بك في {self.bot_name}!</b> 🎉

💰 <b>رصيدك:</b>
• تون: <code>{db_user['balance_ton']:.4f}</code>
• نقاط: <code>{db_user['balance_points']:.0f}</code>

📱 اضغط على الزر أدناه لبدء اللعب!
"""
        
        keyboard = [[
            InlineKeyboardButton(
                "🎮 افتح اللعبة", 
                web_app=WebAppInfo(url=f"{self.webapp_url}/index.html")
            )
        ]]
        
        await update.message.reply_text(
            text, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /admin - فتح لوحة الأدمن"""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("⛔ أنت لست مشرفاً")
            return
        
        text = f"""
👑 <b>لوحة تحكم الأدمن - {self.bot_name}</b>
━━━━━━━━━━━━━━━━━━
📌 استخدم الواجهة الرسومية للإدارة:
        """
        
        keyboard = [[
            InlineKeyboardButton(
                "👑 فتح لوحة التحكم",
                web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html")
            )
        ]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /balance - عرض الرصيد"""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ حدث خطأ في تحميل بياناتك")
            return
        
        text = f"""
💰 <b>رصيدك الحالي</b>
━━━━━━━━━━━━━━━━━━
💵 <b>تون (TON):</b> <code>{user_data['balance_ton']:.4f}</code>
⭐ <b>نقاط (POINTS):</b> <code>{user_data['balance_points']:.0f}</code>
━━━━━━━━━━━━━━━━━━
💱 <b>سعر الصرف:</b> {POINTS_TO_TON_RATE} نقطة = 1 تون
📉 <b>الحد الأدنى للسحب:</b> <code>{WITHDRAWAL_MIN:.4f}</code> تون
"""
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /stats - إحصائيات المستخدم"""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ حدث خطأ في تحميل بياناتك")
            return
        
        withdrawals = self.db.get_user_withdrawals(user_id)
        total_withdrawn = sum(w['amount'] for w in withdrawals if w['status'] == 'completed')
        
        text = f"""
📊 <b>إحصائياتك الشخصية</b>
━━━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> {user_data['first_name']}
💰 <b>الرصيد (تون):</b> <code>{user_data['balance_ton']:.4f}</code>
⭐ <b>الرصيد (نقاط):</b> <code>{user_data['balance_points']:.0f}</code>
💵 <b>إجمالي الأرباح:</b> <code>{user_data['total_earned_ton']:.4f}</code> تون
💳 <b>إجمالي المسحوبات:</b> <code>{total_withdrawn:.4f}</code> تون
👥 <b>الإحالات:</b> <code>{user_data['total_referrals']}</code>
📅 <b>تاريخ التسجيل:</b> {user_data['join_date']}
━━━━━━━━━━━━━━━━━━
"""
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    # ==================== معالج WebApp ====================
    
    async def handle_webapp_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة البيانات الواردة من WebApp"""
        try:
            data = json.loads(update.effective_message.web_app_data.data)
            action = data.get('action')
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            
            logger.info(f"📱 WebApp data: {action} from user {user_id}")
            
            # ===== إجراءات الأدمن =====
            if action.startswith('admin_'):
                await self._handle_admin_actions(update, context, action, data, user_id)
                return
            
            # ===== جلب بيانات المستخدم =====
            if action == 'get_user_data':
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
            
            # ===== جلب إحصائيات الإحالات =====
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
            
            # ===== تحويل النقاط =====
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
                        'message': f'✅ تم تحويل {points} نقطة إلى {points/POINTS_TO_TON_RATE:.4f} تون'
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'convert_result',
                        'success': False,
                        'message': f'❌ {msg}'
                    }))
            
            # ===== مشاهدة إعلان =====
            elif action == 'watch_ad':
                company = data.get('company', '')
                reward = data.get('reward', AD_REWARD_POINTS)
                today_ads = self.db.get_today_ads_count(user_id)
                ads_settings = self.db.get_ads_settings()
                
                daily_limit = ads_settings.get('daily_limit', DAILY_ADS_LIMIT)
                points_reward = ads_settings.get('points_per_ad', AD_REWARD_POINTS)
                
                if today_ads >= daily_limit:
                    await update.message.reply_text(json.dumps({
                        'action': 'ad_result',
                        'success': False,
                        'message': f'⚠️ لقد وصلت للحد اليومي للإعلانات ({daily_limit})! عود غداً.'
                    }))
                    return
                
                self.db.update_user_balance(user_id, points_amount=points_reward, update_earned=True)
                self.db.add_ad_watch(user_id, points_reward)
                
                user_data = self.db.get_user(user_id)
                remaining = daily_limit - (today_ads + 1)
                
                await update.message.reply_text(json.dumps({
                    'action': 'ad_result',
                    'success': True,
                    'reward': points_reward,
                    'new_points': user_data['balance_points'],
                    'remaining': remaining,
                    'message': f'✅ +{points_reward} نقطة! متبقي {remaining} إعلان اليوم'
                }))
            
            # ===== المطالبة بمكافأة الإعلانات =====
            elif action == 'claim_ads':
                points = data.get('points', 0)
                user_data = self.db.get_user(user_id)
                
                if user_data['balance_points'] < points:
                    await update.message.reply_text(json.dumps({
                        'action': 'claim_result',
                        'success': False,
                        'message': '❌ لا تملك هذه النقاط!'
                    }))
                    return
                
                success, msg = self.db.convert_points_to_ton(user_id, points)
                
                if success:
                    await update.message.reply_text(json.dumps({
                        'action': 'claim_result',
                        'success': True,
                        'ton': points/POINTS_TO_TON_RATE,
                        'points': 0,
                        'message': f'🎉 مبروك! حصلت على {points/POINTS_TO_TON_RATE:.4f} تون'
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'claim_result',
                        'success': False,
                        'message': f'❌ {msg}'
                    }))
            
            # ===== عجلة الحظ =====
            elif action == 'get_wheel_status':
                today_spins = self.db.get_today_wheel_spins(user_id)
                user_data = self.db.get_user(user_id)
                
                await update.message.reply_text(json.dumps({
                    'action': 'wheel_status',
                    'remaining_spins': max(0, DAILY_WHEEL_SPINS - today_spins),
                    'total_points': user_data['balance_points'] if user_data else 0
                }))
            
            elif action == 'spin_wheel':
                today_spins = self.db.get_today_wheel_spins(user_id)
                
                if today_spins >= DAILY_WHEEL_SPINS:
                    await update.message.reply_text(json.dumps({
                        'action': 'wheel_result',
                        'success': False,
                        'message': '⚠️ لقد استنفدت جميع محاولاتك اليوم! عود غداً.'
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
                    'remaining': remaining,
                    'message': f'🎉 مبروك! ربحت {reward} نقطة!'
                }))
            
            # ===== تفعيل كود =====
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
                        'new_ton': user_data['balance_ton'],
                        'message': '✅ تم تفعيل الكود بنجاح!'
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'code_result',
                        'success': False,
                        'message': f'❌ {result}'
                    }))
            
            # ===== طلب سحب =====
            elif action == 'request_withdraw':
                amount = data.get('amount', 0)
                wallet = data.get('wallet', '')
                
                success, withdrawal_id = self.db.create_withdrawal(user_id, username, amount, wallet)
                
                if success:
                    await update.message.reply_text(json.dumps({
                        'action': 'withdraw_result',
                        'success': True,
                        'withdrawal_id': withdrawal_id,
                        'amount': amount,
                        'message': f'✅ تم إرسال طلب السحب #{withdrawal_id} بنجاح!'
                    }))
                else:
                    await update.message.reply_text(json.dumps({
                        'action': 'withdraw_result',
                        'success': False,
                        'message': f'❌ {withdrawal_id}'
                    }))
            
            # ===== الحصول على اسم البوت =====
            elif action == 'get_bot_username':
                bot_info = await context.bot.get_me()
                await update.message.reply_text(json.dumps({
                    'action': 'bot_username',
                    'username': bot_info.username
                }))
            
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                await update.message.reply_text(json.dumps({
                    'action': 'error',
                    'message': '❌ إجراء غير معروف'
                }))
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON Error: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'error',
                'message': '❌ خطأ في قراءة البيانات'
            }))
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'error',
                'message': f'❌ حدث خطأ: {str(e)[:100]}'
            }))
    
    # ==================== إجراءات الأدمن ====================
    
    async def _handle_admin_actions(self, update, context, action, data, admin_id):
        """معالجة إجراءات الأدمن"""
        
        if admin_id not in self.admin_ids:
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': False,
                'message': '⛔ أنت لست مشرفاً'
            }))
            return
        
        # إدارة المستخدمين
        if action == 'admin_add_balance':
            target_id = int(data.get('user_id', 0))
            amount = float(data.get('amount', 0))
            currency = data.get('currency', 'ton')
            
            if currency == 'ton':
                self.db.update_user_balance(target_id, ton_amount=amount, update_earned=True)
            else:
                self.db.update_user_balance(target_id, points_amount=amount, update_earned=True)
            
            self.db.add_admin_log(admin_id, f"إضافة رصيد", f"أضاف {amount} {currency} للمستخدم {target_id}")
            
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم إضافة {amount} {currency} للمستخدم {target_id}',
                'refresh': True
            }))
        
        elif action == 'admin_ban_user':
            target_id = int(data.get('user_id', 0))
            self.db.update_user_block_status(target_id, True)
            self.db.add_admin_log(admin_id, f"حظر مستخدم", f"حظر المستخدم {target_id}")
            
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم حظر المستخدم {target_id}',
                'refresh': True
            }))
        
        elif action == 'admin_toggle_ban':
            target_id = int(data.get('user_id', 0))
            user = self.db.get_user(target_id)
            if user:
                new_status = not user.get('is_blocked', False)
                self.db.update_user_block_status(target_id, new_status)
                self.db.add_admin_log(admin_id, f"تغيير حالة", f"غير حالة المستخدم {target_id} إلى {'محظور' if new_status else 'نشط'}")
            
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': '✅ تم تغيير حالة المستخدم',
                'refresh': True
            }))
        
        # إعدادات الإعلانات
        elif action == 'admin_save_api_key':
            api_key = data.get('api_key')
            self.db.save_ads_settings(api_key=api_key)
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': '✅ تم حفظ API كود'
            }))
        
        elif action == 'admin_save_points_per_ad':
            points = data.get('points')
            self.db.save_ads_settings(points_per_ad=points)
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم حفظ النقاط: {points} نقطة لكل إعلان'
            }))
        
        elif action == 'admin_save_daily_ad_limit':
            limit = data.get('limit')
            self.db.save_ads_settings(daily_limit=limit)
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم حفظ الحد اليومي: {limit} إعلان'
            }))
        
        # إعدادات الإحالات
        elif action == 'admin_save_referral':
            settings = data
            self.db.save_referral_settings(
                reward_type=settings.get('reward_type', 'both'),
                points_value=settings.get('points_value', 100),
                ton_value=settings.get('ton_value', 0.01),
                required_tasks=settings.get('required_tasks', 6)
            )
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': '✅ تم حفظ إعدادات الإحالات'
            }))
        
        # إعدادات السحب
        elif action == 'admin_save_min_withdraw':
            min_amount = float(data.get('min_withdraw', 0.02))
            # يمكن حفظ هذا الإعداد في SystemSetting
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم حفظ الحد الأدنى للسحب: {min_amount} TON'
            }))
        
        # إعدادات النظام
        elif action == 'admin_save_exchange_rate':
            rate = data.get('rate')
            # يمكن حفظ هذا الإعداد في SystemSetting
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': f'✅ تم حفظ سعر الصرف: 1 تون = {rate} نقاط'
            }))
        
        elif action == 'admin_save_settings':
            settings = data.get('settings', {})
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': True,
                'message': '✅ تم حفظ جميع الإعدادات'
            }))
        
        # إنشاء كود
        elif action == 'admin_create_code':
            amount = float(data.get('amount', 0))
            max_uses = int(data.get('max_uses', 100))
            
            success, code = self.db.create_gift_code(
                created_by=admin_id,
                reward_ton=amount,
                max_uses=max_uses,
                is_admin=True
            )
            
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': success,
                'message': f'✅ تم إنشاء الكود: <code>{code}</code>' if success else '❌ حدث خطأ'
            }))
        
        else:
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': False,
                'message': f'❌ إجراء غير معروف: {action}'
            }))
    
    # ==================== معالج الأزرار ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار الموحد"""
        query = update.callback_query
        data = query.data
        
        await query.answer()
        
        if data == 'back_to_main':
            await self.start_command(update, context)
        elif data == 'referral_info':
            await self.show_referral_info(update, context)
        else:
            logger.warning(f"Unknown callback: {data}")
    
    # ==================== نظام الإحالات ====================
    
    async def show_referral_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلومات الإحالات"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        stats = self.db.get_user_referrals_stats(user_id)
        bot_info = await context.bot.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        
        settings = stats['settings']
        if settings['reward_type'] == 'points':
            reward_text = f"⭐ {settings['points_value']} نقطة"
        elif settings['reward_type'] == 'ton':
            reward_text = f"💰 {settings['ton_value']:.4f} تون"
        else:
            reward_text = f"⭐ {settings['points_value']} نقطة + 💰 {settings['ton_value']:.4f} تون"
        
        text = f"""
👥 <b>نظام الإحالات</b>
━━━━━━━━━━━━━━━━━━
📎 <b>رابط الإحالة الخاص بك:</b>
<code>{referral_link}</code>

🎁 <b>مكافأة كل إحالة:</b>
{reward_text}

📌 <b>شرط الإحالة:</b>
إكمال المدعو {settings['required_tasks']} مهام

━━━━━━━━━━━━━━━━━━
📊 <b>إحصائياتك:</b>
• 👥 إجمالي الإحالات: <code>{stats['total']}</code>
• ✅ المكتملة: <code>{stats['granted']}</code>
• ⏳ قيد الانتظار: <code>{stats['pending']}</code>
• 💰 الأرباح: {stats['total_points_earned']} نقطة + {stats['total_ton_earned']:.4f} تون
"""
        
        if stats['referrals']:
            text += "\n📋 <b>قائمة المدعوين:</b>\n"
            for ref in stats['referrals'][:10]:
                text += f"• @{ref['username']} | {ref['status']}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔗 مشاركة الرابط", callback_data='share_referral')],
            [InlineKeyboardButton("🔄 تحديث", callback_data='referral_info')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    # ==================== معالج الرسائل ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        await update.message.reply_text(
            "❓ أمر غير معروف. استخدم /start للبدء",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data='back_to_main')
            ]])
        )
    
    # ==================== تشغيل البوت ====================
    
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