# handlers/start.py
"""
معالج الأوامر الرئيسية والقائمة الرئيسية
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_NAME, WELCOME_MESSAGE, WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class StartHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /start"""
        user = update.effective_user
        user_id = user.id
        
        # تسجيل المستخدم في قاعدة البيانات
        self.db.get_or_create_user(user_id, user.username, user.first_name)
        
        # التحقق من وجود إحالة في الرابط
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
        
        # عرض القائمة الرئيسية
        await self.show_main_menu(update, context)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض القائمة الرئيسية"""
        user = update.effective_user
        user_id = user.id
        
        user_data = self.db.get_user(user_id)
        if not user_data:
            user_data = self.db.get_or_create_user(user_id, user.username, user.first_name)
        
        # تحديث حالة المهام المجانية (لشروط السحب)
        free_tasks_status = self.db.get_user_free_tasks_status(user_id)
        free_completed = sum(1 for t in free_tasks_status if t['status'] == 'completed')
        free_total = len(free_tasks_status)
        
        text = f"""
🎉 <b>{WELCOME_MESSAGE}</b> 🎉
━━━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> {user.first_name}
💰 <b>الرصيد (تون):</b> <code>{user_data['balance_ton']:.4f}</code> TON
⭐ <b>الرصيد (نقاط):</b> <code>{user_data['balance_points']:.0f}</code> نقطة
✅ <b>المهام المنجزة:</b> <code>{user_data.get('completed_tasks', 0)}</code>
🎁 <b>المهام المجانية:</b> <code>{free_completed}/{free_total}</code>
👥 <b>الإحالات:</b> <code>{user_data['total_referrals']}</code>
━━━━━━━━━━━━━━━━━━
📌 اختر ما تريد:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💰 رصيدي", callback_data='balance_menu'),
                InlineKeyboardButton("📋 المهام", callback_data='tasks_menu')
            ],
            [
                InlineKeyboardButton("🎡 عجلة الحظ", callback_data='wheel_menu'),
                InlineKeyboardButton("📺 إعلانات", callback_data='ads_menu')
            ],
            [
                InlineKeyboardButton("👥 الإحالات", callback_data='referral_menu'),
                InlineKeyboardButton("🎁 أكواد", callback_data='giftcode_menu')
            ],
            [
                InlineKeyboardButton("💸 سحب", callback_data='withdraw_menu'),
                InlineKeyboardButton("💳 محفظتي", callback_data='wallet_menu')
            ]
        ]
        
        # إضافة زر الأدمن للمشرفين
        if user_id in self.bot.admin_ids:
            keyboard.append([InlineKeyboardButton("👑 لوحة الأدمن", callback_data='admin_panel')])
        
        keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data='back_to_main')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text, reply_markup=reply_markup, parse_mode='HTML'
            )