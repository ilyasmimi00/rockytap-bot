# handlers/ads_posting.py
"""
معالج الإعلانات المدفوعة - نسخة كاملة مصححة
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import re

logger = logging.getLogger(__name__)


class AdsPostingHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def extract_channel_username(self, channel_link):
        """استخراج معرف القناة من الرابط بشكل صحيح"""
        if not channel_link:
            return None
        
        channel_link = channel_link.strip()
        
        # حالة الروابط المباشرة @username
        if channel_link.startswith('@'):
            return channel_link
        
        # حالة t.me/username
        if 't.me/' in channel_link:
            parts = channel_link.split('t.me/')
            username = parts[-1].split('?')[0].split('/')[0]
            if username and not username.startswith('+') and not username.startswith('joinchat'):
                return '@' + username
        
        # حالة الروابط الطويلة (غير مدعومة للتحقق الآلي)
        return None
    
    async def show_ads_posting_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإعلانات المدفوعة"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        packages = self.db.get_ad_packages()
        user_data = self.db.get_user(user_id)
        
        text = f"""
📢 <b>الإعلانات المدفوعة</b>
━━━━━━━━━━━━━━━━━━
💰 <b>رصيدك:</b> {user_data['balance_ton']:.4f} تون

📊 <b>أسعار الباقات:</b>
• 1000 مشاهدة = 1.5 تون
━━━━━━━━━━━━━━━━━━
🎯 <b>اختر الباقة المناسبة:</b>
        """
        
        keyboard = []
        row = []
        for pkg in packages:
            row.append(InlineKeyboardButton(
                f"📺 {pkg['views']} مشاهدة | {pkg['price']:.4f} تون",
                callback_data=f"buy_ad_package_{pkg['id']}"
            ))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("📋 إعلاناتي", callback_data='my_ads')])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')])
        
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    
    async def buy_ad_package(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شراء باقة إعلانات"""
        query = update.callback_query
        user_id = update.effective_user.id
        package_id = int(query.data.split('_')[3])
        
        packages = self.db.get_ad_packages()
        package = next((p for p in packages if p['id'] == package_id), None)
        
        if not package:
            await query.answer("❌ الباقة غير موجودة", show_alert=True)
            return
        
        user_data = self.db.get_user(user_id)
        
        if user_data['balance_ton'] < package['price']:
            await query.answer(f"❌ رصيدك غير كافٍ! تحتاج {package['price']:.4f} تون", show_alert=True)
            return
        
        context.user_data['buying_ad'] = {
            'package_id': package_id,
            'views': package['views'],
            'price': package['price']
        }
        context.user_data['awaiting_ad_details'] = True
        
        text = f"""
📝 <b>إنشاء إعلان جديد</b>
━━━━━━━━━━━━━━━━━━
🎯 <b>الباقة:</b> {package['views']} مشاهدة
💰 <b>السعر:</b> {package['price']:.4f} تون
━━━━━━━━━━━━━━━━━━
📌 <b>الرجاء إرسال المعلومات التالية:</b>

1️⃣ <b>عنوان الإعلان</b> (مطلوب)
2️⃣ <b>وصف الإعلان</b> (اختياري)
3️⃣ <b>رابط قناتك</b> (مثال: https://t.me/your_channel)

⚠️ <b>ملاحظة مهمة:</b>
يجب أن يكون البوت @{context.bot.username} أدمن في قناتك للتحقق من الإعلان!

❌ للإلغاء أرسل /cancel
        """
        
        await query.edit_message_text(text, parse_mode='HTML')
    
    async def handle_ad_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة تفاصيل الإعلان"""
        if not context.user_data.get('awaiting_ad_details'):
            return False
        
        message = update.message
        user_id = update.effective_user.id
        text = message.text.strip()
        
        if text == '/cancel':
            context.user_data['awaiting_ad_details'] = False
            context.user_data.pop('buying_ad', None)
            await message.reply_text("❌ تم إلغاء إنشاء الإعلان")
            return True
        
        lines = text.split('\n')
        
        if len(lines) < 2:
            await message.reply_text(
                "❌ يرجى إرسال المعلومات بالشكل الصحيح:\n"
                "السطر الأول: عنوان الإعلان\n"
                "السطر الثاني: وصف الإعلان (اختياري)\n"
                "السطر الثالث: رابط القناة\n\n"
                "أو أرسل /cancel للإلغاء"
            )
            return True
        
        title = lines[0].strip()
        description = lines[1].strip() if len(lines) > 1 else ""
        channel_link = lines[2].strip() if len(lines) > 2 else ""
        
        if not title or not channel_link:
            await message.reply_text("❌ عنوان الإعلان ورابط القناة مطلوبان")
            return True
        
        # استخراج معرف القناة
        channel_username = self.extract_channel_username(channel_link)
        
        if not channel_username:
            await message.reply_text(
                "⚠️ لم نتمكن من استخراج معرف القناة من الرابط.\n"
                "يرجى التأكد من الرابط والتنسيق الصحيح.\n"
                "مثال: https://t.me/username"
            )
            return True
        
        buying_data = context.user_data.get('buying_ad')
        if not buying_data:
            await message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى")
            context.user_data['awaiting_ad_details'] = False
            return True
        
        success, result = self.db.create_user_ad(
            user_id=user_id,
            title=title,
            description=description,
            channel_link=channel_link,
            channel_username=channel_username,
            channel_id=None,
            package_id=buying_data['package_id']
        )
        
        if success:
            ad_id = result
            
            text = f"""
✅ <b>تم إنشاء الإعلان بنجاح!</b>
━━━━━━━━━━━━━━━━━━
📋 <b>عنوان الإعلان:</b> {title}
👁️ <b>المشاهدات المطلوبة:</b> {buying_data['views']}
💰 <b>المبلغ المدفوع:</b> {buying_data['price']:.4f} تون
━━━━━━━━━━━━━━━━━━
⚠️ <b>الخطوة التالية:</b>
1️⃣ أضف البوت @{context.bot.username} أدمن في قناتك
2️⃣ اضغط على زر "تحقق" أدناه
3️⃣ بعد التحقق، سيبدأ عرض الإعلان تلقائياً
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ تحقق من البوت في قناتي", callback_data=f"ad_verify_{ad_id}")],
                [InlineKeyboardButton("📋 إعلاناتي", callback_data='my_ads')],
                [InlineKeyboardButton("🔙 رجوع", callback_data='ads_posting_menu')]
            ]
            
            await message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
        else:
            await message.reply_text(f"❌ حدث خطأ: {result}")
        
        context.user_data['awaiting_ad_details'] = False
        context.user_data.pop('buying_ad', None)
        return True
    
    async def verify_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التحقق من أن البوت أدمن في قناة المستخدم"""
        query = update.callback_query
        user_id = update.effective_user.id
        ad_id = int(query.data.split('_')[2])
        
        await query.answer("🔍 جاري التحقق من صلاحيات البوت في قناتك...")
        
        ad = self.db.get_ad_by_id(ad_id, user_id)
        if not ad:
            await query.edit_message_text("❌ الإعلان غير موجود")
            return
        
        if ad['is_verified']:
            await query.answer("✅ البوت تم التحقق منه بالفعل!", show_alert=True)
            return
        
        # الحصول على معرف البوت بشكل صحيح
        bot_user = await context.bot.get_me()
        bot_username = bot_user.username
        
        try:
            chat_id = ad['channel_username'] or ad['channel_link']
            if chat_id and not chat_id.startswith('@'):
                chat_id = '@' + chat_id
            
            chat_member = await context.bot.get_chat_member(
                chat_id=chat_id,
                user_id=bot_user.id
            )
            
            if chat_member.status in ['administrator', 'creator']:
                self.db.verify_channel_bot(user_id, ad_id, bot_username)
                
                text = f"""
✅ <b>تم التحقق بنجاح!</b>
━━━━━━━━━━━━━━━━━━
📢 الإعلان "{ad['title']}" أصبح نشطاً الآن!
👁️ المشاهدات المطلوبة: {ad['views_count']}
💰 تم خصم {ad['paid_amount']:.4f} تون من رصيدك

📌 سيتم عرض الإعلان للمستخدمين الذين يشاهدون الإعلانات.
عند اكتمال العدد، سيتم إشعارك تلقائياً.
                """
                
                keyboard = [
                    [InlineKeyboardButton("📊 إحصائيات الإعلان", callback_data=f"ad_manage_{ad_id}")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data='my_ads')]
                ]
                
                await query.edit_message_text(
                    text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    f"❌ لم يتم التحقق!\n\n"
                    f"الرجاء إضافة البوت @{bot_username} كـ <b>أدمن</b> في قناتك {ad['channel_username']}\n\n"
                    f"ثم اضغط على زر التحقق مرة أخرى.",
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Error verifying channel: {e}")
            await query.edit_message_text(
                f"❌ لم يتم التحقق!\n\n"
                f"تأكد من:\n"
                f"1️⃣ إضافة البوت @{bot_username} إلى قناتك\n"
                f"2️⃣ جعل البوت <b>أدمن</b> في القناة\n"
                f"3️⃣ الرابط صحيح: {ad['channel_link']}\n\n"
                f"ثم اضغط على زر التحقق مرة أخرى.\n\n"
                f"📌 خطأ تقني: {str(e)[:100]}",
                parse_mode='HTML'
            )
    
    async def my_ads(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعلانات المستخدم"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        user_ads = self.db.get_user_ads(user_id)
        
        if not user_ads:
            text = "📋 <b>لا توجد إعلانات</b>\n\nيمكنك شراء إعلان جديد من القائمة الرئيسية."
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='ads_posting_menu')]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            return
        
        text = "📋 <b>إعلاناتي</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        
        for ad in user_ads:
            status_emoji = {
                'pending': '⏳',
                'active': '🟢',
                'completed': '✅',
                'rejected': '❌'
            }.get(ad['status'], '❓')
            
            verified_emoji = '🔒' if ad['is_verified'] else '⚠️'
            
            text += f"{status_emoji} <b>{ad['title']}</b>\n"
            text += f"   {verified_emoji} {ad['channel_username'] or ad['channel_link']}\n"
            text += f"   👁️ {ad['current_views']}/{ad['views_count']} مشاهدة\n"
            text += f"   📅 {ad['created_at']}\n"
            text += f"   💰 {ad['paid_amount']:.4f} تون\n"
            text += "━━━━━━━━━━━━━━━━━━\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ إعلان جديد", callback_data='ads_posting_menu')],
            [InlineKeyboardButton("🔄 تحديث", callback_data='my_ads')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    
    async def my_ads_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإعلانات مع أزرار الإدارة"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        user_ads = self.db.get_user_ads(user_id)
        
        if not user_ads:
            await query.answer("لا توجد إعلانات", show_alert=True)
            return
        
        text = "📋 <b>اختر إعلاناً لإدارته</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        keyboard = []
        
        for ad in user_ads:
            status_emoji = '🟢' if ad['status'] == 'active' else '⏳' if ad['status'] == 'pending' else '✅'
            keyboard.append([InlineKeyboardButton(
                f"{status_emoji} {ad['title']} ({ad['current_views']}/{ad['views_count']})",
                callback_data=f"ad_manage_{ad['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='my_ads')])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    
    async def manage_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة إعلان محدد"""
        query = update.callback_query
        user_id = update.effective_user.id
        ad_id = int(query.data.split('_')[2])
        
        ad = self.db.get_ad_by_id(ad_id, user_id)
        if not ad:
            await query.answer("الإعلان غير موجود", show_alert=True)
            return
        
        stats = self.db.get_ad_stats(ad_id)
        members = self.db.get_ad_members(ad_id, limit=10)
        
        progress = stats['progress'] if stats else 0
        
        text = f"""
📊 <b>إدارة الإعلان</b>
━━━━━━━━━━━━━━━━━━
📢 <b>{ad['title']}</b>
📝 {ad['description'] or 'لا يوجد وصف'}

━━━━━━━━━━━━━━━━━━
📈 <b>الإحصائيات:</b>
• 👁️ المشاهدات: {ad['current_views']}/{ad['views_count']} ({progress:.1f}%)
• 👥 الأعضاء: {ad['members_count']}
• 📅 تاريخ الإنشاء: {ad['created_at']}
• 💰 المبلغ المدفوع: {ad['paid_amount']:.4f} TON
━━━━━━━━━━━━━━━━━━
        """
        
        if members:
            text += "\n👥 <b>آخر الأعضاء:</b>\n"
            for m in members[:5]:
                text += f"   • {m['username'] or m['member_id']} | {m['watched_at']}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data=f"ad_refresh_{ad_id}")],
            [InlineKeyboardButton("🗑️ حذف الإعلان", callback_data=f"ad_delete_{ad_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data='my_ads_list')]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    
    async def refresh_ad_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحديث إحصائيات الإعلان"""
        await self.manage_ad(update, context)
    
    async def delete_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حذف الإعلان"""
        query = update.callback_query
        user_id = update.effective_user.id
        ad_id = int(query.data.split('_')[2])
        
        ad = self.db.get_ad_by_id(ad_id, user_id)
        if not ad:
            await query.answer("الإعلان غير موجود", show_alert=True)
            return
        
        success, msg = self.db.delete_ad(ad_id, user_id)
        
        if success:
            await query.answer("✅ تم حذف الإعلان", show_alert=True)
            await self.my_ads_list(update, context)
        else:
            await query.answer(f"❌ {msg}", show_alert=True)
    
    async def ad_members_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة أعضاء الإعلان"""
        query = update.callback_query
        user_id = update.effective_user.id
        ad_id = int(query.data.split('_')[2])
        
        ad = self.db.get_ad_by_id(ad_id, user_id)
        if not ad:
            await query.answer("الإعلان غير موجود", show_alert=True)
            return
        
        members = self.db.get_ad_members(ad_id, limit=50)
        
        if not members:
            text = "👥 <b>لا يوجد أعضاء شاهدوا هذا الإعلان بعد</b>"
        else:
            text = f"👥 <b>أعضاء شاهدوا إعلان '{ad['title']}'</b>\n━━━━━━━━━━━━━━━━━━\n\n"
            for m in members:
                text += f"• {m['username'] or m['member_id']}\n"
                text += f"  📅 {m['watched_at']} | ⭐ {m['reward_points']} نقطة\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data=f"ad_members_{ad_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"ad_manage_{ad_id}")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')