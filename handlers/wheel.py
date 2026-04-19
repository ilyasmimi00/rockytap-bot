# handlers/wheel.py
"""
معالج عجلة الحظ - نسخة كاملة مع Rate Limiting
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import DAILY_WHEEL_SPINS, WHEEL_REWARDS, WEBAPP_URL
import random
import secrets
import logging

logger = logging.getLogger(__name__)

# محاولة استيراد Rate Limiting (إذا كان متاحاً)
try:
    from utils.rate_limit import rate_limit
    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False
    # تعريف decorator بديل إذا لم يكن متاحاً
    def rate_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class WheelHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_wheel_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة عجلة الحظ"""
        try:
            user = update.effective_user
            user_id = user.id
            
            today_spins = self.db.get_today_wheel_spins(user_id)
            remaining = max(0, DAILY_WHEEL_SPINS - today_spins)
            
            # جلب إجمالي النقاط من العجلة
            total_points = self.db.get_user_wheel_total(user_id) if hasattr(self.db, 'get_user_wheel_total') else 0
            
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
🏆 <b>إجمالي أرباح العجلة:</b> {total_points} نقطة
━━━━━━━━━━━━━━━━━━
⚠️ يتم إعادة تعيين المحاولات يومياً في منتصف الليل
            """
            
            keyboard = []
            
            if remaining > 0:
                keyboard.append([InlineKeyboardButton("🎡 ابدأ اللعب", callback_data='spin_wheel')])
            
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')])
            
            await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in show_wheel_menu: {e}")
            await update.callback_query.edit_message_text(
                "❌ حدث خطأ في تحميل العجلة. يرجى المحاولة مرة أخرى."
            )
    
    @rate_limit(command='spin_wheel') if RATE_LIMIT_AVAILABLE else (lambda x: x)
    async def spin_wheel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اللعب في عجلة الحظ - مع تحديد معدل الطلبات"""
        try:
            user = update.effective_user
            user_id = user.id
            
            today_spins = self.db.get_today_wheel_spins(user_id)
            
            if today_spins >= DAILY_WHEEL_SPINS:
                await update.callback_query.answer(
                    "⚠️ لقد استنفدت جميع محاولاتك اليوم! عود غداً.", 
                    show_alert=True
                )
                return
            
            # ✅ تحسين العشوائية: استخدام secrets بدلاً من random
            # secrets.choice أكثر أماناً للاستخدامات المتعلقة بالمال
            try:
                reward = secrets.choice(WHEEL_REWARDS)
            except AttributeError:
                # إذا لم يكن secrets متاحاً (إصدارات قديمة من Python)
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
            remaining = max(0, DAILY_WHEEL_SPINS - (today_spins + 1))
            
            # رسالة النجاح
            await update.callback_query.answer(
                f"🎉 مبروك! ربحت {reward} نقطة!\n"
                f"⭐ رصيدك: {user_data['balance_points']:.0f} نقطة\n"
                f"🎡 متبقي {remaining} محاولة اليوم",
                show_alert=True
            )
            
            # تحديث القائمة
            await self.show_wheel_menu(update, context)
            
        except Exception as e:
            logger.error(f"Error in spin_wheel: {e}")
            await update.callback_query.answer(
                "❌ حدث خطأ أثناء اللعب. يرجى المحاولة مرة أخرى.",
                show_alert=True
            )
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح صفحة عجلة الحظ في WebApp"""
        try:
            user = update.effective_user
            user_id = user.id
            
            keyboard = [[
                InlineKeyboardButton(
                    "🎡 فتح عجلة الحظ",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/wheel.html?user_id={user_id}")
                )
            ]]
            
            await update.callback_query.edit_message_text(
                "🎡 اضغط على الزر أدناه لفتح عجلة الحظ:\n\n"
                "💫 أدر العجلة واربح نقاطاً إضافية!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error in open_webapp: {e}")
            await update.callback_query.edit_message_text(
                "❌ حدث خطأ. يرجى المحاولة مرة أخرى."
            )
    
    async def get_wheel_status(self, user_id: int) -> dict:
        """
        الحصول على حالة عجلة الحظ للمستخدم
        تستخدم من قبل API أو صفحات الويب
        """
        try:
            today_spins = self.db.get_today_wheel_spins(user_id)
            remaining = max(0, DAILY_WHEEL_SPINS - today_spins)
            user_data = self.db.get_user(user_id)
            
            return {
                'success': True,
                'remaining_spins': remaining,
                'total_points': user_data['balance_points'] if user_data else 0,
                'daily_limit': DAILY_WHEEL_SPINS,
                'used_today': today_spins,
                'rewards': WHEEL_REWARDS
            }
        except Exception as e:
            logger.error(f"Error in get_wheel_status: {e}")
            return {
                'success': False,
                'message': str(e),
                'remaining_spins': 0,
                'total_points': 0
            }
    
    async def admin_reset_spins(self, user_id: int):
        """
        إعادة تعيين محاولات عجلة الحظ لمستخدم (للمشرفين فقط)
        """
        try:
            # هذه دالة مساعدة للمشرفين - تحتاج إلى إضافتها في database.py
            if hasattr(self.db, 'reset_user_wheel_spins'):
                self.db.reset_user_wheel_spins(user_id)
                return True, "تم إعادة تعيين محاولات العجلة"
            else:
                # طريقة بديلة: حذف سجلات اليوم وإعادة إنشاؤها
                logger.warning(f"reset_user_wheel_spins not implemented in database")
                return False, "الدالة غير متوفرة في قاعدة البيانات"
        except Exception as e:
            logger.error(f"Error in admin_reset_spins: {e}")
            return False, str(e)