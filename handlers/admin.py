# handlers/admin.py
"""
معالج لوحة التحكم للمشرفين - النسخة الكاملة مع إدارة المهام
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AdminHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.admin_ids = bot.admin_ids
        self.webapp_url = bot.webapp_url
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /admin - فتح لوحة الأدمن"""
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
            )
        ]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض لوحة تحكم الأدمن"""
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
        
        text = f"""
👑 <b>لوحة تحكم الأدمن - {self.bot.bot_name}</b>
━━━━━━━━━━━━━━━━━━
📌 اختر القسم الذي تريد إدارته:
        """
        
        keyboard = [
            [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data='admin_users_menu')],
            [InlineKeyboardButton("📋 إدارة المهام", callback_data='admin_tasks_menu')],
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
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح لوحة التحكم عبر WebApp"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.admin_ids:
            await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
            return
        
        keyboard = [[
            InlineKeyboardButton(
                "👑 فتح لوحة التحكم",
                web_app=WebAppInfo(url=f"{self.webapp_url}/admin.html")
            )
        ]]
        
        await query.edit_message_text(
            "🌐 اضغط على الزر أدناه لفتح لوحة التحكم المتكاملة:\n\n"
            "📊 يمكنك من هنا:\n"
            "• إدارة المستخدمين\n"
            "• إدارة المهام\n"
            "• تعديل إعدادات الإحالات\n"
            "• معالجة طلبات السحب\n"
            "• إنشاء الأكواد الترويجية\n"
            "• تعديل إعدادات النظام",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ==================== قوائم الأدمن ====================
    
    async def users_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة المستخدمين"""
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
    
    async def tasks_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة المهام"""
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
    
    async def referral_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إعدادات الإحالات"""
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
    
    async def withdrawals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة طلبات السحب"""
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
    
    async def codes_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إدارة الأكواد"""
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
    
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إعدادات النظام"""
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
    
    # ==================== إنشاء المهام من البوت ====================
    
    async def create_task_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """طلب إدخال بيانات المهمة الجديدة"""
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
    
    async def handle_task_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال بيانات المهمة الجديدة"""
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
        
        try:
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
                
                # تسجيل في سجل الأدمن
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
            await message.reply_text(f"❌ حدث خطأ غير متوقع: {str(e)}")
        
        context.user_data['awaiting_task_creation'] = False
        return True
    
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة جميع المهام للمشرف"""
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
        
        text = "📋 <b>قائمة المهام</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        
        for task in tasks:
            reward_text = ""
            if task['reward_points'] > 0:
                reward_text += f"⭐ {task['reward_points']}"
            if task['reward_ton'] > 0:
                if reward_text:
                    reward_text += " + "
                reward_text += f"💰 {task['reward_ton']}"
            
            text += f"<b>{task['icon']} {task['title']}</b>\n"
            text += f"📝 {task['description'][:50]}...\n" if task['description'] else ""
            text += f"🎁 {reward_text}\n"
            text += f"🔗 {task['channel_username']}\n"
            text += f"👥 مكتمل: {task.get('completed_count', 0)} مستخدم\n"
            text += f"🆔 ID: {task['id']}\n"
            text += "━━━━━━━━━━━━━━━━━━\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ إنشاء مهمة جديدة", callback_data='admin_create_task')],
            [InlineKeyboardButton("🗑️ حذف مهمة", callback_data='admin_delete_task_form')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='admin_tasks_menu')]
        ]
        
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def delete_task_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """طلب معرف المهمة للحذف"""
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
    
    async def handle_task_deletion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة حذف مهمة"""
        if not context.user_data.get('awaiting_task_deletion'):
            return False
        
        message = update.message
        user_id = update.effective_user.id
        text = message.text.strip()
        
        if text == '/cancel':
            context.user_data['awaiting_task_deletion'] = False
            await message.reply_text("❌ تم إلغاء حذف المهمة")
            return True
        
        try:
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
                
                self.db.add_admin_log(
                    admin_id=user_id,
                    action="حذف مهمة",
                    details=f"تم حذف مهمة '{task['title']}'"
                )
            else:
                await message.reply_text("❌ حدث خطأ أثناء حذف المهمة")
        
        except ValueError:
            await message.reply_text("❌ يرجى إدخال معرف (ID) صحيح للمهمة")
        
        context.user_data['awaiting_task_deletion'] = False
        return True
    
    # ==================== معالج الأزرار ====================
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الأدمن"""
        query = update.callback_query
        data = query.data
        user_id = query.from_user.id
        
        if user_id not in self.admin_ids:
            await query.answer("⛔ أنت لست مشرفاً", show_alert=True)
            return
        
        # قائمة المهام
        if data == 'admin_tasks_menu':
            await self.tasks_menu(update, context)
        elif data == 'admin_create_task':
            await self.create_task_input(update, context)
        elif data == 'admin_list_tasks':
            await self.list_tasks(update, context)
        elif data == 'admin_delete_task_form':
            await self.delete_task_form(update, context)
        
        # القوائم الأخرى
        elif data == 'admin_panel':
            await self.show_admin_panel(update, context)
        elif data == 'admin_open_webapp':
            await self.open_webapp(update, context)
        elif data == 'admin_users_menu':
            await self.users_menu(update, context)
        elif data == 'admin_referral_menu':
            await self.referral_menu(update, context)
        elif data == 'admin_withdrawals_menu':
            await self.withdrawals_menu(update, context)
        elif data == 'admin_codes_menu':
            await self.codes_menu(update, context)
        elif data == 'admin_settings_menu':
            await self.settings_menu(update, context)
        else:
            await query.answer("❓ إجراء غير معروف", show_alert=True)