# handlers/wheel.py
"""
معالج عجلة الحظ
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import DAILY_WHEEL_SPINS, WHEEL_REWARDS, WEBAPP_URL
import random
import logging

logger = logging.getLogger(__name__)


class WheelHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_wheel_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة عجلة الحظ"""
        user = update.effective_user
        user_id = user.id
        
        today_spins = self.db.get_today_wheel_spins(user_id)
        remaining = DAILY_WHEEL_SPINS - today_spins
        
        text = f"""
🎡 <b>عجلة الحظ</b>
━━━━━━━━━━━━━━━━━━
🎁 <b>الجوائز المتاحة:</b>
"""
        
        for reward in WHEEL_REWARDS[:5]:
            text += f"• 🎁 {reward} نقطة\n"
        
        text += f"""
━━━━━━━━━━━━━━━━━━
📊 <b>محاولاتك اليوم:</b> {today_spins}/{DAILY_WHEEL_SPINS}
🎯 <b>المتبقي:</b> {remaining} محاولة
━━━━━━━━━━━━━━━━━━
⚠️ يتم إعادة تعيين المحاولات يومياً
        """
        
        keyboard = []
        
        if remaining > 0:
            keyboard.append([InlineKeyboardButton("🎡 ابدأ اللعب", callback_data='spin_wheel')])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')])
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def spin_wheel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اللعب في عجلة الحظ"""
        user = update.effective_user
        user_id = user.id
        
        today_spins = self.db.get_today_wheel_spins(user_id)
        
        if today_spins >= DAILY_WHEEL_SPINS:
            await update.callback_query.answer(
                "⚠️ لقد استنفدت جميع محاولاتك اليوم! عود غداً.", 
                show_alert=True
            )
            return
        
        # اختيار جائزة عشوائية
        reward = random.choice(WHEEL_REWARDS)
        
        # إضافة المكافأة
        self.db.update_user_balance(
            user_id, 
            points_amount=reward,
            update_earned=True
        )
        
        # تسجيل اللعبة
        self.db.add_wheel_spin(user_id, reward)
        
        user_data = self.db.get_user(user_id)
        remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
        
        await update.callback_query.answer(
            f"🎉 مبروك! ربحت {reward} نقطة!\n"
            f"⭐ رصيدك: {user_data['balance_points']:.0f} نقطة\n"
            f"🎡 متبقي {remaining} محاولة اليوم",
            show_alert=True
        )
        
        # تحديث القائمة
        await self.show_wheel_menu(update, context)