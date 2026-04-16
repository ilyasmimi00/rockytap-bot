# handlers/giftcode.py
"""
معالج الأكواد الترويجية
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class GiftCodeHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_giftcode_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الأكواد الترويجية"""
        user = update.effective_user
        user_id = user.id
        is_admin = user_id in self.bot.admin_ids
        
        used_codes = self.db.get_user_gift_codes_used(user_id)
        
        text = f"""
🎁 <b>الأكواد الترويجية</b>
━━━━━━━━━━━━━━━━━━
📝 <b>كيف يعمل النظام:</b>

✨ <b>أدخل كود</b>
• أدخل كوداً تحصل عليه من الأصدقاء
• تحصل على المكافأة فوراً

✨ <b>إنشاء كود (للمشرفين)</b>
• أنشئ كوداً ترويجياً لأصدقائك
• حدد قيمة الكود وعدد الاستخدامات
━━━━━━━━━━━━━━━━━━
📊 <b>الأكواد المستخدمة:</b>
"""
        
        if used_codes:
            for code in used_codes[:5]:
                text += f"• 🎫 <code>{code['code']}</code> | +{code['reward_points']:.0f} نقطة | 📅 {code['used_at']}\n"
        else:
            text += "• لا توجد أكواد مستخدمة بعد\n"
        
        keyboard = [
            [InlineKeyboardButton("🎫 إدخال كود", callback_data='enter_giftcode')],
            [InlineKeyboardButton("🌐 صفحة الأكواد", web_app=WebAppInfo(url=f"{WEBAPP_URL}/giftcode.html"))],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        if is_admin:
            keyboard.insert(1, [InlineKeyboardButton("✨ إنشاء كود (مشرف)", callback_data='admin_create_code')])
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def show_giftcode_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض سجل الأكواد المستخدمة"""
        user = update.effective_user
        user_id = user.id
        
        used_codes = self.db.get_user_gift_codes_used(user_id)
        
        if not used_codes:
            text = "📋 <b>لا توجد أكواد مستخدمة بعد</b>"
        else:
            text = "📋 <b>الأكواد التي استخدمتها</b>\n━━━━━━━━━━━━━━━━━━\n"
            for code in used_codes:
                text += f"🎫 <code>{code['code']}</code>\n"
                text += f"   💰 +{code['reward_points']:.0f} نقطة + {code['reward_ton']:.4f} تون\n"
                text += f"   📅 {code['used_at']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='giftcode_menu')]]
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح صفحة الأكواد في WebApp"""
        user = update.effective_user
        user_id = user.id
        
        keyboard = [[InlineKeyboardButton(
            "🎫 فتح صفحة الأكواد",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/giftcode.html?user_id={user_id}")
        )]]
        
        await update.callback_query.edit_message_text(
            "🔗 اضغط على الزر أدناه لفتح صفحة الأكواد:\n\n"
            "📝 أدخل الكود الترويجي للحصول على المكافأة",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )