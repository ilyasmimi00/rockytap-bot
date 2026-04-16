# handlers/tasks.py - نظام المهام المتكامل

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import WEBAPP_URL
import logging

logger = logging.getLogger(__name__)


class TasksHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def show_tasks_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة المهام"""
        user = update.effective_user
        user_id = user.id
        
        # جلب جميع المهام النشطة
        tasks = self.db.get_active_tasks()
        
        # جلب تقدم المستخدم
        user_tasks = self.db.get_user_tasks_progress(user_id)
        
        text = f"""
📋 <b>المهام المتاحة</b>
━━━━━━━━━━━━━━━━━━
💰 أكمل المهام واحصل على مكافآت فورية!
📌 اضغط على المهمة ثم اشترك في القناة/المجموعة
✅ بعد الاشتراك، اضغط "تحقق" للحصول على المكافأة
━━━━━━━━━━━━━━━━━━
"""
        
        keyboard = []
        
        for task in tasks:
            # معرفة حالة المهمة للمستخدم
            user_task = next((ut for ut in user_tasks if ut['task_id'] == task['id']), None)
            
            if user_task and user_task['status'] == 'completed':
                status_icon = "✅"
                status_text = "مكتمل"
                callback = f"task_{task['id']}_view"
            elif user_task and user_task['status'] == 'pending':
                status_icon = "⏳"
                status_text = "قيد التنفيذ"
                callback = f"task_{task['id']}_verify"
            else:
                status_icon = "📌"
                status_text = "متاحة"
                callback = f"task_{task['id']}_start"
            
            # نص المكافأة
            reward_text = ""
            if task['reward_points'] > 0:
                reward_text += f"⭐ +{task['reward_points']}"
            if task['reward_ton'] > 0:
                reward_text += f" 💰 +{task['reward_ton']}"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {task['title']} | {reward_text}",
                    callback_data=callback
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
    
    async def start_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء مهمة جديدة"""
        query = update.callback_query
        user_id = update.effective_user.id
        task_id = int(query.data.split('_')[1])
        
        # جلب بيانات المهمة
        task = self.db.get_task(task_id)
        if not task:
            await query.answer("❌ المهمة غير موجودة", show_alert=True)
            return
        
        # إنشاء سجل للمهمة
        self.db.create_user_task(user_id, task_id)
        
        text = f"""
📌 <b>{task['title']}</b>
━━━━━━━━━━━━━━━━━━
📝 <b>الوصف:</b>
{task['description']}

🎁 <b>المكافأة:</b>
"""
        if task['reward_points'] > 0:
            text += f"⭐ {task['reward_points']} نقطة\n"
        if task['reward_ton'] > 0:
            text += f"💰 {task['reward_ton']:.4f} تون\n"

        text += f"""
━━━━━━━━━━━━━━━━━━
📌 <b>للحصول على المكافأة:</b>
1️⃣ اضغط على زر "اشتراك" أدناه
2️⃣ انضم إلى القناة/المجموعة
3️⃣ اضغط على زر "تحقق من الاشتراك"
4️⃣ احصل على المكافأة فوراً!
━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 اشتراك", url=task['channel_link'])],
            [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data=f"task_{task_id}_verify")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="tasks_menu")]
        ]
        
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def verify_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التحقق من اشتراك المستخدم في القناة"""
        query = update.callback_query
        user_id = update.effective_user.id
        task_id = int(query.data.split('_')[1])
        
        await query.answer("🔍 جاري التحقق من اشتراكك...")
        
        # جلب بيانات المهمة
        task = self.db.get_task(task_id)
        if not task:
            await query.edit_message_text("❌ المهمة غير موجودة")
            return
        
        # جلب سجل المهمة للمستخدم
        user_task = self.db.get_user_task(user_id, task_id)
        if not user_task:
            await query.edit_message_text("❌ يرجى بدء المهمة أولاً")
            return
        
        if user_task['status'] == 'completed':
            await query.answer("✅ لقد حصلت على المكافأة بالفعل!", show_alert=True)
            return
        
        # التحقق من اشتراك المستخدم في القناة
        is_member = await self.check_user_member(update, context, task['channel_username'], user_id)
        
        if is_member:
            # منح المكافأة
            reward_points = task['reward_points']
            reward_ton = task['reward_ton']
            
            if reward_points > 0:
                self.db.update_user_balance(user_id, points_amount=reward_points, update_earned=True)
            if reward_ton > 0:
                self.db.update_user_balance(user_id, ton_amount=reward_ton, update_earned=True)
            
            # تحديث حالة المهمة
            self.db.complete_user_task(user_id, task_id)
            
            # جلب الرصيد الجديد
            user_data = self.db.get_user(user_id)
            
            reward_text = ""
            if reward_points > 0:
                reward_text += f"⭐ {reward_points} نقطة"
            if reward_ton > 0:
                if reward_text:
                    reward_text += " + "
                reward_text += f"💰 {reward_ton:.4f} تون"
            
            text = f"""
✅ <b>مبروك! تم التحقق من اشتراكك!</b>
━━━━━━━━━━━━━━━━━━
🎁 <b>لقد حصلت على:</b>
{reward_text}

💰 <b>رصيدك الحالي:</b>
• تون: <code>{user_data['balance_ton']:.4f}</code>
• نقاط: <code>{user_data['balance_points']:.0f}</code>
━━━━━━━━━━━━━━━━━━
📋 يمكنك العودة لإكمال المهام الأخرى!
"""
            
            keyboard = [
                [InlineKeyboardButton("📋 المهام", callback_data="tasks_menu")],
                [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main")]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
            
            # إشعار للمستخدم
            await query.answer(f"🎉 مبروك! حصلت على {reward_text}!", show_alert=True)
            
        else:
            text = f"""
❌ <b>لم يتم التحقق من اشتراكك!</b>
━━━━━━━━━━━━━━━━━━
⚠️ يبدو أنك لم تشترك في القناة/المجموعة بعد.

📌 <b>الرجاء اتباع الخطوات التالية:</b>
1️⃣ اضغط على زر "اشتراك"
2️⃣ انضم إلى القناة/المجموعة
3️⃣ عد واضغط على "تحقق من الاشتراك" مرة أخرى

🔗 <b>رابط الاشتراك:</b>
{task['channel_link']}
━━━━━━━━━━━━━━━━━━
"""
            
            keyboard = [
                [InlineKeyboardButton("🔗 اشتراك", url=task['channel_link'])],
                [InlineKeyboardButton("🔄 إعادة التحقق", callback_data=f"task_{task_id}_verify")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="tasks_menu")]
            ]
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
    
    async def check_user_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_username, user_id):
        """التحقق من عضوية المستخدم في القناة"""
        try:
            # تنظيف معرف القناة
            if channel_username:
                if channel_username.startswith('@'):
                    chat_id = channel_username
                else:
                    chat_id = f"@{channel_username}"
            else:
                return False
            
            # محاولة الحصول على معلومات العضو
            chat_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            
            # التحقق من حالة العضوية
            if chat_member.status in ['member', 'administrator', 'creator']:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            # إذا كان البوت ليس أدمن في القناة، لا يمكنه التحقق
            return False
    
    async def open_webapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح صفحة المهام في WebApp"""
        user = update.effective_user
        user_id = user.id
        
        keyboard = [[
            InlineKeyboardButton(
                "📋 فتح صفحة المهام",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/tasks.html?user_id={user_id}")
            )
        ]]
        
        await update.callback_query.edit_message_text(
            "📋 اضغط على الزر أدناه لفتح صفحة المهام:\n\n"
            "🎯 أكمل المهام واحصل على مكافآت فورية!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )