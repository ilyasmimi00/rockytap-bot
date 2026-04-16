# handlers/balance.py
"""
معالج الرصيد وتحويل النقاط إلى تون
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import POINTS_TO_TON_RATE, WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class BalanceHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الرصيد"""
        user = update.effective_user
        user_id = user.id
        
        user_data = self.db.get_user(user_id)
        
        text = f"""
💰 <b>رصيدك الحالي</b>
━━━━━━━━━━━━━━━━━━
💵 <b>تون (TON):</b> <code>{user_data['balance_ton']:.4f}</code>
⭐ <b>نقاط (POINTS):</b> <code>{user_data['balance_points']:.0f}</code>
━━━━━━━━━━━━━━━━━━
💱 <b>سعر الصرف:</b> {POINTS_TO_TON_RATE} نقطة = 1 تون
📉 <b>الحد الأدنى للسحب:</b> <code>0.02</code> تون
━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحويل النقاط → تون", callback_data='convert_points')],
            [InlineKeyboardButton("💸 سحب الأرباح", callback_data='withdraw_menu')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def start_convert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء عملية تحويل النقاط إلى تون"""
        user = update.effective_user
        user_id = user.id
        
        user_data = self.db.get_user(user_id)
        
        context.user_data['awaiting_convert'] = True
        
        text = f"""
🔄 <b>تحويل النقاط إلى تون</b>
━━━━━━━━━━━━━━━━━━
⭐ <b>نقاطك الحالية:</b> <code>{user_data['balance_points']:.0f}</code>
💱 <b>سعر الصرف:</b> {POINTS_TO_TON_RATE} نقطة = 1 تون
━━━━━━━━━━━━━━━━━━
📝 <b>أدخل عدد النقاط التي تريد تحويلها:</b>

مثال: <code>100</code>
(ستحصل على {100/POINTS_TO_TON_RATE:.4f} تون)

⚠️ <b>ملاحظة:</b> لا يمكن استرداد النقاط بعد التحويل
        """
        
        keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data='balance_menu')]]
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def handle_convert_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال عدد النقاط للتحويل"""
        if not context.user_data.get('awaiting_convert'):
            return False
        
        message = update.message
        user_id = update.effective_user.id
        text = message.text.strip()
        
        try:
            points = float(text)
            
            if points <= 0:
                await message.reply_text("❌ يجب إدخال عدد أكبر من صفر")
                return True
            
            success, msg = self.db.convert_points_to_ton(user_id, points)
            
            if success:
                user_data = self.db.get_user(user_id)
                await message.reply_text(
                    f"✅ {msg}\n"
                    f"💰 رصيد التون الجديد: <code>{user_data['balance_ton']:.4f}</code> TON\n"
                    f"⭐ رصيد النقاط الجديد: <code>{user_data['balance_points']:.0f}</code> نقطة",
                    parse_mode='HTML'
                )
            else:
                await message.reply_text(f"❌ {msg}")
            
        except ValueError:
            await message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        context.user_data['awaiting_convert'] = False
        return True