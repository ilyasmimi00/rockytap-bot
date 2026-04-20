# handlers/referral.py - النسخة المصححة
"""
معالج الإحالات - نسخة مصححة بالكامل
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class ReferralHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_referral_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإحالات"""
        user = update.effective_user
        user_id = user.id
        
        stats = self.db.get_user_referrals_stats(user_id)
        settings = self.db.get_referral_settings()
        
        if settings['reward_type'] == 'points':
            reward_text = f"⭐ {settings['points_value']} نقطة"
        elif settings['reward_type'] == 'ton':
            reward_text = f"💰 {settings['ton_value']:.4f} تون"
        else:
            reward_text = f"⭐ {settings['points_value']} نقطة + 💰 {settings['ton_value']:.4f} تون"
        
        # ✅ الإصلاح: استخدام context.bot بدلاً من self.bot.application.bot
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        text = f"""
🔗 <b>نظام الإحالات</b>
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
━━━━━━━━━━━━━━━━━━
✨ <b>كيف تعمل الإحالة؟</b>
1️⃣ أرسل الرابط لأصدقائك
2️⃣ عندما ينضم صديقك عبر الرابط
3️⃣ بعد إكمال {settings['required_tasks']} مهام، تحصل على المكافأة فوراً 🎁
        """
        
        if stats['referrals']:
            text += "\n📋 <b>قائمة المدعوين:</b>\n"
            for ref in stats['referrals'][:5]:
                status_icon = "✅" if ref['status'] == 'مكتمل' else "⏳"
                text += f"{status_icon} @{ref['username']} | {ref['date']}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔗 مشاركة الرابط", callback_data='share_referral')],
            [InlineKeyboardButton("🌐 صفحة الإحالات", web_app=WebAppInfo(url=f"{WEBAPP_URL}/referral.html"))],
            [InlineKeyboardButton("🔄 تحديث", callback_data='referral_menu')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
    
    async def share_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مشاركة رابط الإحالة"""
        user = update.effective_user
        user_id = user.id
        
        # ✅ الإصلاح: استخدام context.bot
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        text = f"""
🎉 انضم إلي في RockyTap واربح العملات الرقمية! 🎉

💰 اربح نقاط وتون من خلال:
• مشاهدة الإعلانات
• لعب عجلة الحظ
• إكمال المهام اليومية

🔗 رابط الدعوة الخاص بي:
{referral_link}

🚀 ابدأ الآن وانضم إلى المتعة!
        """
        
        keyboard = [[
            InlineKeyboardButton("📤 مشاركة", switch_inline_query=text),
            InlineKeyboardButton("🔗 نسخ الرابط", callback_data='copy_referral_link')
        ]]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "📤 اضغط على الزر لمشاركة الرابط مع أصدقائك:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def copy_referral_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نسخ رابط الإحالة"""
        user = update.effective_user
        user_id = user.id
        
        # ✅ الإصلاح: استخدام context.bot
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        await update.callback_query.answer(f"✅ تم نسخ الرابط: {referral_link}", show_alert=True)
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح صفحة الإحالات في WebApp"""
        user = update.effective_user
        user_id = user.id
        
        keyboard = [[
            InlineKeyboardButton(
                "🔗 فتح صفحة الإحالات",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/referral.html?user_id={user_id}")
            )
        ]]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🔗 اضغط على الزر أدناه لفتح صفحة الإحالات:\n\n"
                "📋 ستظهر لك رابط الإحالة وإحصائياتك التفصيلية",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # ✅ الدالة المصححة بالكامل
    async def handle_referral_join(self, user_id: int, referrer_id: int, bot):
        """
        معالجة انضمام مستخدم عبر رابط إحالة
        - تستقبل bot كمعامل مباشرة
        - لا تستخدم self.bot.application.bot
        """
        result, msg = self.db.create_referral(
            referrer_id=referrer_id,
            referred_id=user_id,
            referred_username=None
        )
        
        if result:
            logger.info(f"✅ New referral: {referrer_id} -> {user_id}")
            
            # ✅ الإصلاح: استخدام المعامل bot مباشرة
            try:
                await bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 <b>مبروك! لديك إحالة جديدة!</b>\n\n"
                         f"👤 المستخدم الجديد: <code>{user_id}</code>\n"
                         f"📊 عندما يكمل هذا المستخدم المهام المطلوبة، ستحصل على المكافأة!",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer: {e}")
        
        return result, msg