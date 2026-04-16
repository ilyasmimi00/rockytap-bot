# handlers/withdraw.py
"""
معالج السحب
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import WITHDRAWAL_MIN, WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class WithdrawHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_withdraw_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة السحب"""
        user = update.effective_user
        user_id = user.id
        
        user_data = self.db.get_user(user_id)
        withdrawals = self.db.get_user_withdrawals(user_id, limit=5)
        pending_count = len([w for w in withdrawals if w['status'] == 'pending'])
        
        # التحقق من شروط السحب (المهام المجانية)
        eligibility = self._check_withdrawal_eligibility(user_id)
        
        text = f"""
💸 <b>سحب الأرباح</b>
━━━━━━━━━━━━━━━━━━
💰 <b>الرصيد المتاح:</b> <code>{user_data['balance_ton']:.4f}</code> TON
📉 <b>الحد الأدنى:</b> <code>{WITHDRAWAL_MIN:.4f}</code> TON
⏳ <b>طلبات معلقة:</b> <code>{pending_count}</code>
━━━━━━━━━━━━━━━━━━
📋 <b>شروط السحب:</b>
• ✅ المهام المنجزة: <code>{eligibility['completed_tasks']}</code>
• 🎁 المهام المجانية: <code>{eligibility['free_completed']}/{eligibility['free_total']}</code>
━━━━━━━━━━━━━━━━━━
        """
        
        if not eligibility['can_withdraw']:
            text += f"\n⚠️ <b>{eligibility['reason']}</b>\n"
        
        keyboard = [
            [InlineKeyboardButton("🌐 صفحة السحب", web_app=WebAppInfo(url=f"{WEBAPP_URL}/withdraw.html"))],
            [InlineKeyboardButton("📋 سجل السحوبات", callback_data='withdraw_history')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def show_withdraw_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض سجل السحوبات"""
        user = update.effective_user
        user_id = user.id
        
        withdrawals = self.db.get_user_withdrawals(user_id, limit=20)
        
        if not withdrawals:
            text = "📋 <b>لا توجد سحوبات سابقة</b>"
        else:
            text = "📋 <b>سجل السحوبات</b>\n━━━━━━━━━━━━━━━━━━\n"
            for w in withdrawals:
                status_emoji = {
                    'pending': '⏳',
                    'paid': '✅',
                    'rejected': '❌'
                }.get(w['status'], '❓')
                
                text += f"{status_emoji} #{w['id']}: <code>{w['amount']:.4f}</code> TON – {w['status']}\n"
                text += f"   📅 {w['requested_at']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='withdraw_menu')]]
        
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح صفحة السحب في WebApp"""
        user = update.effective_user
        user_id = user.id
        
        # التحقق من شروط السحب
        eligibility = self._check_withdrawal_eligibility(user_id)
        
        if not eligibility['can_withdraw']:
            await update.callback_query.answer(eligibility['reason'], show_alert=True)
            return
        
        # فتح صفحة الويب
        keyboard = [[InlineKeyboardButton(
            "🌐 فتح صفحة السحب",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/withdraw.html?user_id={user_id}")
        )]]
        
        await update.callback_query.edit_message_text(
            "🔗 اضغط على الزر أدناه لفتح صفحة السحب:\n\n"
            "📝 أدخل عنوان محفظتك والمبلغ المطلوب",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def _check_withdrawal_eligibility(self, user_id):
        """التحقق من شروط السحب"""
        user_data = self.db.get_user(user_id)
        free_tasks_status = self.db.get_user_free_tasks_status(user_id)
        
        free_completed = sum(1 for t in free_tasks_status if t['status'] == 'completed')
        free_total = len(free_tasks_status)
        total_tasks = user_data.get('completed_tasks', 0) + free_completed
        
        can_withdraw = user_data['balance_ton'] >= WITHDRAWAL_MIN
        
        if user_data.get('first_withdrawal_completed', False):
            reason = "يمكنك السحب" if can_withdraw else "الرصيد غير كافٍ"
        else:
            if total_tasks < 8:
                can_withdraw = False
                reason = f"هذا أول سحب لك. تحتاج 8 مهام منفذة. لديك {total_tasks} مهام"
            else:
                reason = "يمكنك السحب" if can_withdraw else "الرصيد غير كافٍ"
        
        return {
            'can_withdraw': can_withdraw,
            'reason': reason,
            'completed_tasks': user_data.get('completed_tasks', 0),
            'free_completed': free_completed,
            'free_total': free_total
        }