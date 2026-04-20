# backend/bot/handlers/start.py
"""
معالج أمر /start - مع WebApp
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from backend.config import BOT_NAME, WEBAPP_URL
from backend.db import Session
from backend.services.user_service import UserService


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /start"""
    user = update.effective_user
    user_id = user.id
    
    # تسجيل المستخدم
    db = Session()
    try:
        db_user = UserService.get_or_create_user(
            db, 
            user_id, 
            user.username, 
            user.first_name
        )
    finally:
        db.close()
    
    # التعامل مع رابط الإحالة
    if context.args and context.args[0].startswith('ref_'):
        try:
            referrer_id = int(context.args[0].replace('ref_', ''))
            if referrer_id != user_id:
                context.user_data['referrer_id'] = referrer_id
        except ValueError:
            pass
    
    # عرض القائمة الرئيسية
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة الرئيسية مع WebApp"""
    user = update.effective_user
    user_id = user.id
    
    db = Session()
    try:
        user_data = UserService.get_user(db, user_id)
        if not user_data:
            user_data = UserService.get_or_create_user(db, user_id, user.username, user.first_name)
    finally:
        db.close()
    
    text = f"""
🎉 <b>مرحباً بك في {BOT_NAME}!</b> 🎉
━━━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> {user.first_name}
💰 <b>الرصيد (تون):</b> <code>{user_data.balance_ton:.4f}</code>
⭐ <b>الرصيد (نقاط):</b> <code>{user_data.balance_points:.0f}</code>
👥 <b>الإحالات:</b> <code>{user_data.total_referrals}</code>
━━━━━━━━━━━━━━━━━━
📌 اختر ما تريد:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html")),
            InlineKeyboardButton("👥 الإحالات", callback_data='referral_menu')
        ],
        [
            InlineKeyboardButton("🎁 أكواد", callback_data='giftcode_menu'),
            InlineKeyboardButton("💸 سحب", callback_data='withdraw_menu')
        ],
        [
            InlineKeyboardButton("📋 المهام", callback_data='tasks_menu'),
            InlineKeyboardButton("🎡 عجلة الحظ", callback_data='wheel_menu')
        ],
        [
            InlineKeyboardButton("📺 إعلانات", callback_data='ads_menu'),
            InlineKeyboardButton("📢 إعلاناتي", callback_data='ads_posting_menu')
        ]
    ]
    
    # إضافة زر الأدمن
    admin_ids = context.bot_data.get('admin_ids', [])
    if user_id in admin_ids:
        keyboard.append([InlineKeyboardButton("👑 لوحة الأدمن", callback_data='admin_panel')])
    
    keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data='back_to_main')])
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )