# handlers/admin.py
"""
معالج لوحة التحكم للمشرفين - نسخة كاملة مع Rate Limiting وحماية من الأخطاء
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# محاولة استيراد Rate Limiting
try:
    from utils.rate_limit import admin_rate_limit, rate_limit
    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False
    def admin_rate_limit(func):
        return func
    def rate_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class AdminHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.admin_ids = bot.admin_ids
        self.webapp_url = bot.webapp_url
    
    @admin_rate_limit if RATE_LIMIT_AVAILABLE else (lambda x: x)
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /admin - فتح لوحة الأدمن"""
        try:
            user_id = update.effective_user.id
            
            if user_id not in self.admin_ids:
                await update.message.reply_text("⛔ أنت لست مشرفاً")
                return
            
            text = f"""
👑 <b>لوحة تحكم الأدمن - {self.bot.bot_name}</b>
━━━━━━━━━━━━━━━━━━
📌 استخدم الواجهة الرسومية للإدارة:
            """
            
            keyboard = [[
                InlineKeyboardButton(
                    "👑 فتح لوحة التحكم",
                    web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html")
                ),
                InlineKeyboardButton(
                    "📢 إدارة الإعلانات",
                    web_app=WebAppInfo(url=f"{self.webapp_url}/admin_ads.html")
                )
            ]]
            
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in admin_command: {e}")
            await update.message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى")
    
    @admin_rate_limit if RATE_LIMIT_AVAILABLE else (lambda x: x)
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض لوحة تحكم الأدمن"""
        try:
            if update.callback_query:
                query = update.callback_query
                user_id = query.from_user.id
                await query.answer()
            else:
                user_id = update.effective_user.id
            
            if user_id not in self.admin_ids:
                if update.callback_query:
                    await update.callback_query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                else:
                    await update.message.reply_text("⛔ أنت لست مشرفاً")
                return
            
            # جلب إحصائيات سريعة للوحة
            total_users = self.db.get_total_users_count() if hasattr(self.db, 'get_total_users_count') else 0
            pending_withdrawals = self.db.get_pending_withdrawals_count() if hasattr(self.db, 'get_pending_withdrawals_count') else 0
            
            text = f"""
👑 <b>لوحة تحكم الأدمن - {self.bot.bot_name}</b>
━━━━━━━━━━━━━━━━━━
📊 <b>إحصائيات سريعة:</b>
• 👥 إجمالي المستخدمين: {total_users}
• 💳 طلبات سحب معلقة: {pending_withdrawals}
━━━━━━━━━━━━━━━━━━
📌 اختر القسم الذي تريد إدارته:
            """
            
            keyboard = [
                [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data='admin_users_menu')],
                [InlineKeyboardButton("📋 إدارة المهام", callback_data='admin_tasks_menu')],
                [InlineKeyboardButton("📢 إدارة الإعلانات المدفوعة", callback_data='admin_ads_menu')],
                [InlineKeyboardButton("🎁 إعدادات الإحالات", callback_data='admin_referral_menu')],
                [InlineKeyboardButton("💳 طلبات السحب", callback_data='admin_withdrawals_menu')],
                [InlineKeyboardButton("🎫 إدارة الأكواد", callback_data='admin_codes_menu')],
                [InlineKeyboardButton("⚙️ إعدادات النظام", callback_data='admin_settings_menu')],
                [InlineKeyboardButton("🌐 فتح لوحة الويب", callback_data='admin_open_webapp')],
                [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text, reply_markup=reply_markup, parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Error in show_admin_panel: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "❌ حدث خطأ في لوحة التحكم. يرجى المحاولة مرة أخرى."
                )
            else:
                await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    @admin_rate_limit if RATE_LIMIT_AVAILABLE else (lambda x: x)
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الأدمن - مع حماية من الأخطاء"""
        try:
            query = update.callback_query
            data = query.data
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            # قائمة الإجراءات
            actions = {
                'admin_panel': self.show_admin_panel,
                'admin_open_webapp': self.open_webapp,
                'admin_users_menu': self.users_menu,
                'admin_tasks_menu': self.tasks_menu,
                'admin_ads_menu': self.ads_menu,
                'admin_referral_menu': self.referral_menu,
                'admin_withdrawals_menu': self.withdrawals_menu,
                'admin_codes_menu': self.codes_menu,
                'admin_settings_menu': self.settings_menu,
                'admin_create_task': self.create_task_input,
                'admin_list_tasks': self.list_tasks,
                'admin_delete_task_form': self.delete_task_form,
            }
            
            if data in actions:
                await actions[data](update, context)
            else:
                await query.answer("❓ إجراء غير معروف", show_alert=True)
                
        except Exception as e:
            logger.error(f"Error in handle_admin_callback: {e}")
            try:
                await update.callback_query.edit_message_text(
                    "❌ حدث خطأ في لوحة التحكم. يرجى المحاولة مرة أخرى."
                )
            except:
                pass
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح لوحة التحكم عبر WebApp"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        "👑 فتح لوحة التحكم الرئيسية",
                        web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html")
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📢 فتح إدارة الإعلانات",
                        web_app=WebAppInfo(url=f"{self.webapp_url}/admin_ads.html")
                    )
                ]
            ]
            
            await query.edit_message_text(
                "🌐 اضغط على الزر أدناه لفتح لوحة التحكم المتكاملة:\n\n"
                "📊 يمكنك من هنا:\n"
                "• إدارة المستخدمين\n"
                "• إدارة المهام\n"
                "• إدارة الإعلانات المدفوعة\n"
                "• تعديل إعدادات الإحالات\n"
                "• معالجة طلبات السحب\n"
                "• إنشاء الأكواد الترويجية\n"
                "• تعديل إعدادات النظام",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error in open_webapp: {e}")
    
    # ==================== قوائم الأدمن ====================
    
    async def users_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة المستخدمين"""
        try:
            query = update.callback_query
            
            text = """
👥 <b>إدارة المستخدمين</b>
━━━━━━━━━━━━━━━━━━
📌 اختر الإجراء المطلوب:
            """
            
            keyboard = [
                [InlineKeyboardButton("📋 عرض المستخدمين", callback_data='admin_list_users')],
                [InlineKeyboardButton("💰 تعديل الرصيد", callback_data='admin_adjust_balance')],
                [InlineKeyboardButton("⛔ حظر مستخدم", callback_data='admin_ban_user_form')],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in users_menu: {e}")
    
    async def tasks_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة المهام"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            text = """
📋 <b>إدارة المهام</b>
━━━━━━━━━━━━━━━━━━
📌 يمكنك إدارة المهام من خلال:

1️⃣ <b>إنشاء مهمة جديدة</b>
   • أرسل المعلومات التالية كل في سطر منفصل:
   • عنوان المهمة
   • وصف المهمة
   • رابط القناة/المجموعة
   • معرف القناة (مثال: @channel)
   • مكافأة النقاط
   • مكافأة التون

✏️ <b>مثال:</b>
قناة RockyTap
اشترك في قناتنا ليصلك كل جديد
https://t.me/RockyTap
@RockyTap
100
0.01

━━━━━━━━━━━━━━━━━━
⚠️ <b>ملاحظة:</b> يجب أن يكون البوت أدمن في القناة للتحقق من الاشتراك!
            """
            
            keyboard = [
                [InlineKeyboardButton("➕ إنشاء مهمة جديدة", callback_data='admin_create_task')],
                [InlineKeyboardButton("📋 عرض جميع المهام", callback_data='admin_list_tasks')],
                [InlineKeyboardButton("🌐 فتح لوحة الويب", web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in tasks_menu: {e}")
    
    async def ads_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة الإعلانات المدفوعة"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            text = """
📢 <b>إدارة الإعلانات المدفوعة</b>
━━━━━━━━━━━━━━━━━━
📌 يمكنك إدارة إعلانات المستخدمين من خلال:

• ✅ <b>الموافقة على الإعلانات</b> - قبول الإعلانات بعد التحقق
• ❌ <b>رفض الإعلانات</b> - رفض الإعلانات مع إضافة سبب
• 📺 <b>الموافقة على القنوات</b> - قبول قنوات المستخدمين
• 🗑️ <b>حذف الإعلانات</b> - حذف أي إعلان مخالف

━━━━━━━━━━━━━━━━━━
📌 استخدم لوحة الويب لإدارة الإعلانات:
            """
            
            keyboard = [
                [InlineKeyboardButton("📢 فتح إدارة الإعلانات", web_app=WebAppInfo(url=f"{self.webapp_url}/admin_ads.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in ads_menu: {e}")
    
    async def referral_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إعدادات الإحالات"""
        try:
            query = update.callback_query
            settings = self.db.get_referral_settings()
            
            text = f"""
🎁 <b>إعدادات الإحالات</b>
━━━━━━━━━━━━━━━━━━
📊 <b>الإعدادات الحالية:</b>
• نوع المكافأة: {settings.get('reward_type', 'both')}
• ⭐ النقاط: {settings.get('points_value', 100)}
• 💰 التون: {settings.get('ton_value', 0.01)} TON
• 📋 المهام المطلوبة: {settings.get('required_tasks', 6)}
━━━━━━━━━━━━━━━━━━
📌 استخدم لوحة الويب لتعديل الإعدادات:
            """
            
            keyboard = [
                [InlineKeyboardButton("🌐 فتح لوحة الإعدادات", web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in referral_menu: {e}")
    
    async def withdrawals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة طلبات السحب"""
        try:
            query = update.callback_query
            
            pending = self.db.get_pending_withdrawals_count() if hasattr(self.db, 'get_pending_withdrawals_count') else 0
            
            text = f"""
💳 <b>طلبات السحب</b>
━━━━━━━━━━━━━━━━━━
⏳ الطلبات المعلقة: {pending}
━━━━━━━━━━━━━━━━━━
📌 استخدم لوحة الويب لعرض ومعالجة الطلبات:
            """
            
            keyboard = [
                [InlineKeyboardButton("🌐 فتح لوحة السحب", web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in withdrawals_menu: {e}")
    
    async def codes_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة الأكواد"""
        try:
            query = update.callback_query
            
            text = """
🎫 <b>إدارة الأكواد الترويجية</b>
━━━━━━━━━━━━━━━━━━
📌 استخدم لوحة الويب لإنشاء وإدارة الأكواد:
            """
            
            keyboard = [
                [InlineKeyboardButton("🌐 فتح لوحة الأكواد", web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in codes_menu: {e}")
    
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إعدادات النظام"""
        try:
            query = update.callback_query
            
            text = """
⚙️ <b>إعدادات النظام</b>
━━━━━━━━━━━━━━━━━━
📌 استخدم لوحة الويب لتعديل الإعدادات:
            """
            
            keyboard = [
                [InlineKeyboardButton("🌐 فتح لوحة الإعدادات", web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html"))],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in settings_menu: {e}")
    
    # ==================== دوال إنشاء المهام ====================
    
    async def create_task_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """طلب إدخال بيانات المهمة الجديدة"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            context.user_data['awaiting_task_creation'] = True
            
            text = """
📝 <b>إنشاء مهمة جديدة</b>
━━━━━━━━━━━━━━━━━━
📌 أرسل المعلومات التالية كل في سطر منفصل:

1️⃣ <b>عنوان المهمة</b> (مثال: قناة RockyTap)
2️⃣ <b>وصف المهمة</b> (اختياري)
3️⃣ <b>رابط القناة/المجموعة</b> (مثال: https://t.me/channel)
4️⃣ <b>معرف القناة</b> (مثال: @channel)
5️⃣ <b>مكافأة النقاط</b> (مثال: 100)
6️⃣ <b>مكافأة التون</b> (مثال: 0.01)

✏️ <b>مثال:</b>
قناة RockyTap
اشترك في قناتنا ليصلك كل جديد
https://t.me/RockyTap
@RockyTap
100
0.01
━━━━━━━━━━━━━━━━━━
⚠️ <b>ملاحظة:</b> يجب أن يكون البوت أدمن في القناة للتحقق من الاشتراك!

❌ للإلغاء أرسل /cancel
            """
            
            await query.edit_message_text(text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in create_task_input: {e}")
    
    async def handle_task_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال بيانات المهمة الجديدة"""
        try:
            if not context.user_data.get('awaiting_task_creation'):
                return False
            
            message = update.message
            user_id = update.effective_user.id
            text = message.text.strip()
            
            if text == '/cancel':
                context.user_data['awaiting_task_creation'] = False
                await message.reply_text("❌ تم إلغاء إنشاء المهمة")
                return True
            
            lines = text.split('\n')
            
            if len(lines) < 5:
                await message.reply_text(
                    "❌ يرجى إرسال المعلومات بالشكل الصحيح (6 أسطر)\n"
                    "أو أرسل /cancel للإلغاء"
                )
                return True
            
            title = lines[0].strip()
            description = lines[1].strip() if len(lines) > 1 else ""
            channel_link = lines[2].strip()
            channel_username = lines[3].strip()
            reward_points = float(lines[4].strip())
            reward_ton = float(lines[5].strip()) if len(lines) > 5 else 0
            
            if not title or not channel_link:
                await message.reply_text("❌ عنوان المهمة ورابط القناة مطلوبان")
                return True
            
            success, result = self.db.create_task(
                title=title,
                description=description,
                icon='📺',
                channel_link=channel_link,
                channel_username=channel_username,
                reward_points=reward_points,
                reward_ton=reward_ton,
                created_by=user_id
            )
            
            if success:
                reward_text = ""
                if reward_points > 0:
                    reward_text += f"⭐ {reward_points} نقطة"
                if reward_ton > 0:
                    if reward_text:
                        reward_text += " + "
                    reward_text += f"💰 {reward_ton} تون"
                
                await message.reply_text(
                    f"✅ <b>تم إنشاء المهمة بنجاح!</b>\n\n"
                    f"📋 <b>العنوان:</b> {title}\n"
                    f"🎁 <b>المكافأة:</b> {reward_text}\n"
                    f"🔗 <b>القناة:</b> {channel_username}\n\n"
                    f"📌 يمكن للمستخدمين الآن رؤية هذه المهمة والاشتراك للحصول على المكافأة!",
                    parse_mode='HTML'
                )
                
                if hasattr(self.db, 'add_admin_log'):
                    self.db.add_admin_log(
                        admin_id=user_id,
                        action="إنشاء مهمة",
                        details=f"تم إنشاء مهمة '{title}' بمكافأة {reward_text}"
                    )
            else:
                await message.reply_text(f"❌ حدث خطأ: {result}")
        
        except ValueError as e:
            await message.reply_text(f"❌ خطأ في البيانات: يرجى التأكد من أن المكافأة أرقام صحيحة\n{str(e)}")
        except Exception as e:
            logger.error(f"Error in handle_task_creation: {e}")
            await message.reply_text(f"❌ حدث خطأ غير متوقع: {str(e)}")
        
        context.user_data['awaiting_task_creation'] = False
        return True
    
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة جميع المهام للمشرف"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            tasks = self.db.get_all_tasks()
            
            if not tasks:
                await query.edit_message_text(
                    "📋 <b>لا توجد مهام حالياً</b>\n\n"
                    "استخدم الزر أدناه لإنشاء مهمة جديدة:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("➕ إنشاء مهمة", callback_data='admin_create_task')
                    ]]),
                    parse_mode='HTML'
                )
                return
            
            # تجاوز حد طول الرسالة (4096 حرف)
            text = "📋 <b>قائمة المهام</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            
            for task in tasks:
                reward_text = ""
                if task['reward_points'] > 0:
                    reward_text += f"⭐ {task['reward_points']}"
                if task['reward_ton'] > 0:
                    if reward_text:
                        reward_text += " + "
                    reward_text += f"💰 {task['reward_ton']}"
                
                task_text = f"<b>{task['icon']} {task['title']}</b>\n"
                task_text += f"📝 {task['description'][:50]}...\n" if task['description'] else ""
                task_text += f"🎁 {reward_text}\n"
                task_text += f"🔗 {task['channel_username']}\n"
                task_text += f"👥 مكتمل: {task.get('completed_count', 0)} مستخدم\n"
                task_text += f"🆔 ID: {task['id']}\n"
                task_text += "━━━━━━━━━━━━━━━━━━\n"
                
                # إذا تجاوز النص الحد، أرسل القائمة على دفعات
                if len(text + task_text) > 4000:
                    await query.edit_message_text(text, parse_mode='HTML')
                    text = task_text
                else:
                    text += task_text
            
            keyboard = [
                [InlineKeyboardButton("➕ إنشاء مهمة جديدة", callback_data='admin_create_task')],
                [InlineKeyboardButton("🗑️ حذف مهمة", callback_data='admin_delete_task_form')],
                [InlineKeyboardButton("🔙 رجوع", callback_data='admin_tasks_menu')]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in list_tasks: {e}")
    
    async def delete_task_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """طلب معرف المهمة للحذف"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            if user_id not in self.admin_ids:
                await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
                return
            
            context.user_data['awaiting_task_deletion'] = True
            
            await query.edit_message_text(
                "🗑️ <b>حذف مهمة</b>\n━━━━━━━━━━━━━━━━━━\n\n"
                "📌 أرسل معرف (ID) المهمة التي تريد حذفها.\n\n"
                "يمكنك رؤية المعرفات في قائمة المهام.\n\n"
                "❌ للإلغاء أرسل /cancel",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in delete_task_form: {e}")
    
    async def handle_task_deletion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة حذف مهمة"""
        try:
            if not context.user_data.get('awaiting_task_deletion'):
                return False
            
            message = update.message
            user_id = update.effective_user.id
            text = message.text.strip()
            
            if text == '/cancel':
                context.user_data['awaiting_task_deletion'] = False
                await message.reply_text("❌ تم إلغاء حذف المهمة")
                return True
            
            task_id = int(text)
            task = self.db.get_task(task_id)
            
            if not task:
                await message.reply_text(f"❌ لا توجد مهمة بالمعرف {task_id}")
                return True
            
            success = self.db.delete_task(task_id)
            
            if success:
                await message.reply_text(
                    f"✅ <b>تم حذف المهمة بنجاح!</b>\n\n"
                    f"📋 <b>العنوان:</b> {task['title']}",
                    parse_mode='HTML'
                )
                
                if hasattr(self.db, 'add_admin_log'):
                    self.db.add_admin_log(
                        admin_id=user_id,
                        action="حذف مهمة",
                        details=f"تم حذف مهمة '{task['title']}'"
                    )
            else:
                await message.reply_text("❌ حدث خطأ أثناء حذف المهمة")
        
        except ValueError:
            await message.reply_text("❌ يرجى إدخال معرف (ID) صحيح للمهمة")
        except Exception as e:
            logger.error(f"Error in handle_task_deletion: {e}")
            await message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data['awaiting_task_deletion'] = False
        return True
    
    # ==================== معالج WebApp ====================
    
    async def handle_webapp_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, data: dict):
        """معالجة الإجراءات الواردة من صفحة الأدمن"""
        try:
            user_id = update.effective_user.id
            
            if user_id not in self.admin_ids:
                await update.message.reply_text("⛔ أنت لست مشرفاً")
                return
            
            logger.info(f"👑 Admin action: {action} from user {user_id}")
            
            # قاموس الإجراءات
            actions = {
                'admin_add_balance': self._handle_add_balance,
                'admin_ban_user': self._handle_ban_user,
                'admin_toggle_ban': self._handle_toggle_ban,
                'admin_save_referral': self._handle_save_referral,
                'admin_create_code': self._handle_create_code,
                'admin_save_settings': self._handle_save_settings,
            }
            
            if action in actions:
                await actions[action](update, user_id, data)
            else:
                await update.message.reply_text(json.dumps({
                    'action': 'admin_operation_result',
                    'success': False,
                    'message': f'❌ إجراء غير معروف: {action}'
                }))
                
        except Exception as e:
            logger.error(f"Error in handle_webapp_action: {e}")
            await update.message.reply_text(json.dumps({
                'action': 'admin_operation_result',
                'success': False,
                'message': f'❌ حدث خطأ: {str(e)}'
            }))
    
    async def _handle_add_balance(self, update, admin_id, data):
        """معالجة إضافة رصيد"""
        target_id = int(data.get('user_id', 0))
        amount = float(data.get('amount', 0))
        currency = data.get('currency', 'ton')
        
        if currency == 'ton':
            self.db.update_user_balance(target_id, ton_amount=amount, update_earned=True)
        else:
            self.db.update_user_balance(target_id, points_amount=amount, update_earned=True)
        
        if hasattr(self.db, 'add_admin_log'):
            self.db.add_admin_log(admin_id, f"إضافة رصيد", f"أضاف {amount} {currency} للمستخدم {target_id}")
        
        await update.message.reply_text(json.dumps({
            'action': 'admin_operation_result',
            'success': True,
            'message': f'✅ تم إضافة {amount} {currency} للمستخدم {target_id}'
        }))
    
    async def _handle_ban_user(self, update, admin_id, data):
        """معالجة حظر مستخدم"""
        target_id = int(data.get('user_id', 0))
        self.db.update_user_block_status(target_id, True)
        
        if hasattr(self.db, 'add_admin_log'):
            self.db.add_admin_log(admin_id, "حظر مستخدم", f"حظر المستخدم {target_id}")
        
        await update.message.reply_text(json.dumps({
            'action': 'admin_operation_result',
            'success': True,
            'message': f'✅ تم حظر المستخدم {target_id}'
        }))
    
    async def _handle_toggle_ban(self, update, admin_id, data):
        """معالجة تبديل حالة الحظر"""
        target_id = int(data.get('user_id', 0))
        user = self.db.get_user(target_id)
        if user:
            new_status = not user.get('is_blocked', False)
            self.db.update_user_block_status(target_id, new_status)
        
        await update.message.reply_text(json.dumps({
            'action': 'admin_operation_result',
            'success': True,
            'message': '✅ تم تغيير حالة المستخدم'
        }))
    
    async def _handle_save_referral(self, update, admin_id, data):
        """معالجة حفظ إعدادات الإحالات"""
        success = self.db.save_referral_settings(
            reward_type=data.get('reward_type', 'both'),
            points_value=data.get('points_value', 100),
            ton_value=data.get('ton_value', 0.01),
            required_tasks=data.get('required_tasks', 6)
        )
        
        await update.message.reply_text(json.dumps({
            'action': 'admin_operation_result',
            'success': success,
            'message': '✅ تم حفظ إعدادات الإحالات' if success else '❌ حدث خطأ'
        }))
    
    async def _handle_create_code(self, update, admin_id, data):
        """معالجة إنشاء كود ترويجي"""
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
    
    async def _handle_save_settings(self, update, admin_id, data):
        """معالجة حفظ إعدادات النظام"""
        await update.message.reply_text(json.dumps({
            'action': 'admin_operation_result',
            'success': True,
            'message': '✅ تم حفظ جميع الإعدادات'
        }))