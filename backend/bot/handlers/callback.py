# backend/bot/handlers/callback.py
"""
معالج الأزرار (Callback Queries) - نسخة كاملة
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from backend.config import WEBAPP_URL


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار الموحد"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # قائمة الأزرار
    if data == 'back_to_main':
        from backend.bot.handlers.start import show_main_menu
        await show_main_menu(update, context)
    
    elif data == 'balance_menu':
        await query.edit_message_text(
            "💰 <b>رصيدك الحالي</b>\n━━━━━━━━━━━━━━━━━━\n"
            "يمكنك عرض رصيدك من التطبيق الرئيسي.\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لعرض التفاصيل الكاملة.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'referral_menu':
        await query.edit_message_text(
            "🔗 <b>نظام الإحالات</b>\n━━━━━━━━━━━━━━━━━━\n"
            "📍 رابط الإحالة الخاص بك:\n"
            "سيظهر بعد فتح التطبيق\n\n"
            "🎁 مكافأة كل إحالة: 100 نقطة + 0.01 تون\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لعرض رابط الإحالة وإحصائياتك.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/referral.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'giftcode_menu':
        await query.edit_message_text(
            "🎁 <b>الأكواد الترويجية</b>\n━━━━━━━━━━━━━━━━━━\n"
            "✨ أدخل الكود الترويجي لتحصل على مكافآت فورية!\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لإدخال الكود.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/giftcode.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'withdraw_menu':
        await query.edit_message_text(
            "💸 <b>نظام السحب</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>الحد الأدنى للسحب:</b> 0.02 تون\n"
            f"💱 <b>سعر الصرف:</b> 10 نقاط = 1 تون\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لطلب السحب.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/withdraw.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'tasks_menu':
        await query.edit_message_text(
            "📋 <b>المهام المتاحة</b>\n━━━━━━━━━━━━━━━━━━\n"
            "✨ أكمل المهام التالية واحصل على مكافآت:\n"
            "• الاشتراك في القنوات\n"
            "• متابعة المجموعات\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لعرض جميع المهام.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/tasks.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'wheel_menu':
        await query.edit_message_text(
            "🎡 <b>عجلة الحظ</b>\n━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>الجوائز المتاحة:</b>\n"
            "5, 10, 15, 20, 25, 50, 75, 100 نقطة\n\n"
            "🎯 <b>المحاولات اليومية:</b> 3 مرات\n\n"
            "📱 اضغط على زر 'فتح التطبيق' للعب.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/wheel.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'ads_menu':
        await query.edit_message_text(
            "📺 <b>الإعلانات</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>المكافأة:</b> 15 نقطة لكل إعلان\n"
            f"📊 <b>الحد اليومي:</b> 10 إعلانات\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لمشاهدة الإعلانات.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/ads.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'ads_posting_menu':
        await query.edit_message_text(
            "📢 <b>الإعلانات المدفوعة</b>\n━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>الباقات المتاحة:</b>\n"
            "• 25 مشاهدة = 0.0375 تون\n"
            "• 50 مشاهدة = 0.075 تون\n"
            "• 100 مشاهدة = 0.15 تون\n"
            "• 500 مشاهدة = 0.75 تون\n"
            "• 1000 مشاهدة = 1.5 تون\n\n"
            "📱 اضغط على زر 'فتح التطبيق' لإنشاء إعلان مدفوع.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 فتح التطبيق", web_app=WebAppInfo(url=f"{WEBAPP_URL}/ads_posting.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    elif data == 'admin_panel':
        await query.edit_message_text(
            "👑 <b>لوحة التحكم - المشرف</b>\n━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>الإحصائيات:</b>\n"
            "• إجمالي المستخدمين: جاري التحميل...\n"
            "• طلبات السحب المعلقة: جاري التحميل...\n\n"
            "📱 اضغط على زر 'فتح لوحة التحكم' للإدارة.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👑 فتح لوحة التحكم", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin.html")),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_to_main')
            ]]),
            parse_mode='HTML'
        )
    
    else:
        await query.edit_message_text(
            "❓ إجراء غير معروف\n\n"
            "الرجاء استخدام الأزرار المتاحة في القائمة الرئيسية.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='back_to_main')
            ]])
        )