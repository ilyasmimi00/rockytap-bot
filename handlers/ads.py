# handlers/ads.py
"""
معالج الإعلانات
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import DAILY_ADS_LIMIT, AD_REWARD_POINTS, WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class AdsHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_ads_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإعلانات"""
        user = update.effective_user
        user_id = user.id
        
        today_ads = self.db.get_today_ads_count(user_id)
        remaining = DAILY_ADS_LIMIT - today_ads
        
        text = f"""
📺 <b>مشاهدة الإعلانات</b>
━━━━━━━━━━━━━━━━━━
💰 <b>المكافأة:</b> +{AD_REWARD_POINTS} نقطة لكل إعلان
📊 <b>تقدمك اليوم:</b> {today_ads}/{DAILY_ADS_LIMIT}
🎯 <b>المتبقي:</b> {remaining} إعلان
━━━━━━━━━━━━━━━━━━
⚠️ يتم إعادة تعيين العدد يومياً في منتصف الليل
        """
        
        keyboard = []
        
        if remaining > 0:
            keyboard.append([InlineKeyboardButton("📺 مشاهدة إعلان", callback_data='watch_ad')])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')])
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def watch_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مشاهدة إعلان (محاكاة)"""
        user = update.effective_user
        user_id = user.id
        
        today_ads = self.db.get_today_ads_count(user_id)
        
        if today_ads >= DAILY_ADS_LIMIT:
            await update.callback_query.answer(
                "⚠️ لقد وصلت للحد اليومي للإعلانات! عود غداً.", 
                show_alert=True
            )
            return
        
        # إضافة المكافأة
        self.db.update_user_balance(
            user_id, 
            points_amount=AD_REWARD_POINTS,
            update_earned=True
        )
        
        # تسجيل المشاهدة
        self.db.add_ad_watch(user_id, AD_REWARD_POINTS)
        
        user_data = self.db.get_user(user_id)
        remaining = DAILY_ADS_LIMIT - (today_ads + 1)
        
        await update.callback_query.answer(
            f"✅ +{AD_REWARD_POINTS} نقطة! رصيدك: {user_data['balance_points']:.0f} نقطة\n"
            f"📺 متبقي {remaining} إعلان اليوم",
            show_alert=True
        )
        
        # تحديث القائمة
        await self.show_ads_menu(update, context)